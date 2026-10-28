"""Visibility queries and read models for challenge list/detail views."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from Football_Project.extensions import db
from Football_Project.models import (
    Challenge,
    ChallengeGame,
    ChallengeParticipant,
    ChallengePick,
    GroupMember,
)
from Football_Project.services.challenge_service import (
    calculate_participant_standings,
    derive_challenge_status,
    determine_challenge_winners,
    is_challenge_pick_correct,
    is_game_locked,
    winner_for_game,
)
from Football_Project.services.challenge_cancellation_service import (
    can_cancel_challenge,
)
from Football_Project.services.challenge_deletion_service import can_delete_challenge


FINAL_STATUSES = {"STATUS_FINAL", "FINAL", "COMPLETED", "COMPLETE", "STATUS_GAME_OVER"}


def _game_has_final_score(game) -> bool:
    return (
        str(game.status or "").strip().upper() in FINAL_STATUSES
        and game.home_team_score is not None
        and game.away_team_score is not None
    )


def _challenge_load_options():
    return (
        selectinload(Challenge.group),
        selectinload(Challenge.creator),
        selectinload(Challenge.cancelled_by),
        selectinload(Challenge.participants).selectinload(
            ChallengeParticipant.user
        ),
        selectinload(Challenge.challenge_games).selectinload(
            ChallengeGame.game
        ),
    )


def get_visible_challenges(user) -> list[Challenge]:
    """Return challenges visible to a user with related display data loaded."""

    query = Challenge.query.options(*_challenge_load_options())
    if not getattr(user, "is_admin", False):
        managed_group_ids = select(GroupMember.group_id).where(
            GroupMember.user_id == user.id,
            GroupMember.is_active.is_(True),
            func.lower(func.trim(GroupMember.role)) == "group_admin",
        )
        query = query.filter(
            or_(
                Challenge.creator_user_id == user.id,
                Challenge.participants.any(
                    ChallengeParticipant.user_id == user.id
                ),
                Challenge.group_id.in_(managed_group_ids),
            )
        )

    return query.order_by(Challenge.created_at.desc(), Challenge.id.desc()).all()


def can_view_challenge(user, challenge: Challenge) -> bool:
    if getattr(user, "is_admin", False):
        return True
    if challenge.creator_user_id == user.id:
        return True
    if any(participant.user_id == user.id for participant in challenge.participants):
        return True
    return GroupMember.query.filter(
        GroupMember.user_id == user.id,
        GroupMember.group_id == challenge.group_id,
        GroupMember.is_active.is_(True),
        func.lower(func.trim(GroupMember.role)) == "group_admin",
    ).first() is not None


def get_challenge_for_detail(challenge_id: int) -> Challenge | None:
    return (
        Challenge.query
        .options(*_challenge_load_options())
        .filter(Challenge.id == challenge_id)
        .first()
    )


def build_challenge_summary(
    challenge: Challenge,
    *,
    now_utc: datetime | None = None,
) -> dict:
    games = [row.game for row in challenge.challenge_games]
    return {
        "challenge": challenge,
        "status": derive_challenge_status(
            games,
            cancelled_at=challenge.cancelled_at,
            now_utc=now_utc,
        ),
        "participant_count": len(challenge.participants),
        "game_count": len(challenge.challenge_games),
    }


def build_visible_challenge_summaries(
    user,
    *,
    now_utc: datetime | None = None,
) -> list[dict]:
    current = now_utc or datetime.now(timezone.utc)
    return [
        build_challenge_summary(challenge, now_utc=current)
        for challenge in get_visible_challenges(user)
    ]


def load_challenge_picks(challenge_id: int) -> list[ChallengePick]:
    """Load every submitted pick for one challenge in a single query."""

    return ChallengePick.query.filter_by(challenge_id=challenge_id).all()


def build_challenge_standings(
    challenge: Challenge,
    picks: list[ChallengePick],
    *,
    status: str,
) -> tuple[list[dict], set[int]]:
    """Adapt persisted picks to pure scoring helpers and display ordering."""

    game_by_challenge_game_id = {
        row.id: row.game for row in challenge.challenge_games
    }
    challenge_type = challenge.challenge_type or "winner"
    picks_by_participant = {}
    for pick in picks:
        game = game_by_challenge_game_id.get(pick.challenge_game_id)
        if game is not None:
            picks_by_participant.setdefault(pick.participant_id, {})[game.id] = pick

    participants_by_id = {
        participant.id: participant for participant in challenge.participants
    }
    if challenge_type == "winner":
        winner_values = {
            participant_id: {
                game_id: pick.team_picked for game_id, pick in participant_picks.items()
            }
            for participant_id, participant_picks in picks_by_participant.items()
        }
        scored = calculate_participant_standings(
            participants_by_id,
            [row.game for row in challenge.challenge_games],
            winner_values,
        )
    else:
        scored = []
        for participant_id in participants_by_id:
            correct_count = 0
            prediction_error = 0
            graded_count = 0
            for challenge_game in challenge.challenge_games:
                game = challenge_game.game
                if not _game_has_final_score(game):
                    continue
                graded_count += 1
                pick = picks_by_participant.get(participant_id, {}).get(game.id)
                if challenge_type == "score":
                    if pick and pick.predicted_home_score is not None and pick.predicted_away_score is not None:
                        error = abs(pick.predicted_home_score - game.home_team_score) + abs(pick.predicted_away_score - game.away_team_score)
                        prediction_error += error
                        if error == 0:
                            correct_count += 1
                    else:
                        prediction_error += 201
                elif pick:
                    total = game.home_team_score + game.away_team_score
                    result = "over" if total > challenge_game.over_under_line else "under" if total < challenge_game.over_under_line else "push"
                    if pick.team_picked == result:
                        correct_count += 1
            scored.append({
                "participant_id": participant_id,
                "correct_count": correct_count,
                "prediction_error": prediction_error,
                "graded_count": graded_count,
                "total_games": len(challenge.challenge_games),
            })

    if status != "completed" or not scored:
        winner_ids = set()
    elif challenge_type == "score":
        best = min(row["prediction_error"] for row in scored)
        winner_ids = {row["participant_id"] for row in scored if row["prediction_error"] == best}
    else:
        winner_ids = set(determine_challenge_winners(scored, challenge_status=status))
    standings = []
    for row in scored:
        participant = participants_by_id[row["participant_id"]]
        standings.append(
            {
                **row,
                "participant": participant,
                "remaining_count": row["total_games"] - row["graded_count"],
                "is_winner": participant.id in winner_ids,
            }
        )
    standings.sort(
        key=lambda row: (
            row.get("prediction_error", -row["correct_count"]),
            -row["graded_count"],
            (
                row["participant"].user.full_name
                or row["participant"].user.username
                or ""
            ).lower(),
            row["participant_id"],
        )
    )
    return standings, winner_ids


def build_game_pick_display(
    challenge_game: ChallengeGame,
    participants: list[ChallengeParticipant],
    picks_by_key: dict[tuple[int, int], ChallengePick],
    *,
    current_participant: ChallengeParticipant | None,
    revealed: bool,
    challenge_type: str,
) -> list[dict]:
    """Build reveal-safe pick rows for one selected game."""

    display = []
    for participant in participants:
        pick = picks_by_key.get((participant.id, challenge_game.id))
        visible = revealed or (
            current_participant is not None
            and participant.id == current_participant.id
        )
        if challenge_type == "score" and pick:
            display_value = f"{pick.predicted_away_score}-{pick.predicted_home_score}"
            correct = (
                pick.predicted_home_score == challenge_game.game.home_team_score
                and pick.predicted_away_score == challenge_game.game.away_team_score
            ) if revealed and _game_has_final_score(challenge_game.game) else None
        elif challenge_type == "over_under" and pick:
            display_value = (pick.team_picked or "").title()
            if revealed and _game_has_final_score(challenge_game.game):
                total = challenge_game.game.home_team_score + challenge_game.game.away_team_score
                result = "over" if total > challenge_game.over_under_line else "under" if total < challenge_game.over_under_line else "push"
                correct = pick.team_picked == result
            else:
                correct = None
        else:
            display_value = pick.team_picked if pick else None
            correct = is_challenge_pick_correct(
                challenge_game.game,
                pick.team_picked if pick else None,
            ) if revealed else None
        display.append(
            {
                "participant": participant,
                "visible": visible,
                "team_picked": pick.team_picked if visible and pick else None,
                "display_value": display_value if visible else None,
                "has_pick": bool(pick) if visible else None,
                "correct": correct,
            }
        )
    return display


def build_challenge_detail(
    challenge: Challenge,
    *,
    user=None,
    now_utc: datetime | None = None,
) -> dict:
    current = now_utc or datetime.now(timezone.utc)
    ordered_rows = sorted(
        challenge.challenge_games,
        key=lambda row: (row.display_order, row.id),
    )
    games = [row.game for row in ordered_rows]
    participant = None
    if user is not None:
        participant = next(
            (row for row in challenge.participants if row.user_id == user.id),
            None,
        )
    picks = load_challenge_picks(challenge.id)
    picks_by_key = {
        (pick.participant_id, pick.challenge_game_id): pick for pick in picks
    }
    current_picks = {}
    active_membership = False
    if participant is not None:
        current_picks = {
            pick.challenge_game_id: pick
            for pick in picks
            if pick.participant_id == participant.id
        }
        active_membership = GroupMember.query.filter_by(
            user_id=user.id,
            group_id=challenge.group_id,
            is_active=True,
        ).first() is not None

    status = derive_challenge_status(
        games,
        cancelled_at=challenge.cancelled_at,
        now_utc=current,
    )
    ordered_participants = sorted(
        challenge.participants,
        key=lambda row: ((row.user.username or "").lower(), row.id),
    )
    standings, winner_ids = build_challenge_standings(
        challenge,
        picks,
        status=status,
    )
    return {
        "challenge": challenge,
        "status": status,
        "participants": ordered_participants,
        "standings": standings,
        "winners": [
            row["participant"] for row in standings if row["participant_id"] in winner_ids
        ],
        "current_participant": participant,
        "can_cancel": (
            user is not None
            and status in {"open", "in_progress"}
            and can_cancel_challenge(user, challenge)
        ),
        "can_delete": user is not None and can_delete_challenge(user, challenge),
        "can_submit_picks": (
            participant is not None
            and active_membership
            and challenge.cancelled_at is None
        ),
        "games": [
            _build_game_detail(
                row,
                ordered_participants,
                picks_by_key,
                current_picks,
                participant,
                current,
                challenge.challenge_type or "winner",
            )
            for row in ordered_rows
        ],
    }


def _build_game_detail(
    row: ChallengeGame,
    participants: list[ChallengeParticipant],
    picks_by_key: dict[tuple[int, int], ChallengePick],
    current_picks: dict[int, ChallengePick],
    current_participant: ChallengeParticipant | None,
    now_utc: datetime,
    challenge_type: str,
) -> dict:
    locked = is_game_locked(row.game, now_utc=now_utc)
    return {
        "challenge_game": row,
        "game": row.game,
        "locked": locked,
        "current_pick": current_picks.get(row.id),
        "winning_team": winner_for_game(row.game),
        "participant_picks": build_game_pick_display(
            row,
            participants,
            picks_by_key,
            current_participant=current_participant,
            revealed=locked,
            challenge_type=challenge_type,
        ),
    }
