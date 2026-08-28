import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from flask import Flask
from flask_login import LoginManager

from Football_Project.challenges import challenges_bp
from Football_Project.extensions import db
from Football_Project.models import (
    Challenge,
    ChallengeGame,
    ChallengeParticipant,
    Game,
    GroupMember,
    PoolGroup,
    Settings,
    User,
)
from Football_Project.services.challenge_creation_service import (
    ChallengeValidationError,
    create_challenge,
)


class ChallengeCreationTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(
            "Football_Project",
            template_folder="templates",
            static_folder="static",
        )
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="challenge-test-only",
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            WTF_CSRF_ENABLED=False,
        )
        db.init_app(self.app)

        login_manager = LoginManager()
        login_manager.init_app(self.app)

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        # The create template extends base.html, whose navigation references these
        # existing blueprints. Registering them does not start the application.
        from Football_Project.admin import admin_bp
        from Football_Project.auth import auth_bp
        from Football_Project.routes import main_bp

        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(challenges_bp)
        self.app.jinja_env.filters["fmt_mt"] = lambda value: str(value)
        self.app.jinja_env.globals["csrf_token"] = lambda: "test-csrf-disabled"

        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        self.now = datetime.now(timezone.utc)
        self.creator = self._user("creator")
        self.member = self._user("member")
        self.inactive_member_user = self._user("inactive-member")
        self.outsider = self._user("outsider")
        self.group = PoolGroup(name="Primary Group", slug="primary", is_active=True)
        self.other_group = PoolGroup(name="Other Group", slug="other", is_active=True)
        db.session.add_all([self.group, self.other_group])
        db.session.flush()
        self._membership(self.creator, self.group)
        self._membership(self.member, self.group)
        self._membership(self.inactive_member_user, self.group, active=False)
        self._membership(self.outsider, self.other_group)
        db.session.add(Settings(current_week=1, season_year=2026, season_type="REG"))
        self.early_game = self._game(
            "early",
            kickoff=self.now + timedelta(hours=2),
        )
        self.late_game = self._game(
            "late",
            kickoff=self.now + timedelta(hours=4),
        )
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.context.pop()

    def _user(self, username, *, active=True):
        user = User(
            username=username,
            password="test-only",
            is_active=active,
        )
        db.session.add(user)
        db.session.flush()
        return user

    def _membership(self, user, group, *, active=True):
        membership = GroupMember(
            user_id=user.id,
            group_id=group.id,
            role="member",
            is_active=active,
        )
        db.session.add(membership)
        return membership

    def _game(
        self,
        natural_id,
        *,
        kickoff,
        week=1,
        season_year=2026,
        season_type="REG",
    ):
        if kickoff is not None and kickoff.tzinfo is not None:
            # SQLite drops timezone offsets. Persist the same representation the
            # domain helper intentionally treats as legacy Mountain time.
            kickoff = kickoff.astimezone(ZoneInfo("America/Denver")).replace(
                tzinfo=None
            )
        game = Game(
            game_id=natural_id,
            season_year=season_year,
            season_type=season_type,
            week=week,
            home_team=f"Home {natural_id}",
            away_team=f"Away {natural_id}",
            commence_time_mt=kickoff,
            status="STATUS_SCHEDULED",
        )
        db.session.add(game)
        db.session.flush()
        return game

    def _login(self, user):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(user.id)
            session["_fresh"] = True

    def _create(self, **overrides):
        values = {
            "group_id": self.group.id,
            "creator_user_id": self.creator.id,
            "name": "Sunday Showdown",
            "description": "Test challenge",
            "selected_participant_ids": [self.member.id],
            "selected_game_ids": [self.early_game.id],
            "now_utc": self.now,
        }
        values.update(overrides)
        return create_challenge(**values)

    def assert_validation_error(self, message, **overrides):
        with self.assertRaisesRegex(ChallengeValidationError, message):
            self._create(**overrides)

    def test_active_member_can_open_create_form(self):
        self._login(self.creator)
        response = self.client.get(
            f"/groups/{self.group.id}/challenges/new"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create Challenge", response.data)
        self.assertIn(b"Primary Group", response.data)
        self.assertIn(b"included automatically", response.data)

    def test_non_member_cannot_open_create_form(self):
        self._login(self.outsider)
        response = self.client.get(
            f"/groups/{self.group.id}/challenges/new"
        )
        self.assertEqual(response.status_code, 403)

    def test_global_admin_without_membership_cannot_open_create_form(self):
        self.outsider.is_admin = True
        db.session.commit()
        self._login(self.outsider)
        response = self.client.get(
            f"/groups/{self.group.id}/challenges/new"
        )
        self.assertEqual(response.status_code, 403)

    def test_post_create_redirects_to_challenges_panel(self):
        self._login(self.creator)
        response = self.client.post(
            f"/groups/{self.group.id}/challenges",
            data={
                "name": "Route Challenge",
                "participant_ids": [str(self.member.id)],
                "game_ids": [str(self.early_game.id)],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/groups?section=challenges"))
        self.assertEqual(Challenge.query.count(), 1)

    def test_post_validation_error_redisplays_form_without_partial_rows(self):
        self._login(self.creator)
        response = self.client.post(
            f"/groups/{self.group.id}/challenges",
            data={
                "name": "Route Challenge",
                "participant_ids": [str(self.member.id)],
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Select at least one game.", response.data)
        self.assertEqual(Challenge.query.count(), 0)
        self.assertEqual(ChallengeParticipant.query.count(), 0)
        self.assertEqual(ChallengeGame.query.count(), 0)

    def test_inactive_member_cannot_create(self):
        self.assert_validation_error(
            "active member",
            creator_user_id=self.inactive_member_user.id,
        )

    def test_creator_is_automatically_included_exactly_once(self):
        challenge = self._create(
            selected_participant_ids=[
                self.creator.id,
                self.member.id,
                self.creator.id,
            ]
        )
        participant_ids = [row.user_id for row in challenge.participants]
        self.assertCountEqual(participant_ids, [self.creator.id, self.member.id])
        self.assertEqual(len(participant_ids), 2)

    def test_minimum_two_participants_is_enforced(self):
        self.assert_validation_error(
            "additional group member",
            selected_participant_ids=[self.creator.id, self.creator.id],
        )

    def test_participant_from_another_group_is_rejected(self):
        self.assert_validation_error(
            "active member of this group",
            selected_participant_ids=[self.outsider.id],
        )

    def test_inactive_participant_is_rejected(self):
        self.assert_validation_error(
            "active member of this group",
            selected_participant_ids=[self.inactive_member_user.id],
        )

    def test_at_least_one_game_is_required(self):
        self.assert_validation_error(
            "at least one game",
            selected_game_ids=[],
        )

    def test_game_from_another_week_is_rejected(self):
        other_week = self._game(
            "week-two",
            kickoff=self.now + timedelta(days=7),
            week=2,
        )
        db.session.commit()
        self.assert_validation_error(
            "current NFL week",
            selected_game_ids=[other_week.id],
        )

    def test_game_from_another_season_is_rejected(self):
        other_season = self._game(
            "other-season",
            kickoff=self.now + timedelta(hours=3),
            season_year=2025,
        )
        db.session.commit()
        self.assert_validation_error(
            "current NFL week",
            selected_game_ids=[other_season.id],
        )

    def test_game_from_another_season_type_is_rejected(self):
        postseason = self._game(
            "postseason",
            kickoff=self.now + timedelta(hours=3),
            season_type="POST",
        )
        db.session.commit()
        self.assert_validation_error(
            "current NFL week",
            selected_game_ids=[postseason.id],
        )

    def test_game_with_missing_kickoff_is_rejected(self):
        missing = self._game("missing-kickoff", kickoff=None)
        db.session.commit()
        self.assert_validation_error(
            "scheduled kickoff",
            selected_game_ids=[missing.id],
        )

    def test_already_started_game_is_rejected(self):
        started = self._game(
            "started",
            kickoff=self.now - timedelta(hours=1),
        )
        db.session.commit()
        self.assert_validation_error(
            "already started",
            selected_game_ids=[started.id],
        )

    def test_duplicate_participant_ids_are_normalized(self):
        challenge = self._create(
            selected_participant_ids=[self.member.id, self.member.id]
        )
        self.assertEqual(len(challenge.participants), 2)

    def test_duplicate_game_ids_are_normalized(self):
        challenge = self._create(
            selected_game_ids=[self.early_game.id, self.early_game.id]
        )
        self.assertEqual(len(challenge.challenge_games), 1)

    def test_display_order_follows_kickoff_order(self):
        challenge = self._create(
            selected_game_ids=[self.late_game.id, self.early_game.id]
        )
        rows = sorted(challenge.challenge_games, key=lambda row: row.display_order)
        self.assertEqual(
            [(row.game_id, row.display_order) for row in rows],
            [(self.early_game.id, 1), (self.late_game.id, 2)],
        )

    def test_successful_creation_inserts_expected_rows(self):
        challenge = self._create(
            selected_game_ids=[self.early_game.id, self.late_game.id]
        )
        self.assertEqual(Challenge.query.count(), 1)
        self.assertEqual(challenge.name, "Sunday Showdown")
        self.assertEqual(challenge.description, "Test challenge")
        self.assertEqual(challenge.group_id, self.group.id)
        self.assertEqual(challenge.creator_user_id, self.creator.id)
        self.assertEqual(ChallengeParticipant.query.count(), 2)
        self.assertEqual(ChallengeGame.query.count(), 2)

    def test_validation_failure_leaves_no_partial_rows(self):
        self.assert_validation_error(
            "do not exist",
            selected_game_ids=[self.early_game.id, 999999],
        )
        self.assertEqual(Challenge.query.count(), 0)
        self.assertEqual(ChallengeParticipant.query.count(), 0)
        self.assertEqual(ChallengeGame.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
