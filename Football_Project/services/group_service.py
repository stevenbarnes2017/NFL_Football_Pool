from flask import session
from flask_login import current_user
from Football_Project.models import PoolGroup, GroupMember


from flask import session
from flask_login import current_user

def get_active_group_id():
    if not getattr(current_user, "is_authenticated", False):
        return None

    # 1. Validate session group
    group_id = session.get("active_group_id")
    if group_id:
        membership = GroupMember.query.filter_by(
            user_id=current_user.id,
            group_id=group_id,
            is_active=True,
        ).first()

        if membership:
            return group_id
        else:
            # session is stale or invalid
            session.pop("active_group_id", None)

    # 2. Pick first valid membership
    membership = (
        GroupMember.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(GroupMember.id.asc())
        .first()
    )

    if membership:
        session["active_group_id"] = membership.group_id
        return membership.group_id

    # 3. No groups → return None (no default fallback)
    return None