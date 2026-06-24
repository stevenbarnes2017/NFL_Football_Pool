import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

from Football_Project.models import db, Game

# =============================
# Config
# =============================
API_KEY = os.getenv("ODDS_API_KEY", "8b42837961f5ba838a1e1fc381e7600c")
BASE_URL = (
    "https://api.the-odds-api.com/v4/"
    "sports/americanfootball_nfl/odds/"
    f"?apiKey={API_KEY}&regions=us&markets=h2h,spreads&oddsFormat=american"
)
BOOKMAKER_MATCH = "draftkings"  # lowercase compare

# Time zones
utc = pytz.utc
mountain = pytz.timezone("US/Mountain")  # Mountain Time
MT = pytz.timezone("US/Mountain")


# =============================
# Week calc
# =============================
def get_current_week():
    now_mt = datetime.now(MT).replace(tzinfo=None)  # DB stores naive MT

    # 1) Prefer schedule: most recent started game decides the week
    last_started = (Game.query
        .filter(Game.commence_time_mt <= now_mt)
        .order_by(Game.commence_time_mt.desc())
        .first())
    if last_started:
        return last_started.week

    # 2) If nothing has started yet (preseason/week 1 before kickoff), use earliest upcoming
    upcoming = (Game.query
        .filter(Game.commence_time_mt > now_mt)
        .order_by(Game.commence_time_mt.asc())
        .first())
    if upcoming:
        return upcoming.week

    # 3) Fallback (calendar math)
    preseason_start = datetime(2026, 8, 6)
    regular_start = datetime(2026, 9, 9)
    now = datetime.utcnow()

    if now < regular_start:
        delta = (now - preseason_start).days
        week = max(1, min((delta // 7) + 1, 4))
    else:
        delta = (now - regular_start).days
        week = (delta // 7) + 1
        if now.weekday() == 0 or (now.weekday() == 1 and now.hour < 6):
            week -= 1
        week = max(1, min(week, 18))

    return week


# =============================
# Time helpers
# =============================
def convert_to_mountain_time(utc_time_str: str) -> datetime:
    """
    Convert an API UTC time string like '2025-08-10T17:00:00Z'
    to a tz-aware datetime in US/Mountain.
    """
    dt_utc = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    dt_utc = utc.localize(dt_utc)           # attach UTC tz
    return dt_utc.astimezone(mountain)      # aware Mountain Time datetime


def is_within_next_7_days(utc_time_str: str) -> bool:
    """Keep only games scheduled within the next 7 days (inclusive)."""
    current_time = datetime.now(utc)
    game_time = utc.localize(datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ"))
    return current_time <= game_time <= current_time + timedelta(days=7)


# =============================
# API + Parsing
# =============================
def get_nfl_spreads():
    print(f"Making API call to {BASE_URL} at {datetime.now()}")
    response = requests.get(BASE_URL, timeout=30)

    if response.status_code == 200:
        odds_data = response.json()
        games_list = parse_spreads_data(odds_data)
        num_of_games = len(games_list)
        return games_list, num_of_games
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return [], 0


def parse_spreads_data(odds_data):
    """
    Extract: home_team, away_team, favorite team, spread, commence_time_mt (tz-aware datetime).
    Filter to games within the next 7 days.
    Prefer spreads from BOOKMAKER_MATCH (e.g., DraftKings).
    """
    games_list = []

    for game in odds_data:
        home_team = game["home_team"]
        away_team = game["away_team"]
        commence_time_utc = game["commence_time"]

        # Filter by games within the next 7 days
        if not is_within_next_7_days(commence_time_utc):
            continue

        commence_time_mt = convert_to_mountain_time(commence_time_utc)

        # Look for the preferred bookmaker
        for bookmaker in game.get("bookmakers", []):
            if bookmaker.get("title", "").lower() != BOOKMAKER_MATCH:
                continue

            for market in bookmaker.get("markets", []):
                if market.get("key") != "spreads":
                    continue

                home_spread = None
                away_spread = None

                for outcome in market.get("outcomes", []):
                    name = outcome.get("name")
                    point = outcome.get("point")
                    if name == home_team:
                        home_spread = point
                    elif name == away_team:
                        away_spread = point

                # Choose favorite (guard against None)
                favorite_team = "Even"
                spread = None
                if home_spread is not None and home_spread < 0:
                    favorite_team = home_team
                    spread = home_spread
                elif away_spread is not None and away_spread < 0:
                    favorite_team = away_team
                    spread = away_spread

                games_list.append(
                    {
                        "home_team": home_team,
                        "away_team": away_team,
                        "spread": spread,                # favorite's spread (negative)
                        "favorite_team": favorite_team,  # team favored
                        "commence_time_mt": commence_time_mt,  # tz-aware datetime
                    }
                )

    return games_list


# =============================
# Persistence / Export
# =============================
def save_spreads_to_db(games_list, week: int):
    """
    Update existing Game rows for the given week by (home_team, away_team, week).
    Assign tz-aware datetime to Game.commence_time_mt.
    """
    updated = 0
    skipped = 0

    for game_data in games_list:
        game = (
            Game.query.filter_by(
                home_team=game_data["home_team"],
                away_team=game_data["away_team"],
                week=week,
            ).first()
        )

        if game:
            game.spread = game_data["spread"]
            game.favorite_team = game_data["favorite_team"]
            game.commence_time_mt = game_data["commence_time_mt"]  # datetime ✅
            updated += 1
        else:
            print(
                f"❌ No match for {game_data['home_team']} vs {game_data['away_team']} in week {week}"
            )
            skipped += 1

    db.session.commit()
    print(f"✅ Updated {updated} games")
    print(f"⏭️ Skipped {skipped} unmatched games")


def save_to_csv(games_list, filename):
    """
    Export for debugging. Convert datetimes to ISO strings just for CSV.
    """
    rows = []
    for g in games_list:
        r = dict(g)
        if isinstance(r.get("commence_time_mt"), datetime):
            r["commence_time_mt"] = r["commence_time_mt"].isoformat()
        rows.append(r)

    pd.DataFrame(rows).to_csv(filename, index=False)
    print(f"Spreads data saved to {filename}")


# =============================
# CLI helper
# =============================
def main(save_csv=False):
    games_list, num_of_games = get_nfl_spreads()
    print("Number of games found:", num_of_games)

    if save_csv:
        save_to_csv(games_list, "nfl_spreads_next_7_days.csv")

    return games_list, num_of_games


if __name__ == "__main__":
    main(save_csv=True)
