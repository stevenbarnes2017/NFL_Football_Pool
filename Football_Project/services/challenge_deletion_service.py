"""Creator-only permanent deletion for challenges."""

from Football_Project.extensions import db
from Football_Project.models import (
    Challenge,
    ChallengeGame,
    ChallengeParticipant,
    ChallengePick,
)


def can_delete_challenge(user, challenge: Challenge) -> bool:
    """Only the user who created a challenge may permanently delete it."""

    return bool(user and challenge.creator_user_id == getattr(user, "id", None))


def delete_challenge(challenge: Challenge, user) -> None:
    """Permanently delete a challenge and all challenge-specific records."""

    if not can_delete_challenge(user, challenge):
        raise PermissionError("Only the challenge creator can delete this challenge.")

    try:
        # Explicit ordering also works when database-level cascades are disabled.
        ChallengePick.query.filter_by(challenge_id=challenge.id).delete(
            synchronize_session=False
        )
        ChallengeGame.query.filter_by(challenge_id=challenge.id).delete(
            synchronize_session=False
        )
        ChallengeParticipant.query.filter_by(challenge_id=challenge.id).delete(
            synchronize_session=False
        )
        # Detail loading populated these collections. Expire them so the parent
        # delete does not attempt to remove already-deleted child rows again.
        db.session.expire(challenge, ["picks", "challenge_games", "participants"])
        db.session.delete(challenge)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
