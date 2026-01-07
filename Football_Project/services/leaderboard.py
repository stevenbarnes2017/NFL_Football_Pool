# Football_Project/services/leaderboard.py

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func, case, literal, and_
from flask import current_app
from sqlalchemy.sql import true

from ..extensions import db
from ..models import User, Pick, Game


# ----------------------------- helpers ---------------------------------------

def _now_mt():
    # single source of truth for "now" in Mountain time
    return datetime.now(ZoneInfo("US/Mountain"))

def _locked_q_base():
    """
    Base query for LOCKED games using ONLY kickoff time:
      Game.commence_time_mt <= now (US/Mountain)
    """
    return db.session.query(Game.id, Game.week).filter(Game.commence_time_mt <= _now_mt())


# ----------------------------- SEASON ----------------------------------------

def _season_user_rows(current_week: int, season_year: int, season_type: str):
    """
    Season totals = sum of weekly metrics (using the weekly logic).

    Users who have never picked IN THIS SEASON/TYPE -> start at current_week
    (so they aren't penalized for earlier weeks in this season/type).

    IMPORTANT: Everything is scoped to (season_year, season_type) via Game.
    """
    # Seed all users so folks with 0 picks still appear
    users = db.session.query(User.id, User.username).all()
    agg = {
        u.id: {
            "user_id": u.id,
            "username": u.username,
            "total_points": 0,
            "total_correct": 0,
            "total_forfeits": 0,
            "picks_made": 0,
            "best_week_points": 0,
            "last_week_points": 0,
        }
        for u in users
    }

    # Per-user start week (first time they picked IN THIS season/type)
    user_start_week = dict(
        db.session.query(Pick.user_id, func.min(Pick.week))
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
        )
        .group_by(Pick.user_id)
        .all()
    )

    # Users with no picks yet start at current week (only count from now)
    for uid in agg.keys():
        if uid not in user_start_week or user_start_week[uid] is None:
            user_start_week[uid] = current_week

    # Only aggregate weeks that actually have locked games (IN THIS season/type)
    now_mt = datetime.now(ZoneInfo("US/Mountain"))
    weeks_with_locked = [
        w for (w,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type,
                Game.week <= current_week,
                Game.commence_time_mt <= now_mt,
            )
            .distinct()
            .order_by(Game.week)
            .all()
        )
    ]

    # Sum weekly rows, but only for users whose start_week <= week
    for w in weeks_with_locked:
        weekly_rows = _weekly_user_rows(w, season_year, season_type)
        for r in weekly_rows:
            if w < user_start_week.get(r["user_id"], current_week):
                continue  # don't penalize weeks before this user started (in this season/type)

            a = agg[r["user_id"]]
            pts = int(r["points"] or 0)
            corr = int(r["correct"] or 0)
            ffs = int(r["forfeits"] or 0)
            pm  = int(r.get("picks_made", 0) or 0)

            a["total_points"]   += pts
            a["total_correct"]  += corr
            a["total_forfeits"] += ffs
            a["picks_made"]     += pm

            if pts > a["best_week_points"]:
                a["best_week_points"] = pts

            # keep your existing "last week" behavior
            if w == current_week - 1:
                a["last_week_points"] = pts

    # Finalize rows
    rows = []
    for a in agg.values():
        picks_made = a["picks_made"]
        correct = a["total_correct"]
        accuracy = (correct / picks_made) * 100 if picks_made else 0.0
        rows.append({
            "user_id": a["user_id"],
            "username": a["username"],
            "total_points": int(a["total_points"]),
            "total_correct": int(a["total_correct"]),
            "total_forfeits": int(max(0, a["total_forfeits"])),
            "accuracy": round(accuracy, 1),
            "best_week_points": int(a["best_week_points"]),
            "last_week_points": int(a["last_week_points"]),
        })
    return rows


# ----------------------------- WEEKLY ----------------------------------------

