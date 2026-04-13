from datetime import datetime
from zoneinfo import ZoneInfo
from Football_Project.extensions import db
from Football_Project.models import Settings, Game

MT = ZoneInfo("America/Denver")

def compute_week_from_games(season_year: int, season_type: str) -> int | None:
    now = datetime.now(MT).replace(tzinfo=None)

    # ✅ Use earliest upcoming game as the "current week"
    upcoming = (Game.query
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.commence_time_mt.isnot(None),
            Game.commence_time_mt > now
        )
        .order_by(Game.commence_time_mt.asc())
        .first()
    )
    if upcoming:
        return upcoming.week

    # Fallback: season over, use last game week
    last_game = (Game.query
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.commence_time_mt.isnot(None)
        )
        .order_by(Game.commence_time_mt.desc())
        .first()
    )
    return last_game.week if last_game else None

def sync_settings_current_week():
    s = Settings.query.first()
    if not s:
        return {"updated": False, "reason": "no settings row"}

    new_week = compute_week_from_games(s.season_year, s.season_type)
    if not new_week:
        return {"updated": False, "reason": "could not compute week"}

    if s.current_week != new_week:
        old = s.current_week
        s.current_week = new_week
        db.session.commit()
        return {"updated": True, "old": old, "new": new_week}

    return {"updated": False, "reason": "already correct"}