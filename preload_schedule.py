# preload_schedule.py
import requests
from typing import List, Dict
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from Football_Project.app import app
from Football_Project.extensions import db
from Football_Project.models import Game

SEASON_YEAR = 2025
SEASON_TYPE = 3  # 1 = preseason, 2 = regular, 3 = postseason
WEEK_START = 1
WEEK_END = 5

MT = ZoneInfo("America/Denver")
TOLERANCE = timedelta(minutes=1)


def season_type_label(season_type: int) -> str:
    """If your DB stores season_type as string."""
    if season_type == 1:
        return "PRE"
    if season_type == 2:
        return "REG"
    if season_type == 3:
        return "POST"
    return "REG"


def _espn_iso_to_mt(iso_str: str) -> datetime:
    if not iso_str:
        raise ValueError("missing kickoff date")

    s = iso_str.replace("Z", "+00:00")
    dt_utc = datetime.fromisoformat(s)
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    return dt_utc.astimezone(MT)


def generate_game_id(event_id: str, week: int) -> str:
    """
    Make game_id unique and stable even for TBD/TBD placeholders.
    ESPN event_id is unique per matchup slot.
    """
    return f"{SEASON_YEAR}-S{SEASON_TYPE}-W{week}-E{event_id}"


def fetch_games_by_week(week: int) -> List[Dict]:
    url = (
        "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        f"?seasontype={SEASON_TYPE}&year={SEASON_YEAR}&week={week}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    games: List[Dict] = []
    for event in data.get("events", []):
        try:
            event_id = str(event.get("id") or "")
            if not event_id:
                # Very rare, but don’t crash if missing
                continue

            comp = event["competitions"][0]
            competitors = comp["competitors"]

            home = next(c for c in competitors if c.get("homeAway") == "home")
            away = next(c for c in competitors if c.get("homeAway") == "away")

            home_team = home["team"]["displayName"]
            away_team = away["team"]["displayName"]

            kickoff_iso = event.get("date") or comp.get("date")
            kickoff_mt = _espn_iso_to_mt(kickoff_iso)

            games.append(
                {
                    "game_id": generate_game_id(event_id, week),
                    "season_year": SEASON_YEAR,
                    "season_type": season_type_label(SEASON_TYPE),  # if int column, use SEASON_TYPE
                    "week": week,  # ✅ ESPN week (no mapping)
                    "week_label": None,
                    "home_team": home_team,
                    "away_team": away_team,
                    "commence_time_mt": kickoff_mt,
                }
            )
        except Exception as e:
            print(f"⚠️  Skipping one event due to parse error: {e}")
            continue

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
    grand_weeks_failed = 0

    with app.app_context():
        try:
            print("🗄️  DB URL:", str(db.engine.url))
        except Exception as e:
            print(f"⚠️  Could not print DB URL: {e}")

        for week in range(WEEK_START, WEEK_END + 1):
            week_inserted = 0
            week_updated = 0
            week_unchanged = 0

            try:
                games = fetch_games_by_week(week)
                print(f"\n📅 ESPN Week {week}: found {len(games)} games")
                if not games:
                    continue

                for g in games:
                    with db.session.no_autoflush:
                        row = Game.query.filter_by(game_id=g["game_id"]).first()

                    if row:
                        changed_meta = False

                        # Ensure required metadata stays filled
                        if getattr(row, "season_year", None) != g["season_year"]:
                            row.season_year = g["season_year"]
                            changed_meta = True
                        if getattr(row, "season_type", None) != g["season_type"]:
                            row.season_type = g["season_type"]
                            changed_meta = True
                        if getattr(row, "week", None) != g["week"]:
                            row.week = g["week"]
                            changed_meta = True

                        # Update kickoff if missing or materially different
                        if not getattr(row, "commence_time_mt", None):
                            row.commence_time_mt = g["commence_time_mt"]
                            week_updated += 1
                            print(f"🕒 Backfilled kickoff: {g['game_id']} -> {row.commence_time_mt}")
                        else:
                            old = row.commence_time_mt
                            new = g["commence_time_mt"]
                            old_cmp, new_cmp = _normalize_for_compare(old, new)

                            if old_cmp is None or abs(new_cmp - old_cmp) > TOLERANCE:
                                row.commence_time_mt = new
                                week_updated += 1
                                print(f"🔁 Updated kickoff: {g['game_id']} {old} -> {new}")
                            else:
                                if changed_meta:
                                    week_updated += 1
                                    print(f"🧾 Updated metadata: {g['game_id']}")
                                else:
                                    week_unchanged += 1
                                    print(f"⏭️  Exists (same kickoff): {g['game_id']}")
                        continue

                    new_game = Game(
                        game_id=g["game_id"],
                        season_year=g["season_year"],
                        season_type=g["season_type"],   # if int column, use SEASON_TYPE
                        week=g["week"],                 # ✅ ESPN week
                        week_label=g.get("week_label"),
                        home_team=g["home_team"],
                        away_team=g["away_team"],
                        commence_time_mt=g["commence_time_mt"],
                    )
                    db.session.add(new_game)
                    week_inserted += 1
                    print(f"✅ Added: {g['game_id']} @ {g['commence_time_mt']}")

                db.session.commit()

                grand_inserted += week_inserted
                grand_updated += week_updated
                grand_unchanged += week_unchanged

                print(
                    f"✅ Week {week} committed: inserted={week_inserted}, updated={week_updated}, unchanged={week_unchanged}"
                )

            except Exception as e:
                db.session.rollback()
                grand_weeks_failed += 1
                print(f"❌ Failed week {week}: {e}")

    print(
        f"\n✅ Done. Inserted {grand_inserted} new game(s), "
        f"updated {grand_updated} existing game(s), "
        f"unchanged {grand_unchanged} game(s). "
        f"Weeks failed: {grand_weeks_failed}"
    )


if __name__ == "__main__":
    preload_schedule()
