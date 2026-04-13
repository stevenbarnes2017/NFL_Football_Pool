# services/schedule_service.py
import requests
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional

from Football_Project.extensions import db
from Football_Project.models import Game

MT = ZoneInfo("America/Denver")
TOLERANCE = timedelta(minutes=1)


def season_type_label(season_type: int) -> str:
    # If your DB stores season_type as a string like "REG"/"POST"
    return {1: "PRE", 2: "REG", 3: "POST"}.get(season_type, "REG")


def _espn_iso_to_mt(iso_str: str) -> datetime:
    if not iso_str:
        raise ValueError("missing kickoff date")

    s = iso_str.replace("Z", "+00:00")
    dt_utc = datetime.fromisoformat(s)
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    return dt_utc.astimezone(MT)


def generate_game_id(season_year: int, season_type: int, week: int, event_id: str) -> str:
    return f"{season_year}-S{season_type}-W{week}-E{event_id}"


def fetch_games_by_week(season_year: int, season_type: int, week: int) -> List[Dict]:
    url = (
        "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        f"?seasontype={season_type}&year={season_year}&week={week}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    games: List[Dict] = []
    for event in data.get("events", []):
        try:
            event_id = str(event.get("id") or "")
            if not event_id:
                continue

            comp = event["competitions"][0]
            competitors = comp["competitors"]

            home = next(c for c in competitors if c.get("homeAway") == "home")
            away = next(c for c in competitors if c.get("homeAway") == "away")

            kickoff_mt = _espn_iso_to_mt(event.get("date") or comp.get("date"))

            games.append(
                {
                    "game_id": generate_game_id(season_year, season_type, week, event_id),
                    "season_year": season_year,
                    "season_type": season_type_label(season_type),  # if int column, use season_type
                    "week": week,
                    "week_label": None,  # safe even if you don't use it
                    "home_team": home["team"]["displayName"],
                    "away_team": away["team"]["displayName"],
                    "commence_time_mt": kickoff_mt,
                }
            )
        except Exception:
            # don't fail the whole week for one malformed event
            continue

    return games


def _normalize_for_compare(old_dt: Optional[datetime], new_dt: datetime) -> tuple[Optional[datetime], datetime]:
    """
    Prevent endless updates if one side is tz-aware and the other isn't.
    Since your DB column is timezone=True, we prefer tz-aware.
    """
    if old_dt is None:
        return None, new_dt

    # If DB returned naive but new is aware, compare naive-to-naive
    if old_dt.tzinfo is None and new_dt.tzinfo is not None:
        return old_dt, new_dt.replace(tzinfo=None)

    # If DB returned aware but new is naive, compare naive-to-naive
    if old_dt.tzinfo is not None and new_dt.tzinfo is None:
        return old_dt.replace(tzinfo=None), new_dt

    return old_dt, new_dt


def update_schedule(
    season_year: int,
    season_type: int,
    week_start: int = 1,
    week_end: int = 18,
) -> Dict[str, int]:
    """
    Upsert schedule into Game table from ESPN.
    Safe to run multiple times.
    """

    inserted = 0
    updated = 0
    unchanged = 0
    failed_weeks = 0

    st_label = season_type_label(season_type)

    print(
        f"[SCHEDULE] Start update — "
        f"Season {season_year} {st_label}, weeks {week_start}-{week_end}"
    )

    for week in range(week_start, week_end + 1):
        try:
            games = fetch_games_by_week(season_year, season_type, week)

            if not games:
                print(f"[SCHEDULE] Week {week}: no games returned")
                continue

            wk_inserted = 0
            wk_updated = 0
            wk_unchanged = 0

            for g in games:
                row = Game.query.filter_by(game_id=g["game_id"]).first()

                if row:
                    changed = False

                    if row.season_year != g["season_year"]:
                        row.season_year = g["season_year"]
                        changed = True
                    if row.season_type != g["season_type"]:
                        row.season_type = g["season_type"]
                        changed = True
                    if row.week != g["week"]:
                        row.week = g["week"]
                        changed = True
                    if row.week_label != g.get("week_label"):
                        row.week_label = g.get("week_label")
                        changed = True
                    if row.home_team != g["home_team"]:
                        row.home_team = g["home_team"]
                        changed = True
                    if row.away_team != g["away_team"]:
                        row.away_team = g["away_team"]
                        changed = True

                    old = row.commence_time_mt
                    new = g["commence_time_mt"]
                    old_cmp, new_cmp = _normalize_for_compare(old, new)

                    if old_cmp is None or abs(new_cmp - old_cmp) > TOLERANCE:
                        row.commence_time_mt = new
                        changed = True

                    if changed:
                        wk_updated += 1
                    else:
                        wk_unchanged += 1

                else:
                    db.session.add(
                        Game(
                            game_id=g["game_id"],
                            season_year=g["season_year"],
                            season_type=st_label,
                            week=g["week"],
                            week_label=g.get("week_label"),
                            home_team=g["home_team"],
                            away_team=g["away_team"],
                            commence_time_mt=g["commence_time_mt"],
                        )
                    )
                    wk_inserted += 1

            db.session.commit()

            inserted += wk_inserted
            updated += wk_updated
            unchanged += wk_unchanged

            print(
                f"[SCHEDULE] Week {week} done — "
                f"inserted={wk_inserted}, updated={wk_updated}, unchanged={wk_unchanged}"
            )

        except Exception as e:
            db.session.rollback()
            failed_weeks += 1
            print(f"[SCHEDULE] ❌ Week {week} failed: {e}")

    print(
        f"[SCHEDULE] Finished — "
        f"inserted={inserted}, updated={updated}, "
        f"unchanged={unchanged}, failed_weeks={failed_weeks}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "failed_weeks": failed_weeks,
    }
