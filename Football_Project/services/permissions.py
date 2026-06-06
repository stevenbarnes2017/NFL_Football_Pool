# Football_Project/services/permissions.py

import logging

from ..models import GroupMember

logger = logging.getLogger(__name__)


def is_global_admin(user):
    return bool(getattr(user, "is_admin", False))


def is_group_admin(user_id, group_id):
    membership = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=group_id,
        is_active=True,
    ).first()

    result = bool(membership and (membership.role or "").strip().lower() == "group_admin")
    logger.debug("is_group_admin user_id=%s group_id=%s result=%s", user_id, group_id, result)
    return result


def can_manage_group(user, group_id):
    result = is_global_admin(user) or is_group_admin(user.id, group_id)
    logger.debug("can_manage_group user_id=%s group_id=%s result=%s", getattr(user, "id", None), group_id, result)
    return result