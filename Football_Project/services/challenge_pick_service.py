"""Validation and persistence for a participant's challenge picks."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Iterable

from Football_Project.extensions import db
from Football_Project.models import (
    Challenge,
    ChallengeGame,
    ChallengeParticipant,
    ChallengePick,
    GroupMember,
)
from Football_Project.services.challenge_service import is_game_locked


class ChallengePickError(ValueError):
    """Base error for a rejected challenge-pick submission."""


class ChallengePickAuthorizationError(ChallengePickError):
    """Raised when a user is not allowed to submit challenge picks."""


class ChallengePickValidationError(ChallengePickError):
    """Raised when submitted challenge-pick data is invalid."""


def resolve_participant(challenge_id: int, user_id: int) -> ChallengeParticipant:
    participant = ChallengeParticipant.query.filter_by(
        challenge_id=challenge_id,
        user_id=user_id,
    ).first()
    if participant is None:
        raise ChallengePickAuthorizationError(
            "Only challenge participants may submit picks."
        )
    return participant


def validate_active_group_membership(user_id: int, group_id: int) -> GroupMember:
    membership = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=group_id,
        is_active=True,
    ).first()
    if membership is None:
        raise ChallengePickAuthorizationError(
            "You must be an active member of this group to submit picks."
        )
    return membership


def load_participant_picks(
    challenge_id: int,
    participant_id: int,
) -> dict[int, ChallengePick]:
    return {
        pick.challenge_game_id: pick
        for pick in ChallengePick.query.filter_by(
            challenge_id=challenge_id,
            participant_id=participant_id,
        ).all()
    }


def _normalize_submissions(
    submitted_picks: Iterable[tuple[object, object]],
) -> dict[int, str]:
    values: dict[int, set[str]] = defaultdict(set)
    for raw_game_id, raw_team in submitted_picks:
        try:
            challenge_game_id = int(raw_game_id)
        except (TypeError, ValueError) as exc:
            raise ChallengePickValidationError(
                "Invalid challenge game selection."
            ) from exc
        if challenge_game_id <= 0:
            raise ChallengePickValidationError("Invalid challenge game selection.")
        values[challenge_game_id].add(str(raw_team))

    if any(len(teams) > 1 for teams in values.values()):
        raise ChallengePickValidationError(
            "Conflicting picks were submitted for the same game."
        )
    return {game_id: next(iter(teams)) for game_id, teams in values.items()}


def save_challenge_picks(
    *,
    challenge: Challenge,
    user_id: int,
    submitted_picks: Iterable[tuple[object, object]],
    submitted_scores: Iterable[tuple[object, object, object]] = (),
    now_utc: datetime | None = None,
) -> dict[str, int]:
    """Validate and atomically upsert unlocked picks for one participant."""

    try:
        participant = resolve_participant(challenge.id, user_id)
        validate_active_group_membership(user_id, challenge.group_id)
        if challenge.cancelled_at is not None:
            raise ChallengePickValidationError(
                "Picks cannot be changed for a cancelled challenge."
            )

        normalized = _normalize_submissions(submitted_picks)
        normalized_scores = {}
        for raw_game_id, raw_home, raw_away in submitted_scores:
            try:
                game_id = int(raw_game_id)
                home_score = int(raw_home)
                away_score = int(raw_away)
            except (TypeError, ValueError) as exc:
                raise ChallengePickValidationError(
                    "Score predictions must use whole numbers."
                ) from exc
            if game_id <= 0 or not 0 <= home_score <= 100 or not 0 <= away_score <= 100:
                raise ChallengePickValidationError(
                    "Predicted scores must be between 0 and 100."
                )
            normalized_scores[game_id] = (home_score, away_score)

        challenge_type = challenge.challenge_type or "winner"
        if challenge_type == "score":
            normalized_ids = set(normalized_scores)
        else:
            normalized_ids = set(normalized)
        challenge_games = {
            row.id: row
            for row in ChallengeGame.query.filter_by(
                challenge_id=challenge.id
            ).all()
        }
        unknown_ids = normalized_ids - set(challenge_games)
        if unknown_ids:
            raise ChallengePickValidationError(
                "One or more submitted games do not belong to this challenge."
            )

        current = now_utc or datetime.now(timezone.utc)
        editable = []
        locked_count = 0
        for game_id in normalized_ids:
            challenge_game = challenge_games[game_id]
            if is_game_locked(challenge_game.game, now_utc=current):
                locked_count += 1
                continue
            if challenge_type == "score":
                editable.append((challenge_game, None, *normalized_scores[game_id]))
                continue
            team = normalized[game_id]
            allowed = (
                {"over", "under"}
                if challenge_type == "over_under"
                else {challenge_game.game.home_team, challenge_game.game.away_team}
            )
            if team not in allowed:
                raise ChallengePickValidationError("Invalid prediction for this game.")
            editable.append((challenge_game, team, None, None))

        existing = load_participant_picks(challenge.id, participant.id)
        created = 0
        updated = 0
        unchanged = 0
        for challenge_game, team, home_score, away_score in editable:
            pick = existing.get(challenge_game.id)
            if pick is None:
                db.session.add(
                    ChallengePick(
                        challenge_id=challenge.id,
                        participant_id=participant.id,
                        challenge_game_id=challenge_game.id,
                        team_picked=team,
                        predicted_home_score=home_score,
                        predicted_away_score=away_score,
                    )
                )
                created += 1
            elif (
                pick.team_picked != team
                or pick.predicted_home_score != home_score
                or pick.predicted_away_score != away_score
            ):
                pick.team_picked = team
                pick.predicted_home_score = home_score
                pick.predicted_away_score = away_score
                pick.updated_at = current
                updated += 1
            else:
                unchanged += 1

        db.session.commit()
        return {
            "saved": created + updated,
            "created": created,
            "updated": updated,
            "unchanged": unchanged,
            "locked": locked_count,
        }
    except Exception:
        db.session.rollback()
        raise
