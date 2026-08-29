import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import requests
from flask import Flask
from flask_login import LoginManager

from Football_Project.admin import admin_bp
from Football_Project.auth import auth_bp
from Football_Project.routes import main_bp
from Football_Project.utils import (
    build_nfl_playoff_picture,
    get_nfl_playoff_picture,
)


def standings_entry(name, seed, *, clincher="", wins=0, losses=0, diff=0):
    stats = [
        {"name": "playoffSeed", "value": seed},
        {"name": "wins", "value": wins},
        {"name": "losses", "value": losses},
        {"name": "ties", "value": 0},
        {"name": "pointsFor", "value": 100 + diff},
        {"name": "pointsAgainst", "value": 100},
        {"name": "pointDifferential", "value": diff},
        {"name": "streak", "value": 2, "displayValue": "W2"},
    ]
    if clincher:
        stats.append({"name": "clincher", "displayValue": clincher})
    return {
        "team": {
            "displayName": name,
            "abbreviation": name[:3].upper(),
            "logos": [{"href": f"https://example.test/{name}.png"}],
        },
        "stats": stats,
    }


def standings_payload():
    return {
        "children": [
            {
                "name": "American Football Conference",
                "standings": {
                    "entries": [
                        standings_entry("Eighth", 8, wins=5, losses=4),
                        standings_entry("First", 1, clincher="y", wins=8, losses=1, diff=70),
                        standings_entry("Fifth", 5, wins=6, losses=3, diff=20),
                    ]
                },
            },
            {
                "name": "National Football Conference",
                "standings": {"entries": [standings_entry("NFC First", 1)]},
            },
        ]
    }


class PlayoffPictureDataTests(unittest.TestCase):
    def test_teams_are_sorted_by_playoff_seed(self):
        picture = build_nfl_playoff_picture(standings_payload())
        self.assertEqual(
            [team["playoff_seed"] for team in picture["AFC"]["teams"]],
            [1, 5, 8],
        )

    def test_current_field_and_hunt_statuses_are_derived(self):
        teams = {
            team["playoff_seed"]: team
            for team in build_nfl_playoff_picture(standings_payload())["AFC"]["teams"]
        }
        self.assertEqual(teams[1]["picture_status"], "clinched_division")
        self.assertEqual(teams[5]["picture_status"], "wild_card")
        self.assertEqual(teams[8]["picture_status"], "in_hunt")

    def test_legacy_bracket_collections_remain_available(self):
        picture = build_nfl_playoff_picture(standings_payload())
        self.assertIn("clinched", picture["AFC"])
        self.assertIn("in_hunt", picture["AFC"])
        self.assertIn("bubble", picture["AFC"])
        self.assertIn("eliminated", picture["AFC"])

    @patch("Football_Project.utils.requests.get")
    def test_provider_failure_returns_safe_empty_picture(self, get):
        get.side_effect = requests.Timeout("timed out")
        picture = get_nfl_playoff_picture()
        self.assertTrue(picture["metadata"]["error"])
        self.assertEqual(picture["AFC"]["teams"], [])
        self.assertEqual(picture["NFC"]["teams"], [])
        get.assert_called_once_with(
            "https://site.api.espn.com/apis/v2/sports/football/nfl/standings",
            timeout=10,
        )


class PlayoffPicturePageTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(
            "Football_Project",
            template_folder="templates",
            static_folder="static",
        )
        self.app.config.update(TESTING=True, SECRET_KEY="playoff-test-only")
        login_manager = LoginManager(self.app)

        @login_manager.user_loader
        def load_user(_user_id):
            return None
        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(main_bp)
        self.app.jinja_env.filters["fmt_mt"] = lambda value: "Aug 28, 2026 10:00 AM"
        self.client = self.app.test_client()

    def picture(self):
        picture = build_nfl_playoff_picture(standings_payload())
        picture["metadata"]["fetched_at"] = datetime(2026, 8, 28, tzinfo=timezone.utc)
        return picture

    @patch("Football_Project.routes.get_nfl_playoff_picture")
    def test_page_renders_seeded_picture_and_cutoff(self, get_picture):
        get_picture.return_value = self.picture()
        response = self.client.get("/playoff-picture")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"If the season ended today", response.data)
        self.assertIn(b"Playoff cutoff", response.data)
        self.assertIn(b"Division clinched", response.data)
        self.assertIn(b"Wild card", response.data)
        self.assertIn(b"In the hunt", response.data)

    @patch("Football_Project.routes.get_nfl_playoff_picture")
    def test_page_renders_friendly_provider_error(self, get_picture):
        get_picture.return_value = build_nfl_playoff_picture(None, error=True)
        response = self.client.get("/playoff-picture")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Standings are temporarily unavailable", response.data)
        self.assertIn(b"No AFC standings available", response.data)


if __name__ == "__main__":
    unittest.main()
