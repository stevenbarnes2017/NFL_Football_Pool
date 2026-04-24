from flask import session
from flask_login import current_user
from Football_Project.models import PoolGroup, GroupMember


from flask import session
from flask_login import current_user

from flask import session
from flask_login import current_user
from Football_Project.models import GroupMember, PoolGroup


def get_active_group_id():
    group_id = session.get("active_group_id")

    # Anonymous user: don't try to read user attributes like is_admin
    if not getattr(current_user, "is_authenticated", False):
        return group_id

    # Global admin can use any active group
    if getattr(current_user, "is_admin", False):
        if group_id:
            group = PoolGroup.query.filter_by(id=group_id, is_active=True).first()
            if group:
                return group_id

        first_group = (
            PoolGroup.query
            .filter_by(is_active=True)
            .order_by(PoolGroup.name.asc())
            .first()
        )
        if first_group:
            session["active_group_id"] = first_group.id
            return first_group.id

        return None

    # Normal user path
    if group_id:
        membership = GroupMember.query.filter_by(
            user_id=current_user.id,
            group_id=group_id,
            is_active=True,
        ).first()

        if membership:
            return group_id

    first_membership = (
        GroupMember.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(GroupMember.joined_at.asc())
        .first()
    )

    if first_membership:
        session["active_group_id"] = first_membership.group_id
        return first_membership.group_id

    session.pop("active_group_id", None)
    return None