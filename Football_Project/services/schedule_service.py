# services/schedule_service.py
import re
import requests
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Any

from Football_Project.extensions import db
from Football_Project.models import Game

MT = ZoneInfo("America/Denver")
TOLERANCE = timedelta(minutes=1)

TEAM_CACHE: dict[str, str] = {}


def season_type_label(season_type: int) -> str:
    return {1: "PRE", 2: "REG", 3: "POST"}.get(season_type, "REG")


def fetch_json(url: str) -> Dict[str, Any]:
    url = url.replace("http://", "https://")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _espn_iso_to_mt(iso_str: str) -> datetime:
    if not iso_str:
        raise ValueError("missing kickoff date")

    s = iso_str.replace("Z", "+00:00")
    dt_utc = datetime.fromisoformat(s)

    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    return dt_utc.astimezone(MT)


def parse_week_from_ref(week_ref: str) -> int:
    match = re.search(r"/weeks/(\d+)", week_ref or "")
    if not match:
        raise ValueError(f"Could not parse week from ref: {week_ref}")
    return int(match.group(1))


def generate_game_id(season_year: int, season_type: int, week: int, event_id: str) -> str:
    return f"{season_year}-S{season_type}-W{week}-E{event_id}"


def get_team_display_name(team_ref: str) -> str:
    team_ref = team_ref.replace("http://", "https://")

    if team_ref in TEAM_CACHE:
        return TEAM_CACHE[team_ref]

    team = fetch_json(team_ref)

    name = (
        team.get("displayName")
        or team.get("name")
        or team.get("shortDisplayName")
        or team.get("abbreviation")
    )

    if not name:
        raise ValueError(f"Could not find team name from {team_ref}")

    TEAM_CACHE[team_ref] = name
    return name


def fetch_games(
    season_year: int,
    season_type: int,
    week_start: int = 1,
    week_end: int = 18,
) -> List[Dict]:
    """
    Fetch schedule from ESPN Core API.

    This is better than the scoreboard endpoint for future schedule loading
    and schedule-change checks.
    """
    url = (
        f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/"
        f"seasons/{season_year}/types/{season_type}/events?limit=1000"
    )

    data = fetch_json(url)
    print(f"[SCHEDULE] ESPN Core returned {data.get('count', 0)} event refs")

    games: List[Dict] = []

    for item in data.get("items", []):
        ref = item.get("$ref")
        if not ref:
            continue

        try:
            event = fetch_json(ref)

            event_id = str(event.get("id") or "")
            if not event_id:
                print("[SCHEDULE] Skipping event with missing id")
                continue

            week = parse_week_from_ref(event.get("week", {}).get("$ref", ""))

            if week < week_start or week > week_end:
                continue

            comp = event["competitions"][0]
            competitors = comp["competitors"]

            home = next(c for c in competitors if c.get("homeAway") == "home")
            away = next(c for c in competitors if c.get("homeAway") == "away")

            home_team = get_team_display_name(home["team"]["$ref"])
            away_team = get_team_display_name(away["team"]["$ref"])

            kickoff_iso = event.get("date") or comp.get("date")
            kickoff_mt = _espn_iso_to_mt(kickoff_iso)

            # Safety check so ESPN stale data does not poison the DB.
            if kickoff_mt.year != season_year:
                print(
                    f"[SCHEDULE] Skipping stale event {event_id}: "
                    f"{away_team} @ {home_team} kickoff={kickoff_mt}"
                )
                continue

            games.append(
                {
                    "game_id": generate_game_id(season_year, season_type, week, event_id),
                    "season_year": season_year,
                    "season_type": season_type_label(season_type),
                    "week": week,
                    "week_label": None,
                    "home_team": home_team,
                    "away_team": away_team,
                    "commence_time_mt": kickoff_mt,
                }
            )

        except Exception as e:
            print(f"[SCHEDULE] Skipping one event due to parse error: {e}")
            continue

    games.sort(key=lambda g: (g["week"], g["commence_time_mt"], g["game_id"]))
    return games


def _normalize_for_compare(
    old_dt: Optional[datetime],
    new_dt: datetime,
) -> tuple[Optional[datetime], datetime]:
    if old_dt is None:
        return None, new_dt

    if old_dt.tzinfo is None and new_dt.tzinfo is not None:
        return old_dt, new_dt.replace(tzinfo=None)

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
    Upsert schedule into Game table from ESPN Core API.
    Safe to run multiple times.
    """

    inserted = 0
    updated = 0
    unchanged = 0
    failed = 0

    st_label = season_type_label(season_type)

    print(
        f"[SCHEDULE] Start update — "
        f"Season {season_year} {st_label}, weeks {week_start}-{week_end}"
    )

    try:
        games = fetch_games(
            season_year=season_year,
            season_type=season_type,
            week_start=week_start,
            week_end=week_end,
        )

        if not games:
            print("[SCHEDULE] No games returned")
            return {
                "inserted": 0,
                "updated": 0,
                "unchanged": 0,
                "failed": 0,
                "failed_weeks": 0,
            }

        weeks = sorted(set(g["week"] for g in games))

        for week in weeks:
            wk_inserted = 0
            wk_updated = 0
            wk_unchanged = 0

            week_games = [g for g in games if g["week"] == week]

            print(f"[SCHEDULE] Week {week}: found {len(week_games)} games")

            for g in week_games:
                row = Game.query.filter_by(game_id=g["game_id"]).first()

                if row:
                    changed = False

                    for field in [
                        "season_year",
                        "season_type",
                        "week",
                        "week_label",
                        "home_team",
                        "away_team",
                    ]:
                        if getattr(row, field, None) != g.get(field):
                            setattr(row, field, g.get(field))
                            changed = True

                    old = row.commence_time_mt
                    new = g["commence_time_mt"]
                    old_cmp, new_cmp = _normalize_for_compare(old, new)

                    if old_cmp is None or abs(new_cmp - old_cmp) > TOLERANCE:
                        row.commence_time_mt = new
                        changed = True

                    if changed:
                        wk_updated += 1
                        print(
                            f"[SCHEDULE] Updated: {g['game_id']} | "
                            f"{g['away_team']} @ {g['home_team']} | {g['commence_time_mt']}"
                        )
                    else:
                        wk_unchanged += 1

                else:
                    db.session.add(
                        Game(
                            game_id=g["game_id"],
                            season_year=g["season_year"],
                            season_type=g["season_type"],
                            week=g["week"],
                            week_label=g.get("week_label"),
                            home_team=g["home_team"],
                            away_team=g["away_team"],
                            commence_time_mt=g["commence_time_mt"],
                        )
                    )
                    wk_inserted += 1
                    print(
                        f"[SCHEDULE] Added: {g['game_id']} | "
                        f"{g['away_team']} @ {g['home_team']} | {g['commence_time_mt']}"
                    )

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
        failed += 1
        print(f"[SCHEDULE] ❌ Schedule update failed: {e}")

    print(
        f"[SCHEDULE] Finished — "
        f"inserted={inserted}, updated={updated}, unchanged={unchanged}, failed={failed}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "failed": failed,
        "failed_weeks": failed,
    }