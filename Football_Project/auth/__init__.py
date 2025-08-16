# Football_Project/auth/__init__.py
from flask import Blueprint

# Public authentication routes (register, login, logout, reset later)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Import routes so decorators run when the blueprint is registered
from . import routes  # noqa: E402
