# preload_schedule.py
import requests
from typing import List, Dict
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from Football_Project.app import app
from Football_Project.extensions import db
from Football_Project.models import Game

SEASON_YEAR = 2025
SEASON_TYPE = 2  # 1 = preseason, 2 = regular, 3 = postseason
WEEK_START = 1
WEEK_END = 18

MT = ZoneInfo("America/Denver")

# If kickoff differs by <= this, treat it as unchanged
TOLERANCE = timedelta(minutes=1)


def generate_game_id(home_abbr: str, away_abbr: str, week: int) -> str:
    return f"{SEASON_YEAR}-W{week}-{away_abbr}-at-{home_abbr}"


def _espn_iso_to_mt(iso_str: str) -> datetime:
    """
    ESPN gives UTC ISO like '2025-08-10T18:05Z' or '2025-08-10T18:05:00Z'.
    Return tz-aware Mountain Time datetime.
    """
    if not iso_str:
        raise ValueError("missing kickoff date")

    s = iso_str.replace("Z", "+00:00")
    dt_utc = datetime.fromisoformat(s)
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    return dt_utc.astimezone(MT)


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
            comp = event["competitions"][0]
            competitors = comp["competitors"]

            home = next(c for c in competitors if c.get("homeAway") == "home")
            away = next(c for c in competitors if c.get("homeAway") == "away")

            home_team = home["team"]["displayName"]
            away_team = away["team"]["displayName"]
            home_abbr = home["team"]["abbreviation"]
            away_abbr = away["team"]["abbreviation"]

            kickoff_iso = event.get("date") or comp.get("date")
            kickoff_mt = _espn_iso_to_mt(kickoff_iso)

            games.append(
                {
                    "game_id": generate_game_id(home_abbr, away_abbr, week),
                    "week": week,
                    "home_team": home_team,
                    "away_team": away_team,
                    "commence_time_mt": kickoff_mt,  # tz-aware MT datetime
                }
            )
        except Exception as e:
            print(f"⚠️  Skipping one event due to parse error: {e}")
            continue

    return games


def _normalize_for_compare(old_dt: datetime | None, new_dt: datetime) -> tuple[datetime | None, datetime]:
    """
    If your DB stores naive datetimes but ESPN produces tz-aware, normalize for safe comparison.
    Strategy:
      - If old is naive and new is aware: strip tz from new (compare naive-to-naive)
      - If old is aware and new is naive (rare): strip tz from old
      - Else compare as-is
    """
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
        # Sanity: confirm which DB we are writing to
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
                print(f"\n📅 Week {week}: found {len(games)} games")
                if not games:
                    continue

                for g in games:
                    row = Game.query.filter_by(game_id=g["game_id"]).first()

                    if row:
                        # Always update kickoff if missing OR materially different
                        if not getattr(row, "commence_time_mt", None):
                            row.commence_time_mt = g["commence_time_mt"]
                            week_updated += 1
                            print(f"🕒 Backfilled kickoff: {g['game_id']} -> {row.commence_time_mt}")
                        else:
                            old = row.commence_time_mt
                            new = g["commence_time_mt"]

                            old_cmp, new_cmp = _normalize_for_compare(old, new)

                            # old_cmp can't be None here, but keep it safe
                            if old_cmp is None or abs(new_cmp - old_cmp) > TOLERANCE:
                                row.commence_time_mt = new
                                week_updated += 1
                                print(f"🔁 Updated kickoff: {g['game_id']} {old} -> {new}")
                            else:
                                week_unchanged += 1
                                print(f"⏭️  Exists (same kickoff): {g['game_id']}")
                        continue

                    # Insert brand new game
                    new_game = Game(
                        game_id=g["game_id"],
                        week=g["week"],
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
