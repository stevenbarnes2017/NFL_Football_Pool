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
    ChallengePick,
    Game,
    GroupMember,
    Pick,
    PoolGroup,
    Settings,
    User,
    UserScore,
)
from Football_Project.services.challenge_creation_service import (
    ChallengeValidationError,
    create_challenge,
)
from Football_Project.services.challenge_access_service import (
    build_challenge_detail,
    build_challenge_summary,
    get_visible_challenges,
)
from Football_Project.services.challenge_pick_service import (
    ChallengePickAuthorizationError,
    ChallengePickValidationError,
    save_challenge_picks,
)
from Football_Project.services.challenge_cancellation_service import (
    ChallengeCancellationError,
    can_cancel_challenge,
    cancel_challenge,
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

    def test_participant_sees_challenge(self):
        challenge = self._create()
        self.assertIn(
            challenge.id,
            [row.id for row in get_visible_challenges(self.member)],
        )

    def test_creator_sees_challenge(self):
        challenge = self._create()
        self.assertIn(
            challenge.id,
            [row.id for row in get_visible_challenges(self.creator)],
        )

    def test_unrelated_same_group_member_does_not_see_challenge(self):
        unrelated = self._user("same-group-unrelated")
        self._membership(unrelated, self.group)
        db.session.commit()
        self._create()
        self.assertEqual(get_visible_challenges(unrelated), [])

    def test_group_admin_sees_challenge(self):
        group_admin = self._user("group-admin")
        membership = self._membership(group_admin, self.group)
        membership.role = "group_admin"
        db.session.commit()
        challenge = self._create()
        self.assertIn(
            challenge.id,
            [row.id for row in get_visible_challenges(group_admin)],
        )

    def test_global_admin_sees_challenge(self):
        self.outsider.is_admin = True
        db.session.commit()
        challenge = self._create()
        self.assertIn(
            challenge.id,
            [row.id for row in get_visible_challenges(self.outsider)],
        )

    def test_unauthorized_detail_access_is_denied(self):
        unrelated = self._user("detail-outsider")
        self._membership(unrelated, self.group)
        db.session.commit()
        challenge = self._create()
        self._login(unrelated)
        response = self.client.get(f"/challenges/{challenge.id}")
        self.assertEqual(response.status_code, 403)

    def test_participant_can_open_challenge_detail(self):
        challenge = self._create(
            selected_game_ids=[self.early_game.id, self.late_game.id]
        )
        self._login(self.member)
        response = self.client.get(f"/challenges/{challenge.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sunday Showdown", response.data)
        self.assertIn(b"Primary Group", response.data)
        self.assertIn(b"Home early", response.data)
        self.assertIn(b"Home late", response.data)

    def test_challenge_list_shows_participant_and_game_counts(self):
        self._create(selected_game_ids=[self.early_game.id, self.late_game.id])
        self._login(self.creator)
        response = self.client.get("/groups?section=challenges")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"2 participants", response.data)
        self.assertIn(b"2 games", response.data)
        self.assertIn(b"Open Challenge", response.data)

    def test_open_status(self):
        challenge = self._create()
        summary = build_challenge_summary(challenge, now_utc=self.now)
        self.assertEqual(summary["status"], "open")

    def test_in_progress_status(self):
        challenge = self._create()
        self.early_game.commence_time_mt = (
            (self.now - timedelta(minutes=1))
            .astimezone(ZoneInfo("America/Denver"))
            .replace(tzinfo=None)
        )
        self.early_game.status = "STATUS_IN_PROGRESS"
        db.session.commit()
        summary = build_challenge_summary(challenge, now_utc=self.now)
        self.assertEqual(summary["status"], "in_progress")

    def test_completed_status(self):
        challenge = self._create()
        self.early_game.status = "STATUS_FINAL"
        self.early_game.home_team_score = 24
        self.early_game.away_team_score = 17
        db.session.commit()
        summary = build_challenge_summary(challenge, now_utc=self.now)
        self.assertEqual(summary["status"], "completed")

    def test_cancelled_status(self):
        challenge = self._create()
        challenge.cancelled_at = self.now
        db.session.commit()
        summary = build_challenge_summary(challenge, now_utc=self.now)
        self.assertEqual(summary["status"], "cancelled")

    def test_detail_games_are_ordered_by_display_order(self):
        challenge = self._create(
            selected_game_ids=[self.late_game.id, self.early_game.id]
        )
        challenge.challenge_games.reverse()
        detail = build_challenge_detail(challenge, now_utc=self.now)
        self.assertEqual(
            [row["game"].id for row in detail["games"]],
            [self.early_game.id, self.late_game.id],
        )

    def _save_picks(self, challenge, user=None, picks=None, now=None):
        return save_challenge_picks(
            challenge=challenge,
            user_id=(user or self.member).id,
            submitted_picks=picks or [],
            now_utc=now or self.now,
        )

    def _lock_game(self, game, when=None):
        game.commence_time_mt = (
            (when or self.now).astimezone(ZoneInfo("America/Denver")).replace(
                tzinfo=None
            )
        )
        db.session.commit()

    def test_participant_can_submit_home_team_pick_before_kickoff(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        result = self._save_picks(
            challenge, picks=[(row.id, self.early_game.home_team)]
        )
        pick = ChallengePick.query.one()
        self.assertEqual(result["created"], 1)
        self.assertEqual(pick.team_picked, self.early_game.home_team)

    def test_participant_can_submit_away_team_pick(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._save_picks(challenge, picks=[(row.id, self.early_game.away_team)])
        self.assertEqual(ChallengePick.query.one().team_picked, self.early_game.away_team)

    def test_non_participant_cannot_submit(self):
        challenge = self._create()
        with self.assertRaises(ChallengePickAuthorizationError):
            self._save_picks(challenge, user=self.outsider)

    def test_group_admin_non_participant_cannot_submit(self):
        admin = self._user("pick-group-admin")
        membership = self._membership(admin, self.group)
        membership.role = "group_admin"
        db.session.commit()
        challenge = self._create()
        with self.assertRaises(ChallengePickAuthorizationError):
            self._save_picks(challenge, user=admin)

    def test_global_admin_non_participant_cannot_submit(self):
        self.outsider.is_admin = True
        db.session.commit()
        challenge = self._create()
        with self.assertRaises(ChallengePickAuthorizationError):
            self._save_picks(challenge, user=self.outsider)

    def test_participant_removed_from_group_cannot_submit(self):
        challenge = self._create()
        GroupMember.query.filter_by(user_id=self.member.id, group_id=self.group.id).one().is_active = False
        db.session.commit()
        with self.assertRaises(ChallengePickAuthorizationError):
            self._save_picks(challenge)

    def test_invalid_team_is_rejected(self):
        challenge = self._create()
        with self.assertRaises(ChallengePickValidationError):
            self._save_picks(challenge, picks=[(challenge.challenge_games[0].id, "Not A Team")])
        self.assertEqual(ChallengePick.query.count(), 0)

    def test_game_not_in_challenge_is_rejected(self):
        challenge = self._create()
        with self.assertRaises(ChallengePickValidationError):
            self._save_picks(challenge, picks=[(999999, self.late_game.home_team)])

    def test_existing_unlocked_pick_can_be_updated(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._save_picks(challenge, picks=[(row.id, self.early_game.home_team)])
        self._save_picks(challenge, picks=[(row.id, self.early_game.away_team)])
        self.assertEqual(ChallengePick.query.one().team_picked, self.early_game.away_team)

    def test_exactly_at_kickoff_is_locked(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._lock_game(self.early_game, self.now)
        result = self._save_picks(challenge, picks=[(row.id, self.early_game.home_team)])
        self.assertEqual(result["locked"], 1)
        self.assertEqual(ChallengePick.query.count(), 0)

    def test_after_kickoff_is_locked(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._lock_game(self.early_game, self.now - timedelta(seconds=1))
        result = self._save_picks(challenge, picks=[(row.id, self.early_game.home_team)])
        self.assertEqual(result["locked"], 1)
        self.assertEqual(ChallengePick.query.count(), 0)

    def test_locked_existing_pick_is_unchanged(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._save_picks(challenge, picks=[(row.id, self.early_game.home_team)])
        self._lock_game(self.early_game)
        self._save_picks(challenge, picks=[(row.id, self.early_game.away_team)])
        self.assertEqual(ChallengePick.query.one().team_picked, self.early_game.home_team)

    def test_locked_missing_pick_cannot_be_created(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._lock_game(self.early_game)
        self._save_picks(challenge, picks=[(row.id, self.early_game.home_team)])
        self.assertEqual(ChallengePick.query.count(), 0)

    def test_locked_game_is_skipped_while_later_game_is_saved(self):
        challenge = self._create(selected_game_ids=[self.early_game.id, self.late_game.id])
        rows = {row.game_id: row for row in challenge.challenge_games}
        self._lock_game(self.early_game)
        result = self._save_picks(challenge, picks=[
            (rows[self.early_game.id].id, self.early_game.home_team),
            (rows[self.late_game.id].id, self.late_game.away_team),
        ])
        self.assertEqual((result["locked"], result["created"]), (1, 1))
        self.assertEqual(ChallengePick.query.one().challenge_game_id, rows[self.late_game.id].id)

    def test_duplicate_submitted_game_ids_with_same_value_are_normalized(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._save_picks(challenge, picks=[
            (row.id, self.early_game.home_team),
            (row.id, self.early_game.home_team),
        ])
        self.assertEqual(ChallengePick.query.count(), 1)

    def test_conflicting_duplicate_game_ids_leave_no_partial_writes(self):
        challenge = self._create(selected_game_ids=[self.early_game.id, self.late_game.id])
        rows = {row.game_id: row for row in challenge.challenge_games}
        with self.assertRaises(ChallengePickValidationError):
            self._save_picks(challenge, picks=[
                (rows[self.early_game.id].id, self.early_game.home_team),
                (rows[self.late_game.id].id, self.late_game.home_team),
                (rows[self.late_game.id].id, self.late_game.away_team),
            ])
        self.assertEqual(ChallengePick.query.count(), 0)

    def test_current_participant_sees_saved_pick_on_detail(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._save_picks(challenge, picks=[(row.id, self.early_game.home_team)])
        self._login(self.member)
        response = self.client.get(f"/challenges/{challenge.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Save Picks", response.data)
        self.assertIn(b"checked", response.data)

    def test_non_participant_detail_remains_read_only(self):
        admin = self._user("readonly-admin")
        membership = self._membership(admin, self.group)
        membership.role = "group_admin"
        db.session.commit()
        challenge = self._create()
        self._login(admin)
        response = self.client.get(f"/challenges/{challenge.id}")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Save Picks", response.data)
        self.assertNotIn(b'type="radio"', response.data)

    def test_non_participant_pick_route_is_denied(self):
        challenge = self._create()
        self._login(self.outsider)
        response = self.client.post(f"/challenges/{challenge.id}/picks")
        self.assertEqual(response.status_code, 403)

    def _save_for_user(self, challenge, user, selections):
        return self._save_picks(
            challenge,
            user=user,
            picks=[
                (row.id, selections[row.game_id])
                for row in challenge.challenge_games
                if row.game_id in selections
            ],
        )

    def _finalize(self, game, home_score, away_score):
        game.status = "STATUS_FINAL"
        game.home_team_score = home_score
        game.away_team_score = away_score
        db.session.commit()

    def _standing_for(self, detail, user):
        return next(
            row for row in detail["standings"]
            if row["participant"].user_id == user.id
        )

    def _game_detail_for(self, detail, game):
        return next(row for row in detail["games"] if row["game"].id == game.id)

    def test_open_challenge_standings_are_all_zero(self):
        challenge = self._create(selected_game_ids=[self.early_game.id, self.late_game.id])
        detail = build_challenge_detail(challenge, user=self.member, now_utc=self.now)
        self.assertTrue(all(row["correct_count"] == 0 for row in detail["standings"]))
        self.assertTrue(all(row["graded_count"] == 0 for row in detail["standings"]))
        self.assertTrue(all(row["remaining_count"] == 2 for row in detail["standings"]))

    def test_in_progress_standings_are_calculated(self):
        challenge = self._create(selected_game_ids=[self.early_game.id, self.late_game.id])
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        self._lock_game(self.early_game)
        self._finalize(self.early_game, 24, 17)
        detail = build_challenge_detail(challenge, user=self.member, now_utc=self.now)
        standing = self._standing_for(detail, self.member)
        self.assertEqual(detail["status"], "in_progress")
        self.assertEqual((standing["correct_count"], standing["graded_count"], standing["remaining_count"]), (1, 1, 1))

    def test_completed_standings_and_single_winner(self):
        challenge = self._create()
        self._save_for_user(challenge, self.creator, {self.early_game.id: self.early_game.away_team})
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        self._finalize(self.early_game, 21, 14)
        detail = build_challenge_detail(challenge, user=self.member, now_utc=self.now)
        self.assertEqual(detail["status"], "completed")
        self.assertEqual([row.user_id for row in detail["winners"]], [self.member.id])
        self.assertEqual(self._standing_for(detail, self.member)["correct_count"], 1)

    def test_completed_challenge_supports_tied_winners(self):
        challenge = self._create()
        for user in (self.creator, self.member):
            self._save_for_user(challenge, user, {self.early_game.id: self.early_game.home_team})
        self._finalize(self.early_game, 21, 14)
        detail = build_challenge_detail(challenge, now_utc=self.now)
        self.assertCountEqual([row.user_id for row in detail["winners"]], [self.creator.id, self.member.id])

    def test_corrected_score_changes_winner_dynamically(self):
        challenge = self._create()
        self._save_for_user(challenge, self.creator, {self.early_game.id: self.early_game.home_team})
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.away_team})
        self._finalize(self.early_game, 21, 14)
        first = build_challenge_detail(challenge, now_utc=self.now)
        self.assertEqual(first["winners"][0].user_id, self.creator.id)
        self._finalize(self.early_game, 14, 21)
        corrected = build_challenge_detail(challenge, now_utc=self.now)
        self.assertEqual(corrected["winners"][0].user_id, self.member.id)

    def test_nfl_tie_is_graded_without_correct_pick(self):
        challenge = self._create()
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        self._finalize(self.early_game, 20, 20)
        standing = self._standing_for(build_challenge_detail(challenge, now_utc=self.now), self.member)
        self.assertEqual((standing["correct_count"], standing["graded_count"]), (0, 1))

    def test_participant_sees_own_unlocked_pick_only(self):
        challenge = self._create()
        self._save_for_user(challenge, self.creator, {self.early_game.id: self.early_game.away_team})
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        detail = build_challenge_detail(challenge, user=self.member, now_utc=self.now)
        rows = self._game_detail_for(detail, self.early_game)["participant_picks"]
        own = next(row for row in rows if row["participant"].user_id == self.member.id)
        other = next(row for row in rows if row["participant"].user_id == self.creator.id)
        self.assertEqual(own["team_picked"], self.early_game.home_team)
        self.assertFalse(other["visible"])
        self.assertIsNone(other["team_picked"])

    def test_nonparticipant_admin_cannot_see_unlocked_picks(self):
        admin = self._user("reveal-admin")
        membership = self._membership(admin, self.group)
        membership.role = "group_admin"
        challenge = self._create()
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        db.session.commit()
        detail = build_challenge_detail(challenge, user=admin, now_utc=self.now)
        self.assertTrue(all(not row["visible"] for row in detail["games"][0]["participant_picks"]))

    def test_exactly_at_kickoff_reveals_all_picks(self):
        challenge = self._create()
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        self._lock_game(self.early_game, self.now)
        detail = build_challenge_detail(challenge, user=self.creator, now_utc=self.now)
        self.assertTrue(all(row["visible"] for row in detail["games"][0]["participant_picks"]))

    def test_after_kickoff_reveals_all_picks(self):
        challenge = self._create()
        self._lock_game(self.early_game, self.now - timedelta(seconds=1))
        detail = build_challenge_detail(challenge, now_utc=self.now)
        self.assertTrue(all(row["visible"] for row in detail["games"][0]["participant_picks"]))

    def test_thursday_revealed_while_sunday_remains_hidden(self):
        challenge = self._create(selected_game_ids=[self.early_game.id, self.late_game.id])
        self._lock_game(self.early_game)
        detail = build_challenge_detail(challenge, now_utc=self.now)
        self.assertTrue(all(row["visible"] for row in self._game_detail_for(detail, self.early_game)["participant_picks"]))
        self.assertTrue(all(not row["visible"] for row in self._game_detail_for(detail, self.late_game)["participant_picks"]))

    def test_revealed_game_identifies_missing_pick(self):
        challenge = self._create()
        self._lock_game(self.early_game)
        detail = build_challenge_detail(challenge, now_utc=self.now)
        rows = detail["games"][0]["participant_picks"]
        self.assertTrue(all(row["visible"] and row["has_pick"] is False for row in rows))

    def test_final_game_marks_correct_and_incorrect_picks(self):
        challenge = self._create()
        self._save_for_user(challenge, self.creator, {self.early_game.id: self.early_game.away_team})
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        self._lock_game(self.early_game)
        self._finalize(self.early_game, 24, 17)
        rows = build_challenge_detail(challenge, now_utc=self.now)["games"][0]["participant_picks"]
        results = {row["participant"].user_id: row["correct"] for row in rows}
        self.assertEqual(results, {self.creator.id: False, self.member.id: True})

    def test_completed_detail_renders_winner_badge(self):
        challenge = self._create()
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        self._finalize(self.early_game, 24, 17)
        self._login(self.member)
        response = self.client.get(f"/challenges/{challenge.id}")
        self.assertIn(b"Winner", response.data)

    def test_standing_order_is_deterministic_without_changing_tied_winners(self):
        self.creator.full_name = "Zulu"
        self.member.full_name = "Alpha"
        challenge = self._create()
        self._finalize(self.early_game, 24, 17)
        detail = build_challenge_detail(challenge, now_utc=self.now)
        self.assertEqual([row["participant"].user_id for row in detail["standings"]], [self.member.id, self.creator.id])
        self.assertCountEqual([row.user_id for row in detail["winners"]], [self.creator.id, self.member.id])

    def test_detail_reads_do_not_write_challenge_pick_data(self):
        challenge = self._create()
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        before = [(row.id, row.team_picked, row.updated_at) for row in ChallengePick.query.all()]
        build_challenge_detail(challenge, user=self.member, now_utc=self.now)
        after = [(row.id, row.team_picked, row.updated_at) for row in ChallengePick.query.all()]
        self.assertEqual(after, before)
        self.assertFalse(db.session.new)
        self.assertFalse(db.session.dirty)

    def test_creator_can_cancel_open_challenge(self):
        challenge = self._create()
        cancel_challenge(challenge, self.creator, now_utc=self.now)
        self.assertIsNotNone(challenge.cancelled_at)
        self.assertEqual(challenge.cancelled_by_user_id, self.creator.id)

    def test_creator_can_cancel_in_progress_challenge(self):
        challenge = self._create()
        self._lock_game(self.early_game)
        cancel_challenge(challenge, self.creator, now_utc=self.now)
        self.assertIsNotNone(challenge.cancelled_at)

    def test_group_admin_can_cancel(self):
        admin = self._user("cancel-admin")
        membership = self._membership(admin, self.group)
        membership.role = "group_admin"
        db.session.commit()
        challenge = self._create()
        self.assertTrue(can_cancel_challenge(admin, challenge))
        cancel_challenge(challenge, admin, now_utc=self.now)
        self.assertEqual(challenge.cancelled_by_user_id, admin.id)

    def test_inactive_former_group_admin_cannot_cancel(self):
        admin = self._user("former-cancel-admin")
        membership = self._membership(admin, self.group, active=False)
        membership.role = "group_admin"
        db.session.commit()
        challenge = self._create()
        self.assertFalse(can_cancel_challenge(admin, challenge))

    def test_global_admin_can_cancel_without_membership(self):
        self.outsider.is_admin = True
        db.session.commit()
        challenge = self._create()
        cancel_challenge(challenge, self.outsider, now_utc=self.now)
        self.assertEqual(challenge.cancelled_by_user_id, self.outsider.id)

    def test_unrelated_participant_cannot_cancel(self):
        challenge = self._create()
        self.assertFalse(can_cancel_challenge(self.member, challenge))
        with self.assertRaises(PermissionError):
            cancel_challenge(challenge, self.member, now_utc=self.now)

    def test_unrelated_group_member_cannot_cancel(self):
        member = self._user("cancel-unrelated-member")
        self._membership(member, self.group)
        db.session.commit()
        challenge = self._create()
        self.assertFalse(can_cancel_challenge(member, challenge))

    def test_completed_challenge_cannot_be_cancelled(self):
        challenge = self._create()
        self._finalize(self.early_game, 24, 17)
        with self.assertRaisesRegex(ChallengeCancellationError, "completed"):
            cancel_challenge(challenge, self.creator, now_utc=self.now)
        self.assertIsNone(challenge.cancelled_at)

    def test_already_cancelled_challenge_cannot_be_cancelled_again(self):
        challenge = self._create()
        cancel_challenge(challenge, self.creator, now_utc=self.now)
        original = challenge.cancelled_at
        with self.assertRaisesRegex(ChallengeCancellationError, "already cancelled"):
            cancel_challenge(challenge, self.creator, now_utc=self.now + timedelta(minutes=1))
        self.assertEqual(challenge.cancelled_at, original)

    def test_cancellation_preserves_participants_games_and_picks(self):
        challenge = self._create()
        self._save_for_user(challenge, self.member, {self.early_game.id: self.early_game.home_team})
        counts = (
            ChallengeParticipant.query.count(),
            ChallengeGame.query.count(),
            ChallengePick.query.count(),
        )
        cancel_challenge(challenge, self.creator, now_utc=self.now)
        self.assertEqual(
            (
                ChallengeParticipant.query.count(),
                ChallengeGame.query.count(),
                ChallengePick.query.count(),
            ),
            counts,
        )

    def test_cancelled_challenge_rejects_pick_updates(self):
        challenge = self._create()
        row = challenge.challenge_games[0]
        self._save_picks(challenge, picks=[(row.id, self.early_game.home_team)])
        cancel_challenge(challenge, self.creator, now_utc=self.now)
        with self.assertRaises(ChallengePickValidationError):
            self._save_picks(challenge, picks=[(row.id, self.early_game.away_team)])
        self.assertEqual(ChallengePick.query.one().team_picked, self.early_game.home_team)

    def test_cancelled_challenge_hides_save_and_cancel_controls(self):
        challenge = self._create()
        cancel_challenge(challenge, self.creator, now_utc=self.now)
        self._login(self.creator)
        response = self.client.get(f"/challenges/{challenge.id}")
        self.assertNotIn(b"Save Picks", response.data)
        self.assertNotIn(b">Cancel Challenge</button>", response.data)
        self.assertIn(b"Challenge cancelled", response.data)

    def test_completed_challenge_hides_cancel_control(self):
        challenge = self._create()
        self._finalize(self.early_game, 24, 17)
        self._login(self.creator)
        response = self.client.get(f"/challenges/{challenge.id}")
        self.assertNotIn(b">Cancel Challenge</button>", response.data)

    def test_cancel_button_only_visible_to_authorized_users(self):
        challenge = self._create()
        participant_detail = build_challenge_detail(
            challenge,
            user=self.member,
            now_utc=self.now,
        )
        self.assertFalse(participant_detail["can_cancel"])
        self._login(self.creator)
        creator_response = self.client.get(f"/challenges/{challenge.id}")
        self.assertIn(b">Cancel Challenge</button>", creator_response.data)

    def test_cancel_route_forbids_unauthorized_user(self):
        challenge = self._create()
        self._login(self.member)
        response = self.client.post(f"/challenges/{challenge.id}/cancel")
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(challenge.cancelled_at)

    def test_cancel_route_redirects_with_success_feedback(self):
        challenge = self._create()
        self._login(self.creator)
        response = self.client.post(
            f"/challenges/{challenge.id}/cancel",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"cancelled successfully", response.data)

    def test_cancelled_status_appears_on_list_and_detail(self):
        challenge = self._create()
        cancel_challenge(challenge, self.creator, now_utc=self.now)
        self._login(self.creator)
        detail = self.client.get(f"/challenges/{challenge.id}")
        listing = self.client.get("/groups?section=challenges")
        self.assertIn(b"Cancelled", detail.data)
        self.assertIn(b"Cancelled", listing.data)

    def test_cancellation_does_not_affect_normal_pick_or_user_score(self):
        challenge = self._create()
        regular_pick = Pick(
            user_id=self.creator.id,
            game_id=self.early_game.id,
            team_picked=self.early_game.home_team,
            week=1,
            group_id=self.group.id,
        )
        score = UserScore(
            user_id=self.creator.id,
            week=1,
            season_year=2026,
            season_type="REG",
            score=7,
            group_id=self.group.id,
        )
        db.session.add_all([regular_pick, score])
        db.session.commit()
        cancel_challenge(challenge, self.creator, now_utc=self.now)
        self.assertEqual(db.session.get(Pick, regular_pick.id).team_picked, self.early_game.home_team)
        self.assertEqual(db.session.get(UserScore, score.id).score, 7)

    def test_removed_creator_retains_cancellation_rights(self):
        challenge = self._create()
        GroupMember.query.filter_by(user_id=self.creator.id, group_id=self.group.id).one().is_active = False
        db.session.commit()
        self.assertTrue(can_cancel_challenge(self.creator, challenge))


if __name__ == "__main__":
    unittest.main()
