# services/odds_core.py
from __future__ import annotations

import io
import csv
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple, Optional

from flask import current_app
from ..extensions import db
from ..models import Game
from Football_Project.services.season import get_current_week
from ..get_the_odds import get_nfl_spreads  # provider fetcher (keep your existing function)

# ------------------------------ Utilities ------------------------------------

def _norm_team(name: str | None) -> str:
    """Normalize team names for matching (lowercase, alnum only)."""
    if not name:
        return ""
    return re.sub(r"[^a-z0-9]+", "", str(name).lower())

def _pair_key(home: str | None, away: str | None) -> frozenset[str]:
    """Order-insensitive key from two team names."""
    return frozenset({_norm_team(home), _norm_team(away)})

def _parse_provider_kickoff(g: Dict[str, Any]) -> Optional[datetime]:
    """
    Try common kickoff fields; accept ISO8601 strings or epoch seconds.
    Return tz-aware UTC datetime if possible.
    """
    candidates = [
        "commence_time_utc", "commence_time",
        "kickoff_time_utc", "kickoff_time",
        "start_time_utc", "start_time",
    ]
    val = None
    for k in candidates:
        if g.get(k) is not None:
            val = g[k]
            break
    if val is None:
        return None

    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(float(val), tz=timezone.utc)

    try:
        dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def _kickoff_utc_from_game(game: Game) -> Optional[datetime]:
    """Convert your stored kickoff (commence_time_mt) to UTC if present."""
    dt = getattr(game, "commence_time_mt", None)
    if not dt:
        return None
    try:
        return dt if dt.tzinfo and dt.tzinfo.utcoffset(dt) is not None else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None

def _to_csv_bytes(rows: List[Dict[str, Any]]) -> bytes:
    """Portable CSV for email attachment/diagnostics."""
    if not rows:
        return b""
    fieldnames = sorted({k for r in rows for k in r.keys()})
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fieldnames})
    return out.getvalue().encode("utf-8")

# ------------------------------ Public helpers -------------------------------

def is_week_odds_complete(week: int, season_year: int, season_type: str) -> bool:
    """
    Treat 'complete' as: every Game for the week has a non-null spread AND favorite_team
    for the CURRENT season_year/season_type.
    """
    q = Game.query.filter(
        Game.week == week,
        Game.season_year == season_year,
        Game.season_type == season_type,
    )

    total = q.count()
    if total == 0:
        return False

    ready = q.filter(
        Game.spread.isnot(None),
        Game.favorite_team.isnot(None),
    ).count()

    return ready == total

def games_count_for_week(week: int, season_year: int, season_type: str) -> int:
    return Game.query.filter(
        Game.week == week,
        Game.season_year == season_year,
        Game.season_type == season_type,
    ).count()

def to_csv_bytes(games_list: List[Dict[str, Any]]) -> bytes:
    """CSV compatible with your existing columns."""
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["game_id", "home_team", "away_team", "favorite_team", "spread"])
    for g in games_list:
        w.writerow([
            g.get("game_id"),
            g.get("home_team"),
            g.get("away_team"),
            g.get("favorite_team"),
            g.get("spread"),
        ])
    return out.getvalue().encode("utf-8")

# ------------------------------ Matching logic -------------------------------

def _resolve_matches_by_team_time(
    week: int,
    provider_games: List[Dict[str, Any]],
    season_year: int,
    season_type: str,
    time_tolerance: timedelta = timedelta(hours=12),
) -> Tuple[Dict[int, int], Dict[str, Any]]:
    """
    Resolve provider games -> DB Game.id using (home, away) teams plus nearest kickoff time (if available).
    Scoped to (season_year, season_type, week).
    """
    db_games = Game.query.filter(
        Game.week == week,
        Game.season_year == season_year,
        Game.season_type == season_type,
    ).all()

    db_by_pair: Dict[frozenset[str], List[Game]] = {}
    for g in db_games:
        db_by_pair.setdefault(_pair_key(g.home_team, g.away_team), []).append(g)

    mapping: Dict[int, int] = {}
    unmatched: List[Dict[str, Any]] = []
    ambiguous: List[Dict[str, Any]] = []

    for i, pg in enumerate(provider_games):
        pkey = _pair_key(pg.get("home_team"), pg.get("away_team"))
        candidates = db_by_pair.get(pkey, [])

        if not candidates:
            unmatched.append({
                "index": i,
                "home": pg.get("home_team"),
                "away": pg.get("away_team"),
                "reason": "no_team_pair_match",
            })
            continue

        p_time = _parse_provider_kickoff(pg)

        if len(candidates) == 1:
            mapping[i] = candidates[0].id
            continue

        if p_time:
            scored = []
            for g in candidates:
                g_time = _kickoff_utc_from_game(g)
                if g_time:
                    scored.append((abs((p_time - g_time).total_seconds()), g))
            if scored:
                scored.sort(key=lambda t: t[0])
                best_delta, best_game = scored[0]
                if best_delta <= time_tolerance.total_seconds():
                    mapping[i] = best_game.id
                else:
                    ambiguous.append({
                        "index": i,
                        "home": pg.get("home_team"),
                        "away": pg.get("away_team"),
                        "reason": "closest_time_outside_tolerance",
                        "closest_diff_seconds": best_delta,
                    })
                continue

        ambiguous.append({
            "index": i,
            "home": pg.get("home_team"),
            "away": pg.get("away_team"),
            "reason": "multiple_team_pair_matches_no_time",
        })

    diag = {
        "season_year": season_year,
        "season_type": season_type,
        "week": week,
        "unmatched_count": len(unmatched),
        "ambiguous_count": len(ambiguous),
        "unmatched": unmatched,
        "ambiguous": ambiguous,
    }
    return mapping, diag


