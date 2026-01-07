from datetime import datetime

from sqlalchemy import func

from ..extensions import db
from ..models import Game, Settings


# services/season.py
def get_current_season_context():
    """
    Returns (season_year, season_type) from the Settings row.
    Falls back to (current year, 'REG') if missing.
    """
    s = Settings.query.first()

    if not s:
        # safe fallback so app doesn't crash
        return datetime.utcnow().year, "REG"

    return int(s.season_year), s.season_type

def apply_season_filter(query, model, season_year, season_type):
    """
    Enforces current season + type on a query
    """
    return query.filter(
        model.season_year == season_year,
        model.season_type == season_type
    )

def get_current_week(season_year, season_type):
    """
    Returns the active week number for the season
    """
    return (
        db.session.query(func.max(Game.week))
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.status != "completed"
        )
        .scalar()
    )


def picks_locked(game):
    """
    Returns True if picks should be locked for this game
    """
    return datetime.utcnow() >= game.kickoff
