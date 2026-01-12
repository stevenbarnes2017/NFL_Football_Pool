# Football_Project/services/leaderboard.py

from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

from sqlalchemy import func, case, literal
from ..extensions import db
from ..models import User, Pick, Game


# ----------------------------- helpers ---------------------------------------

def _now_mt():
    return datetime.now(ZoneInfo("America/Denver"))

def _norm_status(s: str | None) -> str:
    return (s or "").strip().upper()

def _is_final_status(s: str | None) -> bool:
    # ESPN commonly uses "STATUS_FINAL" in your DB, but be tolerant.
    ss = _norm_status(s)
    return ss in {"STATUS_FINAL", "FINAL", "STATUS_GAME_OVER"}

def _final_games_subq(season_year: int, season_type: str, week: int):
    """Subquery of FINAL game ids for this season/type/week."""
    return (
        db.session.query(Game.id.label("gid"))
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week == week,
            Game.status.isnot(None),
        )
        .filter(
            # can't call python function inside SQL; use SQL-friendly comparison
            func.upper(func.trim(Game.status)).in_(["STATUS_FINAL", "FINAL", "STATUS_GAME_OVER"])
        )
        .subquery()
    )

def _eligible_games_subq(season_year: int, season_type: str, week: int):
    """Subquery of ALL game ids for this season/type/week."""
    return (
        db.session.query(Game.id.label("gid"))
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week == week,
        )
        .subquery()
    )

def _weeks_with_finals(season_year: int, season_type: str, through_week: int):
    """Weeks that have at least one FINAL game (season/type scoped)."""
    weeks = [
        w for (w,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type,
                Game.week <= through_week,
            )
            .filter(func.upper(func.trim(Game.status)).in_(["STATUS_FINAL", "FINAL", "STATUS_GAME_OVER"]))
            .distinct()
            .order_by(Game.week)
            .all()
        )
    ]
    return weeks


# ----------------------------- WEEKLY ----------------------------------------

def _weekly_user_rows(week: int, season_year: int, season_type: str):
    """
    Weekly leaderboard:
      - points = sum(Pick.points_earned) for picks in this season/type/week
      - correct = count of picks with points_earned > 0 (same scope)
      - forfeits = (# FINAL games this week) - (# picks with confidence among FINAL games)
    """

    eligible_games = _eligible_games_subq(season_year, season_type, week)
    final_games = _final_games_subq(season_year, season_type, week)

    final_count = db.session.query(func.count(final_games.c.gid)).scalar() or 0

    # Points/correct/picks_made — scoped via Pick.game_id in eligible games
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

    # Valid picks among FINAL games = picks that have confidence (not null) for FINAL games
    valid_picks = (
        db.session.query(
            Pick.user_id.label("user_id"),
            func.count(Pick.id).label("valid_picks"),
        )
        .join(final_games, final_games.c.gid == Pick.game_id)
        .filter(
            Pick.week == week,
            Pick.confidence.isnot(None),
        )
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
            (literal(final_count) - func.coalesce(valid_picks.c.valid_picks, 0)).label("forfeits"),
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


# ----------------------------- SEASON ----------------------------------------

def _season_user_rows(current_week: int, season_year: int, season_type: str):
    """
    Season totals = sum of weekly rows for weeks that have FINAL games.
    Users with no picks yet start at current_week (same behavior you had).
    """

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

    for uid in agg.keys():
        if uid not in user_start_week or user_start_week[uid] is None:
            user_start_week[uid] = current_week

    weeks_with_finals = _weeks_with_finals(season_year, season_type, current_week)

    for w in weeks_with_finals:
        weekly_rows = _weekly_user_rows(w, season_year, season_type)
        for r in weekly_rows:
            if w < user_start_week.get(r["user_id"], current_week):
                continue

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

            if w == current_week - 1:
                a["last_week_points"] = pts

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


# ----------------------------- ranking ---------------------------------------

def _apply_season_tiebreak(r):
    return (
        -int(r.get("total_points", 0)),
        -int(r.get("total_correct", 0)),
        int(r.get("total_forfeits", 0)),
        -int(r.get("best_week_points", 0)),
        str(r.get("username", "")).lower(),
    )

def _apply_weekly_tiebreak(r):
    return (-r["points"], -r["correct"], r["forfeits"], r["username"].lower())


# ----------------------------- Public API ------------------------------------

def get_season_leaderboard(current_week: int, season_year: int, season_type: str):
    rows = _season_user_rows(current_week, season_year, season_type)
    rows.sort(key=_apply_season_tiebreak)

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
