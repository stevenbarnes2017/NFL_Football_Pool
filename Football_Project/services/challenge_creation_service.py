"""Authorization, validation, and persistence for creating challenges."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
from zoneinfo import ZoneInfo

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
from Football_Project.services.challenge_service import is_game_locked


MOUNTAIN_TIME = ZoneInfo("America/Denver")


class ChallengeValidationError(ValueError):
    """Raised when a challenge creation request violates an MVP rule."""


def _normalize_ids(raw_ids: Iterable[object], label: str) -> list[int]:
    normalized: list[int] = []
    seen: set[int] = set()

    for raw_id in raw_ids:
        try:
            value = int(raw_id)
        except (TypeError, ValueError) as exc:
            raise ChallengeValidationError(f"Invalid {label} selection.") from exc
        if value <= 0:
            raise ChallengeValidationError(f"Invalid {label} selection.")
        if value not in seen:
            seen.add(value)
            normalized.append(value)

    return normalized


def validate_active_group_membership(user_id: int, group_id: int) -> GroupMember:
    group = db.session.get(PoolGroup, group_id)
    if group is None or not group.is_active:
        raise ChallengeValidationError("That group is not available.")

    membership = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=group_id,
        is_active=True,
    ).first()
    if membership is None:
        raise ChallengeValidationError(
            "You must be an active member of this group to create a challenge."
        )
    return membership


def load_eligible_group_members(group_id: int) -> list[User]:
    return (
        User.query
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(
            GroupMember.group_id == group_id,
            GroupMember.is_active.is_(True),
            User.is_active.is_(True),
        )
        .order_by(User.username.asc())
        .all()
    )


def _current_settings() -> Settings:
    settings = Settings.query.first()
    if settings is None:
        raise ChallengeValidationError(
            "Current NFL season settings are not configured."
        )
    return settings


def load_eligible_current_week_games(
    settings: Settings | None = None,
    *,
    now_utc: datetime | None = None,
) -> list[Game]:
    settings = settings or _current_settings()
    current = now_utc or datetime.now(timezone.utc)
    games = (
        Game.query
        .filter(
            Game.season_year == settings.season_year,
            Game.season_type == settings.season_type,
            Game.week == settings.current_week,
            Game.commence_time_mt.isnot(None),
        )
        .order_by(Game.commence_time_mt.asc(), Game.id.asc())
        .all()
    )
    return [game for game in games if not is_game_locked(game, now_utc=current)]


def validate_selected_participant_ids(
    group_id: int,
    creator_user_id: int,
    selected_participant_ids: Iterable[object],
) -> list[int]:
    selected_ids = _normalize_ids(selected_participant_ids, "participant")
    participant_ids = [creator_user_id]
    participant_ids.extend(
        user_id for user_id in selected_ids if user_id != creator_user_id
    )

    if len(participant_ids) < 2:
        raise ChallengeValidationError(
            "Select at least one additional group member."
        )

    eligible_ids = {
        user.id
        for user in load_eligible_group_members(group_id)
    }
    invalid_ids = set(participant_ids) - eligible_ids
    if invalid_ids:
        raise ChallengeValidationError(
            "Every participant must be an active member of this group."
        )
    return participant_ids


def _kickoff_utc(game: Game) -> datetime:
    kickoff = game.commence_time_mt
    if kickoff.tzinfo is None:
        kickoff = kickoff.replace(tzinfo=MOUNTAIN_TIME)
    return kickoff.astimezone(timezone.utc)


def validate_selected_game_ids(
    selected_game_ids: Iterable[object],
    settings: Settings,
    *,
    now_utc: datetime | None = None,
) -> list[Game]:
    game_ids = _normalize_ids(selected_game_ids, "game")
    if not game_ids:
        raise ChallengeValidationError("Select at least one game.")

    games = Game.query.filter(Game.id.in_(game_ids)).all()
    games_by_id = {game.id: game for game in games}
    if set(game_ids) != set(games_by_id):
        raise ChallengeValidationError("One or more selected games do not exist.")

    current = now_utc or datetime.now(timezone.utc)
    for game_id in game_ids:
        game = games_by_id[game_id]
        if (
            game.season_year != settings.season_year
            or game.season_type != settings.season_type
            or game.week != settings.current_week
        ):
            raise ChallengeValidationError(
                "Every selected game must be from the current NFL week."
            )
        if game.commence_time_mt is None:
            raise ChallengeValidationError(
                "Every selected game must have a scheduled kickoff."
            )
        if is_game_locked(game, now_utc=current):
            raise ChallengeValidationError(
                "A selected game has already started."
            )

    return sorted(
        games_by_id.values(),
        key=lambda game: (_kickoff_utc(game), game.id),
    )


def create_challenge(
    *,
    group_id: int,
    creator_user_id: int,
    name: str,
    description: str | None,
    selected_participant_ids: Iterable[object],
    selected_game_ids: Iterable[object],
    now_utc: datetime | None = None,
) -> Challenge:
    """Validate and create a challenge and all associations atomically."""

    try:
        clean_name = (name or "").strip()
        if not clean_name:
            raise ChallengeValidationError("Challenge name is required.")
        if len(clean_name) > 140:
            raise ChallengeValidationError(
                "Challenge name must be 140 characters or fewer."
            )

        membership = validate_active_group_membership(
            creator_user_id,
            group_id,
        )
        group = membership.group
        settings = _current_settings()
        participant_ids = validate_selected_participant_ids(
            group_id,
            creator_user_id,
            selected_participant_ids,
        )
        games = validate_selected_game_ids(
            selected_game_ids,
            settings,
            now_utc=now_utc,
        )

        challenge = Challenge(
            group_id=group.id,
            creator_user_id=creator_user_id,
            name=clean_name,
            description=(description or "").strip() or None,
            season_year=settings.season_year,
            season_type=settings.season_type,
            week=settings.current_week,
        )
        db.session.add(challenge)
        db.session.flush()

        db.session.add_all(
            ChallengeParticipant(
                challenge_id=challenge.id,
                user_id=user_id,
            )
            for user_id in participant_ids
        )
        db.session.add_all(
            ChallengeGame(
                challenge_id=challenge.id,
                game_id=game.id,
                display_order=display_order,
            )
            for display_order, game in enumerate(games, start=1)
        )
        db.session.commit()
        return challenge
    except Exception:
        db.session.rollback()
        raise
