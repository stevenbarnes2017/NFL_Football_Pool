# Football_Project/services/permissions.py

from ..models import GroupMember


def is_global_admin(user):
    print("PERM is_global_admin user.id:", getattr(user, "id", None))
    print("PERM is_global_admin user.is_admin:", getattr(user, "is_admin", None))
    return bool(getattr(user, "is_admin", False))


def is_group_admin(user_id, group_id):
    print("PERM is_group_admin user_id:", user_id)
    print("PERM is_group_admin group_id:", group_id)

    membership = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=group_id,
        is_active=True,
    ).first()

    print("PERM membership:", membership)

    if membership:
        print("PERM membership.user_id:", membership.user_id)
        print("PERM membership.group_id:", membership.group_id)
        print("PERM membership.role:", repr(membership.role))
        print("PERM membership.is_active:", membership.is_active)

    result = bool(membership and (membership.role or "").strip().lower() == "group_admin")
    print("PERM is_group_admin result:", result)
    return result


def can_manage_group(user, group_id):
    print("PERM can_manage_group user.id:", getattr(user, "id", None))
    print("PERM can_manage_group group_id:", group_id)

    result = is_global_admin(user) or is_group_admin(user.id, group_id)
    print("PERM can_manage_group result:", result)
    return result