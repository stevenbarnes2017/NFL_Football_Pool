# Football_Project/services/__init__.py
from .odds_care import attempt_import_odds, is_week_odds_complete
from .email_helpers import send_admin_email

__all__ = [
    "attempt_import_odds",
    "is_week_odds_complete",
    "send_admin_email",
]
