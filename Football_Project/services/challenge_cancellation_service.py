"""Authorization and persistence for cancelling challenges."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func

from Football_Project.extensions import db
from Football_Project.models import Challenge, GroupMember
from Football_Project.services.challenge_service import derive_challenge_status


class ChallengeCancellationError(ValueError):
    """Raised when a challenge cannot be cancelled in its current state."""


def can_cancel_challenge(user, challenge: Challenge) -> bool:
    """Return whether a user has cancellation authority for this challenge."""

    if getattr(user, "is_admin", False):
        return True
    if challenge.creator_user_id == user.id:
        return True
    return GroupMember.query.filter(
        GroupMember.user_id == user.id,
        GroupMember.group_id == challenge.group_id,
        GroupMember.is_active.is_(True),
        func.lower(func.trim(GroupMember.role)) == "group_admin",
    ).first() is not None


def validate_challenge_can_be_cancelled(
    challenge: Challenge,
    *,
    now_utc: datetime | None = None,
) -> str:
    status = derive_challenge_status(
        [row.game for row in challenge.challenge_games],
        cancelled_at=challenge.cancelled_at,
        now_utc=now_utc,
    )
    if status == "cancelled":
        raise ChallengeCancellationError("This challenge is already cancelled.")
    if status == "completed":
        raise ChallengeCancellationError("A completed challenge cannot be cancelled.")
    return status


def cancel_challenge(
    challenge: Challenge,
    user,
    *,
    now_utc: datetime | None = None,
) -> Challenge:
    """Cancel an open/in-progress challenge without deleting related rows."""

    try:
        if not can_cancel_challenge(user, challenge):
            raise PermissionError("You are not authorized to cancel this challenge.")
        current = now_utc or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("now_utc must be timezone-aware")
        validate_challenge_can_be_cancelled(challenge, now_utc=current)
        challenge.cancelled_at = current.astimezone(timezone.utc)
        challenge.cancelled_by_user_id = user.id
        db.session.commit()
        return challenge
    except Exception:
        db.session.rollback()
        raise
