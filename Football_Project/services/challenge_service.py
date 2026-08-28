"""Pure domain logic for group challenges.

This module intentionally has no Flask, SQLAlchemy, or application-model imports.
Callers are responsible for loading authorized challenge data and adapting stored
picks into the simple inputs accepted here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo


MOUNTAIN_TIME = ZoneInfo("America/Denver")
FINAL_GAME_STATUSES = frozenset(
    {
        "STATUS_FINAL",
        "FINAL",
        "COMPLETED",
        "COMPLETE",
        "STATUS_GAME_OVER",
    }
)


def _normalized_status(status: object) -> str:
    return str(status or "").strip().upper()


def _aware_utc(value: datetime, *, assume_mountain_if_naive: bool) -> datetime:
    if value.tzinfo is None:
        if not assume_mountain_if_naive:
            raise ValueError("now_utc must be timezone-aware")
        value = value.replace(tzinfo=MOUNTAIN_TIME)
    return value.astimezone(timezone.utc)


def _has_final_result(game: object) -> bool:
    return (
        _normalized_status(getattr(game, "status", None)) in FINAL_GAME_STATUSES
        and getattr(game, "home_team_score", None) is not None
        and getattr(game, "away_team_score", None) is not None
    )


def is_game_locked(game: object, now_utc: datetime | None = None) -> bool:
    """Return whether a game has reached its authoritative kickoff time.

    ``Game.commence_time_mt`` is authoritative. A naive stored kickoff is treated
    as Mountain time for compatibility with existing application data. An
    explicitly supplied ``now_utc`` must be timezone-aware.
    """

    kickoff = getattr(game, "commence_time_mt", None)
    if kickoff is None:
        return False

    current = now_utc or datetime.now(timezone.utc)
    current_utc = _aware_utc(current, assume_mountain_if_naive=False)
    kickoff_utc = _aware_utc(kickoff, assume_mountain_if_naive=True)
    return current_utc >= kickoff_utc


def winner_for_game(game: object) -> str | None:
    """Return the straight-up winning team for a final, scored game.

    ``None`` represents either an ungraded game or an NFL tie. Callers that need
    to distinguish those cases should use ``is_challenge_pick_correct``, which
    returns ``None`` only for ungraded games and ``False`` for a tied game.
    """

    if not _has_final_result(game):
        return None

    home_score = getattr(game, "home_team_score")
    away_score = getattr(game, "away_team_score")
    if home_score > away_score:
        return getattr(game, "home_team")
    if away_score > home_score:
        return getattr(game, "away_team")
    return None


def derive_challenge_status(
    games: Sequence[object],
    *,
    cancelled_at: datetime | None = None,
    now_utc: datetime | None = None,
) -> str:
    """Derive ``open``, ``in_progress``, ``completed``, or ``cancelled``.

    A valid challenge must contain at least one selected game. Cancellation has
    precedence, and completion requires a final status plus scores for every
    selected game.
    """

    if cancelled_at is not None:
        return "cancelled"
    if not games:
        raise ValueError("A challenge must contain at least one game")
    if all(_has_final_result(game) for game in games):
        return "completed"
    if any(is_game_locked(game, now_utc=now_utc) for game in games):
        return "in_progress"
    return "open"


def is_challenge_pick_correct(game: object, team_picked: str | None) -> bool | None:
    """Return pick correctness, or ``None`` while the game is ungraded.

    An NFL tie is graded but awards no correct pick, so it returns ``False``.
    """

    if not _has_final_result(game):
        return None
    winner = winner_for_game(game)
    if winner is None:
        return False
    return bool(team_picked) and team_picked == winner


def calculate_participant_standings(
    participant_ids: Iterable[int],
    games: Sequence[object],
    picks_by_participant: Mapping[int, Mapping[int, str]],
) -> list[dict[str, int]]:
    """Calculate challenge-only standings without persisting any scores.

    ``picks_by_participant`` has the form
    ``{participant_id: {game_id: team_picked}}``. Standings are sorted by most
    correct picks, then participant id for deterministic output.
    """

    standings: list[dict[str, int]] = []
    graded_games = sum(1 for game in games if _has_final_result(game))

    for participant_id in participant_ids:
        participant_picks = picks_by_participant.get(participant_id, {})
        correct_count = 0
        for game in games:
            result = is_challenge_pick_correct(
                game,
                participant_picks.get(getattr(game, "id")),
            )
            if result is True:
                correct_count += 1

        standings.append(
            {
                "participant_id": participant_id,
                "correct_count": correct_count,
                "graded_count": graded_games,
                "total_games": len(games),
            }
        )

    return sorted(
        standings,
        key=lambda row: (-row["correct_count"], row["participant_id"]),
    )


def determine_challenge_winners(
    standings: Sequence[Mapping[str, int]],
    *,
    challenge_status: str,
) -> list[int]:
    """Return every winning participant id, including ties.

    Winners are declared only for a completed challenge.
    """

    if challenge_status != "completed" or not standings:
        return []
    best_score = max(row["correct_count"] for row in standings)
    return [
        row["participant_id"]
        for row in standings
        if row["correct_count"] == best_score
    ]
