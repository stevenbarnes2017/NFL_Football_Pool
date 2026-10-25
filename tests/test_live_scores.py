import unittest

from Football_Project.utils import parse_game_summary, parse_scoreboard_event


def competitor(side, abbr, name, score, team_id, record="4-2", winner=False):
    return {
        "homeAway": side,
        "score": score,
        "winner": winner,
        "records": [{"summary": record}],
        "team": {"id": team_id, "abbreviation": abbr, "displayName": name},
    }


def scoreboard_event(state="in", competitors=None, situation=None):
    return {
        "id": "401",
        "date": "2026-10-25T17:00Z",
        "status": {
            "displayClock": "5:32",
            "period": 2,
            "type": {"state": state, "description": "In Progress", "shortDetail": "2nd - 5:32"},
        },
        "competitions": [{
            "competitors": competitors if competitors is not None else [
                competitor("home", "CHI", "Chicago Bears", "17", "3"),
                competitor("away", "NE", "New England Patriots", "10", "17"),
            ],
            "situation": situation if situation is not None else {
                "down": 3, "distance": 7, "yardLine": 35, "possession": "17",
                "downDistanceText": "3rd & 7 at CHI 35", "isRedZone": False,
            },
            "broadcasts": [{"names": ["CBS"]}, {"names": ["Paramount+"]}, {"names": ["NFL+"]}],
        }],
    }


class ParseScoreboardEventTests(unittest.TestCase):
    def test_keeps_legacy_fields(self):
        g = parse_scoreboard_event(scoreboard_event())
        self.assertEqual(g["game_id"], "401")
        self.assertEqual(g["home_team"], "Chicago Bears")
        self.assertEqual(g["away_team"], "New England Patriots")
        self.assertEqual((g["home_score"], g["away_score"]), ("17", "10"))
        self.assertEqual(g["status"], "In Progress")
        self.assertEqual((g["clock"], g["period"]), ("5:32", 2))
        self.assertEqual((g["down"], g["distance"], g["yardLine"]), (3, 7, 35))

    def test_display_fields(self):
        g = parse_scoreboard_event(scoreboard_event())
        self.assertEqual(g["state"], "in")
        self.assertEqual(g["detail"], "2nd - 5:32")
        self.assertEqual(g["kickoff"], "2026-10-25T17:00Z")
        self.assertEqual((g["home_abbr"], g["away_abbr"]), ("CHI", "NE"))
        self.assertEqual(g["home_record"], "4-2")
        self.assertEqual(g["broadcast"], "CBS, Paramount+")
        self.assertEqual(g["down_distance"], "3rd & 7 at CHI 35")
        self.assertFalse(g["red_zone"])

    def test_possession_maps_team_id_to_name(self):
        g = parse_scoreboard_event(scoreboard_event())
        self.assertEqual(g["possession"], "New England Patriots")

    def test_uses_home_away_flag_not_list_order(self):
        event = scoreboard_event(competitors=[
            competitor("away", "NE", "New England Patriots", "10", "17"),
            competitor("home", "CHI", "Chicago Bears", "17", "3"),
        ])
        g = parse_scoreboard_event(event)
        self.assertEqual(g["home_team"], "Chicago Bears")
        self.assertEqual(g["away_score"], "10")

    def test_pregame_without_situation(self):
        event = scoreboard_event(state="pre", situation={})
        event["competitions"][0].pop("broadcasts")
        g = parse_scoreboard_event(event)
        self.assertEqual(g["state"], "pre")
        self.assertIsNone(g["possession"])
        self.assertIsNone(g["down_distance"])
        self.assertIsNone(g["broadcast"])

    def test_skips_events_without_two_teams(self):
        self.assertIsNone(parse_scoreboard_event(scoreboard_event(competitors=[])))


