# Football_Project/services/dashboard.py
"""Data for the user dashboard (pick status, standing, latest recap, season stats)."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from flask import session
from flask_login import current_user

from ..extensions import db
from ..models import Game, Pick, User, WeeklyRecap
from ..time_utils import MT, ensure_dt_mt
from .leaderboard import get_season_leaderboard
from .recap import assign_ranks, get_recap, is_final_status, points_left_on_table, recap_weeks


RANK_HISTORY_WEEKS = 5
LEADERBOARD_SIZE = 5


def effective_user_id() -> int:
    """The user whose data is shown: the viewed user in admin view-as mode, else the current user."""
    if getattr(current_user, "is_admin", False):
        view_id = session.get("view_as_user_id") or session.get("admin_view_as_user_id")
        if view_id:
            try:
                return int(view_id)
            except (TypeError, ValueError):
                pass
    return int(current_user.id)


def format_countdown(delta: timedelta) -> str:
    secs = max(0, int(delta.total_seconds()))
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _kickoff(game):
    return ensure_dt_mt(game.commence_time_mt)


def pick_status(user_id, group_id, season_year, season_type, week, now=None):
    now = now or datetime.now(timezone.utc)
    games = (
        Game.query
        .filter_by(season_year=season_year, season_type=season_type, week=week)
        .all()
    )
    picks = {
        p.game_id: p
        for p in Pick.query.filter(
            Pick.user_id == user_id,
            Pick.group_id == group_id,
            Pick.game_id.in_([g.id for g in games] or [-1]),
        ).all()
    }

    total = len(games)
    picked = sum(1 for g in games if picks.get(g.id) and picks[g.id].team_picked)
    started = [g for g in games if _kickoff(g) and _kickoff(g) <= now]
    open_games = sorted((g for g in games if _kickoff(g) and _kickoff(g) > now), key=_kickoff)
    unpicked_open = [g for g in open_games if not (picks.get(g.id) and picks[g.id].team_picked)]
    final = sum(1 for g in games if is_final_status(g.status))

    if total and final == total:
        mode = "complete"
    elif started:
        mode = "live"
    else:
        mode = "open"

    next_lock = _kickoff(open_games[0]) if open_games else None
    return {
        "mode": mode,
        "week": week,
        "total": total,
        "picked": picked,
        "remaining": total - picked,
        "unpicked_open": len(unpicked_open),
        "pct": round(picked / total * 100) if total else 0,
        "final": final,
        "started": len(started),
        "first_started": bool(started),
        "next_lock": next_lock,
        "next_lock_label": next_lock.astimezone(MT).strftime("%A %-I:%M %p") if next_lock else None,
        "next_lock_iso": next_lock.isoformat() if next_lock else None,
        "countdown": format_countdown(next_lock - now) if next_lock else None,
        "week_points": sum(int(p.points_earned or 0) for p in picks.values()),
    }


def _ranked_season_rows(current_week, season_year, season_type, group_id):
    """Season leaderboard rows re-ranked so equal points + correct picks share a rank."""
    _, rows = get_season_leaderboard(current_week, season_year, season_type, group_id)

    def key(r):
        diff = r.get("tiebreaker_diff")
        return (-r["total_points"], -r["total_correct"], diff if diff is not None else float("inf"))

    return assign_ranks(rows, key)


def _season_stats(user_id, group_id, season_year, season_type):
    rows = (
        db.session.query(
            Game.week, Game.status, Pick.team_picked, Pick.confidence, Pick.points_earned,
        )
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Pick.user_id == user_id,
            Pick.group_id == group_id,
            Game.season_year == season_year,
            Game.season_type == season_type,
        )
        .all()
    )

    week_status = defaultdict(list)
    for (w, s) in (
        db.session.query(Game.week, Game.status)
        .filter(Game.season_year == season_year, Game.season_type == season_type, Game.week.isnot(None))
        .all()
    ):
        week_status[w].append(s)
    complete_weeks = {w for w, ss in week_status.items() if all(is_final_status(s) for s in ss)}

    by_week = defaultdict(list)
    made = correct = 0
    for r in rows:
        if not is_final_status(r.status):
            continue
        if r.team_picked:
            made += 1
            if (r.points_earned or 0) > 0:
                correct += 1
        if r.week in complete_weeks:
            by_week[r.week].append({
                "team_picked": r.team_picked,
                "confidence": r.confidence,
                "points_earned": r.points_earned,
            })

    weekly_points = {w: sum(int(p["points_earned"] or 0) for p in by_week.get(w, [])) for w in complete_weeks}
    # Average only over completed weeks the player took part in (or all completed weeks if none yet)
    played = [w for w in complete_weeks if by_week.get(w)]
    best_week = max(played, key=lambda w: (weekly_points[w], -w), default=None)

    return {
        "accuracy": round(correct / made * 100) if made else None,
        "avg_points": round(sum(weekly_points[w] for w in played) / len(played), 1) if played else None,
        "best_week": best_week,
        "best_week_points": weekly_points[best_week] if best_week is not None else None,
        "left_on_table": sum(points_left_on_table(by_week[w]) for w in played),
        "weeks_counted": len(played),
    }


def build_dashboard(user_id, group_id, settings, now=None):
    season_year, season_type = settings.season_year, settings.season_type
    week = settings.current_week
    user = db.session.get(User, user_id)
    first_name = ((user.full_name or "").strip().split(" ")[0] if user else "") or (user.username if user else "")

    ctx = {
        "user_id": user_id,
        "first_name": first_name,
        "week": week,
        "season_year": season_year,
        "season_type": season_type,
        "group_id": group_id,
    }
    if not group_id:
        return ctx

    ctx["picks"] = pick_status(user_id, group_id, season_year, season_type, week, now=now)

    # --- standing + mini leaderboard
    rows = _ranked_season_rows(week, season_year, season_type, group_id)
    me = next((r for r in rows if r["user_id"] == user_id), None)
    leader_pts = rows[0]["total_points"] if rows else 0
    standing = None
    if me:
        second = next((r for r in rows if r["user_id"] != user_id), None)
        standing = {
            "rank": me["rank"],
            "players": len(rows),
            "points": me["total_points"],
            "behind": leader_pts - me["total_points"],
            "ahead_of_next": (me["total_points"] - second["total_points"]) if second and me["rank"] == 1 else None,
        }
    board = rows[:LEADERBOARD_SIZE]
    ctx["standing"] = standing
    ctx["board"] = board
    ctx["board_me"] = me if me and me not in board else None

    # --- rank by week (from stored recaps)
    recaps = (
        WeeklyRecap.query
        .filter_by(group_id=group_id, season_year=season_year, season_type=season_type)
        .order_by(WeeklyRecap.week.desc())
        .limit(RANK_HISTORY_WEEKS)
        .all()
    )
    history = []
    for rc in reversed(recaps):
        mine = next((s for s in rc.data.get("scores", []) if s["user_id"] == user_id), None)
        if mine:
            n = max(1, rc.data.get("participants") or 1)
            history.append({
                "week": rc.week,
                "rank": mine["season_rank"],
                "height": round(100 * (n - mine["season_rank"] + 1) / n),
            })
    ctx["rank_history"] = history

    # --- latest recap card
    latest = None
    for w in reversed(recap_weeks(group_id, season_year, season_type)):
        latest = get_recap(group_id, season_year, season_type, w)
        if latest:
            break
    if latest:
        mine = next((s for s in latest.data["scores"] if s["user_id"] == user_id), None)
        ctx["recap"] = {
            "week": latest.week,
            "headline": latest.headline,
            "me": mine,
            # the most recently completed week is "new"
            "is_new": latest.week >= week - 1,
        }
    else:
        ctx["recap"] = None

    ctx["stats"] = _season_stats(user_id, group_id, season_year, season_type)
    return ctx
