# preload_schedule.py
import requests
from typing import List, Dict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from Football_Project.app import app
from Football_Project.extensions import db
from Football_Project.models import Game

SEASON_YEAR = 2025
SEASON_TYPE = 2  # 1 = preseason, 2 = regular, 3 = postseason
WEEK_START = 1
WEEK_END = 18

MT = ZoneInfo("America/Denver")

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
        f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
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

            # ESPN kickoff (UTC ISO)
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

def preload_schedule():
    total_inserted = 0
    with app.app_context():
        for week in range(WEEK_START, WEEK_END + 1):
            try:
                games = fetch_games_by_week(week)
                print(f"\n📅 Week {week}: found {len(games)} games")
                if not games:
                    continue

                for g in games:
                    row = Game.query.filter_by(game_id=g["game_id"]).first()
                    if row:
                        # If kickoff is empty in DB, fill it now
                        if not getattr(row, "commence_time_mt", None):
                            row.commence_time_mt = g["commence_time_mt"]
                            print(f"🕒 Backfilled kickoff: {g['game_id']} -> {row.commence_time_mt}")
                        else:
                            print(f"⏭️  Exists (kept kickoff): {g['game_id']}")
                        continue

                    new_game = Game(
                        game_id=g["game_id"],
                        week=g["week"],
                        home_team=g["home_team"],
                        away_team=g["away_team"],
                        commence_time_mt=g["commence_time_mt"],  # set at insert
                    )
                    db.session.add(new_game)
                    total_inserted += 1
                    print(f"✅ Added: {g['game_id']} @ {g['commence_time_mt']}")

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed week {week}: {e}")

    print(f"\n✅ Done. Inserted {total_inserted} new game(s).")

if __name__ == "__main__":
    preload_schedule()