def summary_payload():
    return {
        "header": {"competitions": [{
            "date": "2026-10-23T00:15Z",
            "status": {"type": {"state": "post", "description": "Final", "shortDetail": "Final"}},
            "competitors": [
                {"homeAway": "home", "score": "30", "winner": True,
                 "record": [{"summary": "5-2"}],
                 "linescores": [{"displayValue": v} for v in ("10", "10", "7", "3")],
                 "team": {"id": "3", "abbreviation": "CHI", "displayName": "Chicago Bears"}},
                {"homeAway": "away", "score": "24", "winner": False,
                 "record": [{"summary": "4-3"}],
                 "linescores": [{"displayValue": v} for v in ("0", "14", "7", "3")],
                 "team": {"id": "17", "abbreviation": "NE", "displayName": "New England Patriots"}},
            ],
        }]},
        "boxscore": {
            "teams": [
                {"homeAway": "away", "team": {"id": "17"}, "statistics": [
                    {"name": "totalYards", "displayValue": "380"},
                    {"name": "thirdDownEff", "displayValue": "2-7"},
                    {"name": "somethingUnlisted", "displayValue": "x"},
                ]},
                {"homeAway": "home", "team": {"id": "3"}, "statistics": [
                    {"name": "totalYards", "displayValue": "405"},
                    {"name": "thirdDownEff", "displayValue": "4-12"},
                ]},
            ],
            "players": [
                {"team": {"abbreviation": "CHI", "displayName": "Chicago Bears"}, "statistics": [
                    {"name": "kicking", "labels": ["FG", "PCT"], "athletes": [
                        {"athlete": {"displayName": "Cairo Santos"}, "stats": ["3/3", "100.0"]}]},
                    {"name": "passing", "labels": ["C/ATT", "YDS"], "athletes": [
                        {"athlete": {"displayName": "Caleb Williams"}, "stats": ["22/33", "289"]}]},
                    {"name": "fumbles", "labels": ["FUM"], "athletes": []},
                ]},
                {"team": {"abbreviation": "NE", "displayName": "New England Patriots"}, "statistics": [
                    {"name": "rushing", "labels": ["CAR", "YDS"], "athletes": [
                        {"athlete": {"displayName": "Drake Maye"}, "stats": ["4", "26"]}]},
                ]},
            ],
        },
        "scoringPlays": [{
            "type": {"abbreviation": "FG", "text": "Field Goal Good"},
            "text": "Cairo Santos 43 Yd Field Goal ",
            "awayScore": 0, "homeScore": 3,
            "period": {"number": 1}, "clock": {"displayValue": "9:53"},
            "team": {"abbreviation": "CHI"},
        }],
    }


class ParseGameSummaryTests(unittest.TestCase):
    def test_header(self):
        d = parse_game_summary(summary_payload())
        self.assertEqual((d["away_team"], d["home_team"]), ("New England Patriots", "Chicago Bears"))
        self.assertEqual(d["home"]["abbr"], "CHI")
        self.assertTrue(d["home"]["winner"])
        self.assertEqual(d["away"]["linescores"], ["0", "14", "7", "3"])
        self.assertEqual((d["state"], d["detail"]), ("post", "Final"))

    def test_team_stats_are_labelled_side_by_side(self):
        d = parse_game_summary(summary_payload())
        self.assertEqual(d["team_stats"], [
            {"label": "Total yards", "away": "380", "home": "405"},
            {"label": "3rd down", "away": "2-7", "home": "4-12"},
        ])

    def test_player_stats_grouped_by_category_with_own_columns(self):
        d = parse_game_summary(summary_payload())
        # away team first, matching the scorebug
        self.assertEqual([t["abbr"] for t in d["player_stats"]], ["NE", "CHI"])
        chi = d["player_stats"][1]
        # display order: passing before kicking; empty categories dropped
        self.assertEqual([c["name"] for c in chi["categories"]], ["passing", "kicking"])
        passing = chi["categories"][0]
        self.assertTrue(passing["featured"])
        self.assertEqual(passing["labels"], ["C/ATT", "YDS"])
        self.assertEqual(passing["rows"], [{"name": "Caleb Williams", "stats": ["22/33", "289"]}])
        self.assertFalse(chi["categories"][1]["featured"])

    def test_scoring_plays(self):
        d = parse_game_summary(summary_payload())
        self.assertEqual(d["scoring_plays"], [{
            "quarter": 1, "clock": "9:53", "team": "CHI", "type": "FG",
            "text": "Cairo Santos 43 Yd Field Goal", "away_score": 0, "home_score": 3,
        }])

    def test_pregame_summary_has_no_stats(self):
        payload = summary_payload()
        payload["boxscore"] = {}
        payload["scoringPlays"] = []
        d = parse_game_summary(payload)
        self.assertEqual(d["team_stats"], [])
        self.assertEqual(d["player_stats"], [])

    def test_missing_header_returns_none(self):
        self.assertIsNone(parse_game_summary({}))


if __name__ == "__main__":
    unittest.main()
