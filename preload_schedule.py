# preload_schedule.py
import re
import requests
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from Football_Project.app import app
from Football_Project.extensions import db
from Football_Project.models import Game

SEASON_YEAR = 2026
SEASON_TYPE = 1  # 1 = preseason, 2 = regular, 3 = postseason

MT = ZoneInfo("America/Denver")
TOLERANCE = timedelta(minutes=1)

TEAM_CACHE: dict[str, str] = {}


def season_type_label(season_type: int) -> str:
    if season_type == 1:
        return "PRE"
    if season_type == 2:
        return "REG"
    if season_type == 3:
        return "POST"
    return "REG"


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


def generate_game_id(event_id: str, week: int) -> str:
    return f"{SEASON_YEAR}-S{SEASON_TYPE}-W{week}-E{event_id}"


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


def fetch_all_games() -> List[Dict]:
    url = (
        f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/"
        f"seasons/{SEASON_YEAR}/types/{SEASON_TYPE}/events?limit=1000"
    )

    data = fetch_json(url)
    print(f"📡 ESPN Core API returned {data.get('count', 0)} event refs")

    games: List[Dict] = []

    for item in data.get("items", []):
        ref = item.get("$ref")
        if not ref:
            continue

        try:
            event = fetch_json(ref)

            event_id = str(event.get("id") or "")
            if not event_id:
                print("⚠️  Skipping event with missing id")
                continue

            week = parse_week_from_ref(event.get("week", {}).get("$ref", ""))

            comp = event["competitions"][0]
            competitors = comp["competitors"]

            home = next(c for c in competitors if c.get("homeAway") == "home")
            away = next(c for c in competitors if c.get("homeAway") == "away")

            home_team = get_team_display_name(home["team"]["$ref"])
            away_team = get_team_display_name(away["team"]["$ref"])

            kickoff_iso = event.get("date") or comp.get("date")
            kickoff_mt = _espn_iso_to_mt(kickoff_iso)

            if kickoff_mt.year != SEASON_YEAR:
                print(
                    f"⚠️  Skipping stale ESPN event: {event_id} "
                    f"{away_team} @ {home_team} kickoff={kickoff_mt}"
                )
                continue

            games.append(
                {
                    "game_id": generate_game_id(event_id, week),
                    "season_year": SEASON_YEAR,
                    "season_type": season_type_label(SEASON_TYPE),
                    "week": week,
                    "week_label": None,
                    "home_team": home_team,
                    "away_team": away_team,
                    "commence_time_mt": kickoff_mt,
                    "event_id": event_id,
                }
            )

        except Exception as e:
            print(f"⚠️  Skipping one event due to parse error: {e}")
            continue

    games.sort(key=lambda g: (g["week"], g["commence_time_mt"], g["game_id"]))
    return games


def _normalize_for_compare(old_dt: datetime | None, new_dt: datetime) -> tuple[datetime | None, datetime]:
    if old_dt is None:
        return None, new_dt

    if (old_dt.tzinfo is None) and (new_dt.tzinfo is not None):
        return old_dt, new_dt.replace(tzinfo=None)

    if (old_dt.tzinfo is not None) and (new_dt.tzinfo is None):
        return old_dt.replace(tzinfo=None), new_dt

    return old_dt, new_dt


def preload_schedule():
    grand_inserted = 0
    grand_updated = 0
    grand_unchanged = 0

    with app.app_context():
        try:
            print("🗄️  DB URL:", str(db.engine.url))
        except Exception as e:
            print(f"⚠️  Could not print DB URL: {e}")

        games = fetch_all_games()

        if not games:
            print("⚠️  No games returned from ESPN Core API")
            return

        weeks = sorted(set(g["week"] for g in games))

        for week in weeks:
            week_games = [g for g in games if g["week"] == week]

            week_inserted = 0
            week_updated = 0
            week_unchanged = 0

            print(f"\n📅 ESPN Core Week {week}: found {len(week_games)} games")

            for g in week_games:
                print(
                    f"🔎 ESPN returned: {g['game_id']} | "
                    f"W{g['week']} | {g['away_team']} @ {g['home_team']} | "
                    f"{g['commence_time_mt']}"
                )

                with db.session.no_autoflush:
                    row = Game.query.filter_by(game_id=g["game_id"]).first()

                if row:
                    changed = False

                    fields_to_check = [
                        "season_year",
                        "season_type",
                        "week",
                        "week_label",
                        "home_team",
                        "away_team",
                    ]

                    for field in fields_to_check:
                        if getattr(row, field, None) != g.get(field):
                            setattr(row, field, g.get(field))
                            changed = True

                    old = getattr(row, "commence_time_mt", None)
                    new = g["commence_time_mt"]

                    if not old:
                        row.commence_time_mt = new
                        changed = True
                        print(f"🕒 Backfilled kickoff: {g['game_id']} -> {new}")
                    else:
                        old_cmp, new_cmp = _normalize_for_compare(old, new)

                        if old_cmp is None or abs(new_cmp - old_cmp) > TOLERANCE:
                            row.commence_time_mt = new
                            changed = True
                            print(f"🔁 Updated kickoff: {g['game_id']} {old} -> {new}")

                    if changed:
                        week_updated += 1
                        print(f"🧾 Updated: {g['game_id']}")
                    else:
                        week_unchanged += 1
                        print(f"⏭️  Exists unchanged: {g['game_id']}")

                    continue

                new_game = Game(
                    game_id=g["game_id"],
                    season_year=g["season_year"],
                    season_type=g["season_type"],
                    week=g["week"],
                    week_label=g.get("week_label"),
                    home_team=g["home_team"],
                    away_team=g["away_team"],
                    commence_time_mt=g["commence_time_mt"],
                )

                db.session.add(new_game)
                week_inserted += 1
                print(
                    f"✅ Added: {g['game_id']} | "
                    f"{g['away_team']} @ {g['home_team']} | "
                    f"{g['commence_time_mt']}"
                )

            db.session.commit()

            grand_inserted += week_inserted
            grand_updated += week_updated
            grand_unchanged += week_unchanged

            print(
                f"✅ Week {week} committed: "
                f"inserted={week_inserted}, "
                f"updated={week_updated}, "
                f"unchanged={week_unchanged}"
            )

    print(
        f"\n✅ Done. Inserted {grand_inserted} new game(s), "
        f"updated {grand_updated} existing game(s), "
        f"unchanged {grand_unchanged} game(s)."
    )


if __name__ == "__main__":
    preload_schedule()