def _save_spreads_resolved_to_db(
    week: int,
    provider_games: List[Dict[str, Any]],
    mapping: Dict[int, int],
    season_year: int,
    season_type: str,
) -> None:
    """
    Update resolved DB games with spread/favorite and bump saved_at.
    Scoped to (season_year, season_type, week) for safety.
    """
    def pick_key(d: Dict[str, Any], keys: Tuple[str, ...]):
        for k in keys:
            if k in d and d[k] is not None:
                return d[k]
        return None

    spread_keys = ("spread", "line", "current_spread", "point_spread")
    fav_keys = ("favorite_team", "favorite", "fav")

    ids = list(mapping.values())

    # Extra safety: only allow updating games in the current season/type/week
    db_games = {
        g.id: g for g in Game.query.filter(
            Game.id.in_(ids),
            Game.week == week,
            Game.season_year == season_year,
            Game.season_type == season_type,
        ).all()
    }

    updated = 0

    for i, pg in enumerate(provider_games):
        db_id = mapping.get(i)
        if not db_id:
            continue
        g = db_games.get(db_id)
        if not g:
            continue

        spread = pick_key(pg, spread_keys)
        favorite = pick_key(pg, fav_keys)

        if spread is not None:
            try:
                g.spread = float(spread)
            except Exception:
                pass

        if favorite:
            g.favorite_team = str(favorite)

        g.saved_at = datetime.utcnow()
        db.session.add(g)
        updated += 1

    db.session.commit()

# ------------------------------ Orchestrator ---------------------------------

from datetime import timedelta
from flask import current_app

def attempt_import_odds(week: int, season_year: int, season_type: str):
    """
    Fetch spreads and merge them by (teams + kickoff time) rather than provider IDs.
    Scoped to current (season_year, season_type).

    Returns (status, csv_bytes or None, details dict)
      status ∈ {"success","not_ready","error"}
    """
    wk = week

    try:
        provider_games, _count = get_nfl_spreads()
    except Exception as e:
        return ("error", None, {"season_year": season_year, "season_type": season_type, "week": wk, "error": str(e)})

    if not provider_games:
        return ("not_ready", None, {"season_year": season_year, "season_type": season_type, "week": wk, "reason": "provider_empty"})

    expected = games_count_for_week(wk, season_year, season_type)
    if expected == 0:
        return ("not_ready", None, {"season_year": season_year, "season_type": season_type, "week": wk, "reason": "no_games_in_db"})

    # If the provider returns fewer than expected, consider not ready yet
    if len(provider_games) < expected:
        return ("not_ready", None, {
            "season_year": season_year,
            "season_type": season_type,
            "week": wk,
            "expected": expected,
            "received": len(provider_games),
            "reason": "count_mismatch"
        })

    # IMPORTANT: resolve matches only against games in this season/type/week
    mapping, diag = _resolve_matches_by_team_time(
        wk,
        provider_games,
        season_year=season_year,
        season_type=season_type,
        time_tolerance=timedelta(hours=12)
    )

    if len(mapping) < expected:
        details = {
            "season_year": season_year,
            "season_type": season_type,
            "week": wk,
            "expected": expected,
            "received": len(provider_games),
            "matched": len(mapping),
            **diag
        }
        try:
            current_app.logger.info(f"[odds] NOT_READY {details}")
        except Exception:
            pass
        return ("not_ready", None, details)

    # Save resolved odds into existing Game rows (scoped)
    try:
        _save_spreads_resolved_to_db(
            wk,
            provider_games,
            mapping,
            season_year=season_year,
            season_type=season_type
        )

        csv_bytes = _to_csv_bytes(provider_games)
        details = {
            "season_year": season_year,
            "season_type": season_type,
            "week": wk,
            "expected": expected,
            "received": len(provider_games),
            "matched": len(mapping)
        }
        try:
            current_app.logger.info(f"[odds] SUCCESS {details}")
        except Exception:
            pass
        return ("success", csv_bytes, details)
    except Exception as e:
        return ("error", None, {
            "season_year": season_year,
            "season_type": season_type,
            "week": wk,
            "error": f"save_failed: {e}"
        })
