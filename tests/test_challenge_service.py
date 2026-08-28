import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from Football_Project.services.challenge_service import (
    calculate_participant_standings,
    derive_challenge_status,
    determine_challenge_winners,
    is_challenge_pick_correct,
    is_game_locked,
    winner_for_game,
)


NOW = datetime(2026, 9, 13, 18, 0, tzinfo=timezone.utc)


def game(
    game_id,
    *,
    kickoff=NOW,
    status="STATUS_SCHEDULED",
    home_score=None,
    away_score=None,
):
    return SimpleNamespace(
        id=game_id,
        commence_time_mt=kickoff,
        status=status,
        home_team=f"Home {game_id}",
        away_team=f"Away {game_id}",
        home_team_score=home_score,
        away_team_score=away_score,
    )


class GameLockTests(unittest.TestCase):
    def test_before_kickoff_is_open(self):
        self.assertFalse(is_game_locked(game(1, kickoff=NOW + timedelta(seconds=1)), NOW))

    def test_exactly_at_kickoff_is_locked(self):
        self.assertTrue(is_game_locked(game(1, kickoff=NOW), NOW))

    def test_after_kickoff_is_locked(self):
        self.assertTrue(is_game_locked(game(1, kickoff=NOW - timedelta(seconds=1)), NOW))

    def test_one_game_can_lock_while_another_remains_open(self):
        locked = game(1, kickoff=NOW - timedelta(minutes=1))
        open_game = game(2, kickoff=NOW + timedelta(minutes=1))
        self.assertTrue(is_game_locked(locked, NOW))
        self.assertFalse(is_game_locked(open_game, NOW))


class GameResultTests(unittest.TestCase):
    def test_home_team_winner(self):
        final = game(1, status="STATUS_FINAL", home_score=24, away_score=17)
        self.assertEqual(winner_for_game(final), final.home_team)
        self.assertTrue(is_challenge_pick_correct(final, final.home_team))
        self.assertFalse(is_challenge_pick_correct(final, final.away_team))

    def test_away_team_winner_with_existing_status_variant(self):
        final = game(1, status="completed", home_score=14, away_score=21)
        self.assertEqual(winner_for_game(final), final.away_team)
        self.assertTrue(is_challenge_pick_correct(final, final.away_team))

    def test_nfl_tie_awards_no_correct_pick(self):
        final = game(1, status="FINAL", home_score=20, away_score=20)
        self.assertIsNone(winner_for_game(final))
        self.assertFalse(is_challenge_pick_correct(final, final.home_team))
        self.assertFalse(is_challenge_pick_correct(final, final.away_team))

    def test_non_final_game_is_ungraded(self):
        live = game(1, status="STATUS_IN_PROGRESS", home_score=21, away_score=14)
        self.assertIsNone(winner_for_game(live))
        self.assertIsNone(is_challenge_pick_correct(live, live.home_team))

    def test_final_game_with_missing_score_is_ungraded(self):
        incomplete = game(1, status="STATUS_FINAL", home_score=21, away_score=None)
        self.assertIsNone(is_challenge_pick_correct(incomplete, incomplete.home_team))


class ChallengeStatusTests(unittest.TestCase):
    def test_open_challenge(self):
        games = [game(1, kickoff=NOW + timedelta(hours=1))]
        self.assertEqual(derive_challenge_status(games, now_utc=NOW), "open")

    def test_in_progress_challenge(self):
        games = [
            game(1, kickoff=NOW - timedelta(minutes=1), status="STATUS_IN_PROGRESS"),
            game(2, kickoff=NOW + timedelta(hours=1)),
        ]
        self.assertEqual(derive_challenge_status(games, now_utc=NOW), "in_progress")

    def test_completed_challenge_supports_final_status_variants(self):
        games = [
            game(1, status="STATUS_FINAL", home_score=21, away_score=14),
            game(2, status="STATUS_GAME_OVER", home_score=10, away_score=17),
            game(3, status="COMPLETE", home_score=7, away_score=6),
        ]
        self.assertEqual(derive_challenge_status(games, now_utc=NOW), "completed")

    def test_cancelled_challenge_takes_precedence(self):
        games = [game(1, status="FINAL", home_score=21, away_score=14)]
        self.assertEqual(
            derive_challenge_status(games, cancelled_at=NOW, now_utc=NOW),
            "cancelled",
        )


class ChallengeStandingsTests(unittest.TestCase):
    def test_participant_standings(self):
        first = game(1, status="FINAL", home_score=24, away_score=17)
        second = game(2, status="FINAL", home_score=10, away_score=20)
        standings = calculate_participant_standings(
            [10, 20],
            [first, second],
            {
                10: {1: first.home_team, 2: second.away_team},
                20: {1: first.away_team, 2: second.away_team},
            },
        )
        self.assertEqual(
            standings,
            [
                {"participant_id": 10, "correct_count": 2, "graded_count": 2, "total_games": 2},
                {"participant_id": 20, "correct_count": 1, "graded_count": 2, "total_games": 2},
            ],
        )

    def test_two_participants_can_tie_for_winner(self):
        final = game(1, status="FINAL", home_score=24, away_score=17)
        standings = calculate_participant_standings(
            [10, 20],
            [final],
            {10: {1: final.home_team}, 20: {1: final.home_team}},
        )
        winners = determine_challenge_winners(standings, challenge_status="completed")
        self.assertEqual(winners, [10, 20])

    def test_corrected_score_changes_calculated_result(self):
        final = game(1, status="FINAL", home_score=24, away_score=17)
        picks = {10: {1: final.home_team}, 20: {1: final.away_team}}

        original = calculate_participant_standings([10, 20], [final], picks)
        self.assertEqual(determine_challenge_winners(original, challenge_status="completed"), [10])

        final.home_team_score = 17
        final.away_team_score = 24

        corrected = calculate_participant_standings([10, 20], [final], picks)
        self.assertEqual(determine_challenge_winners(corrected, challenge_status="completed"), [20])


if __name__ == "__main__":
    unittest.main()