def _weekly_user_rows(week: int, season_year: int, season_type: str):
    """
    Per-user metrics for a single week.

    Forfeits = (# locked games this week) - (# valid picks with confidence for those locked games)

    IMPORTANT: Everything here is scoped to (season_year, season_type, week) via Game.
    """
    now_mt = datetime.now(ZoneInfo("US/Mountain"))

    # Eligible games for THIS season/type/week (prevents cross-season bleed)
    eligible_games = (
        db.session.query(Game.id.label("gid"))
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week == week,
        )
        .subquery()
    )

    # Locked games for this week (kickoff passed) — scoped to eligible games
    locked_games = (
        db.session.query(Game.id.label("gid"))
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week == week,
            Game.commence_time_mt <= now_mt,
        )
        .subquery()
    )
    locked_count = db.session.query(func.count(locked_games.c.gid)).scalar() or 0

    # User list & points for the week:
    # ONLY count picks that belong to eligible games for this season/type/week.
    points_block = (
        db.session.query(
            User.id.label("user_id"),
            User.username.label("username"),
            func.coalesce(func.sum(Pick.points_earned), 0).label("points"),
            func.coalesce(func.sum(case((Pick.points_earned > 0, 1), else_=0)), 0).label("correct"),
            func.coalesce(func.count(Pick.id), 0).label("picks_made"),
        )
        .outerjoin(
            Pick,
            (Pick.user_id == User.id)
            & (Pick.week == week)
            & (Pick.game_id.in_(db.session.query(eligible_games.c.gid)))
        )
        .group_by(User.id)
        .subquery()
    )

    # Valid picks among LOCKED games (confidence not null)
    valid_picks = (
        db.session.query(
            Pick.user_id.label("user_id"),
            func.count(Pick.id).label("valid_picks"),
        )
        .join(locked_games, locked_games.c.gid == Pick.game_id)
        .filter(Pick.week == week, Pick.confidence.isnot(None))
        .group_by(Pick.user_id)
        .subquery()
    )

    rows = (
        db.session.query(
            points_block.c.user_id,
            points_block.c.username,
            points_block.c.points,
            points_block.c.correct,
            points_block.c.picks_made,
            (literal(locked_count) - func.coalesce(valid_picks.c.valid_picks, 0)).label("forfeits"),
        )
        .outerjoin(valid_picks, valid_picks.c.user_id == points_block.c.user_id)
        .all()
    )

    res = []
    for r in rows:
        picks_made = int(r.picks_made or 0)
        correct = int(r.correct or 0)
        accuracy = (correct / picks_made) * 100 if picks_made else 0.0
        res.append({
            "user_id": r.user_id,
            "username": r.username,
            "points": int(r.points or 0),
            "correct": correct,
            "forfeits": max(0, int(r.forfeits or 0)),
            "picks_made": picks_made,
            "accuracy": round(accuracy, 1),
            "tiebreak_note": None,
        })
    return res

def _apply_season_tiebreak(r):
    """
    Sort key for season leaderboard.
    Higher points/correct/best_week rank first; fewer forfeits rank higher; 
    username ASC as final stable key.
    """
    return (
        -int(r.get("total_points", 0)),
        -int(r.get("total_correct", 0)),
        int(r.get("total_forfeits", 0)),
        -int(r.get("best_week_points", 0)),
        str(r.get("username", "")).lower(),
    )

def _apply_weekly_tiebreak(r):
    # 1) Points DESC
    # 2) Correct DESC
    # 3) Fewest Forfeits ASC
    # 4) Username ASC
    return (-r["points"], -r["correct"], r["forfeits"], r["username"].lower())


# ----------------------------- Public API ------------------------------------

def get_season_leaderboard(current_week: int, season_year: int, season_type: str):
    rows = _season_user_rows(current_week, season_year, season_type)
    rows.sort(key=_apply_season_tiebreak)

    # dense rank
    rank, last_key = 0, None
    for r in rows:
        key = _apply_season_tiebreak(r)
        if key != last_key:
            rank += 1
            last_key = key
        r["rank"] = rank

    total_participants = len(rows)
    avg_points = round(sum(r["total_points"] for r in rows) / total_participants, 1) if total_participants else 0.0
    header = {
        "through_week": current_week,
        "participants": total_participants,
        "avg_points": avg_points,
        "season_year": season_year,
        "season_type": season_type,
    }
    return header, rows


def get_weekly_leaderboard(week: int, season_year: int, season_type: str):
    rows = _weekly_user_rows(week, season_year, season_type)
    rows.sort(key=_apply_weekly_tiebreak)

    # Dense ranks with ties
    rank, last_key = 0, None
    for r in rows:
        key = _apply_weekly_tiebreak(r)
        if key != last_key:
            rank += 1
            last_key = key
        r["rank"] = rank

    champions = {r["user_id"] for r in rows if r["rank"] == 1}
    header = {
        "week": week,
        "champion_user_ids": champions,
        "season_year": season_year,
        "season_type": season_type,
    }
    return header, rows

