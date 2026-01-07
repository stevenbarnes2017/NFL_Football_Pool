from flask import session
from flask_login import current_user

def get_effective_user_id() -> int:
    view_id = session.get("admin_view_as_user_id")
    if current_user.is_admin and view_id:
        return int(view_id)
    return int(current_user.id)