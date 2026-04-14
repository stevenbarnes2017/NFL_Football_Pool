from flask import session
from flask_login import current_user
from Football_Project.models import PoolGroup, GroupMember


def get_active_group_id():
    # 1. Session override
    group_id = session.get("active_group_id")
    if group_id:
        return group_id

    # 2. First active membership
    if getattr(current_user, "is_authenticated", False):
        membership = (
            GroupMember.query
            .filter_by(user_id=current_user.id, is_active=True)
            .order_by(GroupMember.id.asc())
            .first()
        )
        if membership:
            session["active_group_id"] = membership.group_id
            return membership.group_id

    # 3. Fallback to default group
    default_group = PoolGroup.query.filter_by(
        slug="main-pool",
        is_active=True
    ).first()

    if default_group:
        session["active_group_id"] = default_group.id
        return default_group.id

    return None