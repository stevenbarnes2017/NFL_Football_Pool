from datetime import datetime
import pytz
import platform
from .models import db, Game, Pick, UserScore
from Football_Project.get_the_odds import get_current_week
from football_scores import save_scores_to_db, get_football_scores
import requests
from flask import render_template, current_app, request, session
from pytz import timezone  # Add this
import logging  # Ensure logging is imported at the top
import os
import json
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import func, literal
from .scoring import norm_status
from collections import defaultdict
import re



season_type = 2  # 1 = preseason, 2 = regular, 3 = postseason
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_effective_user_id():
    view_as_id = session.get("view_as_user_id") or session.get("admin_view_as_user_id")
    if view_as_id and getattr(current_user, "is_admin", False):
        try:
            return int(view_as_id)
        except (TypeError, ValueError):
            return current_user.id
    return current_user.id

def get_settings() ->"Settings":
    s = Settings.query.first()
    if not s:
        s = Settings(current_week=18, season_year=2025, season_type="REG", season_locked=True)
        db.session.add(s)
        db.session.commit()
    return s

def get_effective_user():
    """
    Returns the user we should act as:
    - If admin is in view-as mode: that user
    - Otherwise: current_user
    """
    view_as_id = session.get("view_as_user_id")
    if view_as_id and getattr(current_user, "is_admin", False):
        u = User.query.get(view_as_id)
        if u:
            return u
    return current_user

def send_picks_email(recipient_email, user_picks):
    # Format the picks into an email-friendly string
    picks_body = "Here are your picks for the current week:\n\n"

    # Define column widths
    team_column_width = 25  # Adjust this width as needed
    
    # Loop over the dictionary items and extract only team_picked and confidence
    for details in user_picks.values():
        team_picked = details.get('team_picked')
        confidence = details.get('confidence')
        if team_picked and confidence is not None:
            picks_body += f"{team_picked}   {confidence}\n"

    # Brevo API endpoint for sending transactional emails
    url = "https://api.brevo.com/v3/smtp/email"

    # Headers for authorization and content type
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    # Email content with the formatted picks
    email_data = {
        "sender": {"name": "NFL Football Pool", "email": "lines31@hotmail.com"},
        "to": [{"email": recipient_email}],
        "subject": "Your Weekly Picks",
        "htmlContent": f"<pre>{picks_body}</pre>"
    }

    # Send the email using a POST request
    try:
        response = requests.post(url, json=email_data, headers=headers)
        response.raise_for_status()
        print("Email sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send email: {e}")
        print(f"Using API Key: {headers['api-key']}")
        raise



# Cache for scores
live_scores_cache = {'live_games': [], 'last_week_games': None}

def send_password_reset_email(recipient_email, reset_url):
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")  # Read fresh at runtime
    print(f"Using BREVO_API_KEY: {BREVO_API_KEY}")  # Debugging line
    if not BREVO_API_KEY:
        raise RuntimeError("BREVO_API_KEY is not set in the environment!")

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    html_content = f"""
    <p>Hello,</p>
    <p>You requested to reset your password. Click the link below to reset it:</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>If you didn’t request this, you can safely ignore this email.</p>
    """

    email_data = {
        "sender": {"name": "NFL Football Pool", "email": "lines31@hotmail.com"},
        "to": [{"email": recipient_email}],
        "subject": "Reset Your Password",
        "htmlContent": html_content
    }

    response = requests.post(url, json=email_data, headers=headers)
    response.raise_for_status()
    print(f"✅ Password reset email sent to {recipient_email}!")


def fetch_and_cache_scores():
    """Fetch live scores and update the cache."""
    try:
        with current_app.app_context():
            global live_scores_cache
            live_scores_cache = fetch_live_scores()
            print("fetch_and_cache_scores executed successfully")
    except Exception as e:
        print(f"Error in fetch_and_cache_scores: {e}")
    


def save_week_scores_to_db(year, seasontype, weeknum):
    """
    Fetch and save the football game scores for a given year, season type, and week.
    """
    try:
        # Fetch the football game scores for the given week
        games = get_football_scores(year, seasontype, weeknum)  # This returns a list

        # Check if games were retrieved successfully
        if not games:
            print(f"No games data to save for week {weeknum}.")
            return f"No data available for week {weeknum}."

        # Save each game's score to the database
        save_scores_to_db(games, weeknum)  # Assumes save_scores_to_db can handle a list of game dictionaries
        return f"Successfully saved game scores for week {weeknum} to the database."

    except Exception as e:
        print(f"An error occurred while fetching or saving the scores: {e}")
        return str(e)



# Function to detect timezone and parse datetime correctly
def parse_datetime_with_timezone(datetime_str):
    # Split datetime string and timezone abbreviation
    if 'MDT' in datetime_str:
        dt_str, timezone_abbr = datetime_str.rsplit(' ', 1)
        mountain_tz = pytz.timezone('America/Denver')  # Covers MDT during DST
    elif 'MST' in datetime_str:
        dt_str, timezone_abbr = datetime_str.rsplit(' ', 1)
        mountain_tz = pytz.timezone('America/Denver')  # Covers MST (Standard Time)
    else:
        raise ValueError(f"Unknown timezone in datetime string: {datetime_str}")

    # Parse the naive datetime string (without timezone abbreviation)
    naive_datetime = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

    # Localize the naive datetime to the correct timezone
    localized_datetime = mountain_tz.localize(naive_datetime)

    # Convert the localized datetime to UTC and return
    return localized_datetime.astimezone(pytz.utc)

#Function to query the db for all saved games and return them.
def get_saved_games(week=None):
    query = Game.query.order_by(Game.commence_time_mt)
    if week is not None:
        query = query.filter_by(week=week)
    
    saved_games = query.all()

    games_list = []
    for game in saved_games:
        games_list.append({
            "id": game.id,
            "home_team": game.home_team,
            "away_team": game.away_team,
            "spread": game.spread,
            "favorite_team": game.favorite_team,
            "commence_time_mt": game.commence_time_mt,
            "week": game.week
        })
    
    return games_list

# Function to tally user scores based on the week
def calculate_user_scores(week: int, write_final_only: bool = True):
    """
    Recalculate points_earned on each Pick for the given week (live).
    Persist weekly totals to UserScore using FINAL games only (default).
    Returns a dict of totals:
      - if write_final_only=True -> FINAL-only totals
      - else -> LIVE (in-progress + final) totals
    """
    games = Game.query.filter_by(week=week).all()
    picks = Pick.query.filter_by(week=week).all()

    # quick visibility
    distinct_statuses = {norm_status(g.status) for g in games}
    print(f"[scores] Week {week} statuses in DB: {distinct_statuses}")

    live_total_by_user  = defaultdict(int)
    final_total_by_user = defaultdict(int)

    considered, awarded = 0, 0

    # Pre-index games for speed
    games_by_id = {g.id: g for g in games}

    for pick in picks:
        if pick.is_overridden:
            # honor manual override both in live and (if final) rollups
            live_total_by_user[pick.user_id]  += pick.points_earned or 0
            final_total_by_user[pick.user_id] += pick.points_earned or 0
            continue

        game = games_by_id.get(pick.game_id)
        if not game:
            continue

        g_status = norm_status(game.status)

        if g_status not in ('STATUS_IN_PROGRESS', 'STATUS_FINAL'):
            # nothing to award yet
            continue

        considered += 1
        points = 0

        home = game.home_team_score
        away = game.away_team_score

        if home is None or away is None:
            # cannot judge without scores
            points = 0
        else:
            # If spread is missing, award by straight winner
            if game.spread is None:
                winner = game.home_team if home > away else game.away_team
                if pick.team_picked == winner:
                    points = pick.confidence or 0
            else:
                # ATS: favorite must cover
                fav = game.favorite_team
                if not fav:
                    # fall back to straight winner if favorite unknown
                    winner = game.home_team if home > away else game.away_team
                    if pick.team_picked == winner:
                        points = pick.confidence or 0
                else:
                    # margin from favorite's perspective
                    if game.home_team == fav:
                        margin = home - away
                    else:
                        margin = away - home

                    covered = margin > abs(game.spread)

                    if pick.team_picked == fav and covered:
                        points = pick.confidence or 0
                    elif pick.team_picked != fav and not covered:
                        points = pick.confidence or 0

        # Update the pick row for live views
        pick.points_earned = points
        db.session.add(pick)

        # Live total (in-progress + final)
        live_total_by_user[pick.user_id] += points

        # Weekly locked totals: only from FINAL games
        if g_status == 'STATUS_FINAL':
            final_total_by_user[pick.user_id] += points
            awarded += 1 if points else 0

    db.session.commit()

    print(f"[scores] Week {week}: picks={len(picks)} considered={considered} final_awards>0={awarded}")

    # Persist to UserScore weekly table (locked totals only)
    if write_final_only:
        for user_id, score in final_total_by_user.items():
            row = UserScore.query.filter_by(user_id=user_id, week=week).first()
            if row:
                row.score = score
                row.calculated_at = datetime.utcnow()
            else:
                db.session.add(UserScore(user_id=user_id, week=week, score=score))
        db.session.commit()
        # For callers that expect a dict of totals, return what we wrote (final-only)
        return dict(final_total_by_user)

    # If someone needs live totals instead:
    return dict(live_total_by_user)

def get_current_season_year():
    """
    Returns the NFL season year (not calendar year).
    Jan–Feb belong to the prior season.
    """
    now = datetime.now(timezone("US/Mountain"))
    return now.year - 1 if now.month in (1, 2) else now.year

def auto_fetch_scores():
    """Fetch and process scores automatically."""
    try:
        logger.debug("Executing auto_fetch_scores job")
        print("auto_fetch_scores triggered")

        with current_app.app_context():
            from datetime import datetime
            
            year = get_current_season_year()

            current_week = get_current_week()
            print(f"Year: {year}, Season Type: {season_type}, Fetching scores for Week: {current_week}")

            games = get_football_scores(year, season_type, current_week)
            result = save_week_scores_to_db(year, season_type, current_week)
            print(f"Result of save_week_scores_to_db: {result}")

            calculate_user_scores(current_week)
            print(f"User scores calculated and updated for week {current_week}.")

    except Exception as e:
        print(f"Error in auto_fetch_scores: {e}")
    finally:
        print("Finished running auto_fetch_scores")



def get_unpicked_games_for_week(user_picks, week, season_year, season_type):
    picked_game_ids = {pick.game_id for pick in user_picks}

    query = Game.query.filter(
        Game.season_year == season_year,
        Game.season_type == season_type,
        Game.week == week
    )

    if picked_game_ids:
        query = query.filter(~Game.id.in_(picked_game_ids))

    return query.order_by(Game.commence_time_mt.asc()).all()

def save_user_scores_to_db(user_scores, week):
    """
    Save or update user scores in the database for a specific week.
    """
    # Debug print to check the structure of user_scores
    print(f"user_scores structure: {user_scores}")
    
    # Ensure user_scores is a dictionary before calling .items()
    if isinstance(user_scores, dict):
        for user_id, score in user_scores.items():
            # Check if the user already has a score entry for the given week
            score_record = UserScore.query.filter_by(user_id=user_id, week=week).first()
            if score_record:
                # Update existing score record
                score_record.score = score
            else:
                # Create new score record
                score_record = UserScore(user_id=user_id, week=week, score=score)
                db.session.add(score_record)
        
        db.session.commit()  # Commit the changes to the database
    else:
        print("Error: user_scores is not a dictionary!")

# Define time zones
utc = pytz.utc
mountain = pytz.timezone('US/Mountain')

# Function to convert UTC time to Mountain Time
def convert_to_mountain_time(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%MZ")
    utc_time = utc.localize(utc_time)
    return utc_time.astimezone(mountain).strftime("%Y-%m-%d %H:%M:%S %Z")

# Function to convert Mountain Time to UTC
def convert_mountain_time_to_utc(mt_time_str):
    dt_str, tz_abbr = mt_time_str.rsplit(' ', 1)
    naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

    if tz_abbr == 'MDT':
        mt_time = mountain.localize(naive_dt)
    elif tz_abbr == 'MST':
        mt_time = mountain.localize(naive_dt)
    else:
        raise ValueError(f"Unknown timezone abbreviation: {tz_abbr}")
    
    return mt_time.astimezone(utc).strftime("%Y-%m-%d %H:%M:%S %Z")

# Function to convert a datetime string or object to UTC
def convert_to_utc(time_value):
    print(f"Converting time: {time_value}")  # Debugging time value before conversion

    if isinstance(time_value, str):
        # If time_value is a string, assume it's in "YYYY-MM-DD HH:MM:SS TZ" format
        try:
            dt_str, tz_abbr = time_value.rsplit(' ', 1)  # Split time and timezone
            naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

            # Localize the naive datetime based on the timezone abbreviation
            if tz_abbr == 'MDT':
                local_tz = pytz.timezone('America/Denver')
            elif tz_abbr == 'MST':
                local_tz = pytz.timezone('America/Denver')
            else:
                raise ValueError(f"Unknown timezone abbreviation: {tz_abbr}")

            # Localize the naive datetime to the correct time zone
            localized_dt = local_tz.localize(naive_dt)
        except Exception as e:
            print(f"Error during time parsing: {e}")
            raise e
    elif isinstance(time_value, datetime):
        localized_dt = time_value
    else:
        raise ValueError(f"Unsupported time format: {type(time_value)}")

    # Convert localized datetime to UTC and return
    utc_time = localized_dt.astimezone(pytz.utc)
    print(f"Converted time to UTC: {utc_time}")  # Debugging the result after conversion
    return utc_time


def highest_available_confidence(user_id: int, week: int) -> int | None:
    """Return the highest confidence number not yet used by this user in this week."""
    # how many games this week = how many confidence points exist
    total_games = Game.query.filter_by(week=week).count()
    all_confidences = set(range(1, total_games + 1))
    used = {
        p.confidence
        for p in Pick.query.filter_by(user_id=user_id, week=week)
        .filter(Pick.confidence.isnot(None))
        .all()
    }
    available = sorted(list(all_confidences - used), reverse=True)
    return available[0] if available else None


def lock_picks_for_commenced_games(user_id):
    from datetime import datetime, timezone
    import pytz

    now_utc = datetime.now(timezone.utc)
    current_week = get_current_week()

    week_games = Game.query.filter(Game.week == current_week).all()

    games_list = []
    for game in week_games:
        # normalize to aware UTC
        if isinstance(game.commence_time_mt, str):
            game_commence_time_utc = convert_to_utc(game.commence_time_mt)
        elif isinstance(game.commence_time_mt, datetime):
            if game.commence_time_mt.tzinfo is None:
                local_tz = pytz.timezone('America/Denver')
                localized_dt = local_tz.localize(game.commence_time_mt)
                game_commence_time_utc = localized_dt.astimezone(pytz.utc)
            else:
                game_commence_time_utc = game.commence_time_mt.astimezone(pytz.utc)
        else:
            raise ValueError(f"Invalid commence_time format for game {game.id}")

        games_list.append({
            'id': game.id,
            'home_team': game.home_team,
            'away_team': game.away_team,
            'spread': game.spread,
            'favorite_team': game.favorite_team,
            'commence_time_utc': game_commence_time_utc,
            'commence_time_mt': game.commence_time_mt,
        })

        # lock if kicked off
        if game_commence_time_utc <= now_utc:
            existing_pick = Pick.query.filter_by(user_id=user_id, game_id=game.id).first()

            if not existing_pick:
                # Case A: no pick at all -> create a missed pick with highest available confidence
                avail = highest_available_confidence(user_id, current_week)
                missed_pick = Pick(
                    user_id=user_id,
                    game_id=game.id,
                    week=current_week,
                    team_picked=None,        # no team chosen
                    confidence=avail,
                    points_earned=0,
                )
                db.session.add(missed_pick)

            elif existing_pick.team_picked and (existing_pick.confidence is None or existing_pick.confidence == 0):
                # Case B: team chosen but no confidence -> assign highest available
                avail = highest_available_confidence(user_id, current_week)
                existing_pick.confidence = avail
                db.session.add(existing_pick)

            # else: team + confidence already set -> leave it

    db.session.commit()

    used_confidence_points = [
        p.confidence for p in Pick.query.filter_by(user_id=user_id, week=current_week)
        .filter(Pick.confidence.isnot(None)).all()
    ]

    return render_template(
        'nfl_picks.html',
        now_utc=now_utc,
        games=games_list,
        selected_week=current_week,
        used_confidence_points=used_confidence_points
    )


def group_games_by_day(games_list):
    grouped_games = {
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
        "Sunday": [],
        "Monday": []
    }

    for game in games_list:
        commence_time_mt = game['commence_time_mt_display']  # Mountain Time for grouping
        day_of_week = commence_time_mt.strftime("%A")
        if day_of_week == "Wednesday":
            grouped_games["Wednesday"].append(game)
        if day_of_week == "Thursday":
            grouped_games["Thursday"].append(game)
        elif day_of_week == "Friday":
            grouped_games["Friday"].append(game)
        elif day_of_week == "Saturday":
            grouped_games["Saturday"].append(game)
        elif day_of_week == "Sunday":
            grouped_games["Sunday"].append(game)
        elif day_of_week == "Monday":
            grouped_games["Monday"].append(game)

    return grouped_games

def _norm_team(s: str) -> str:
    # normalize names: lower, strip non-alnum
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def _tkey(home: str, away: str) -> str:
    return f"{_norm_team(home)}|{_norm_team(away)}"

def _map_status(s: str | None) -> str:
    if not s:
        return "STATUS_SCHEDULED"
    t = s.strip().lower()
    if t in {"final", "finished", "completed", "status_final"}:
        return "STATUS_FINAL"
    if t in {"in progress", "live", "status_in_progress"}:
        return "STATUS_IN_PROGRESS"
    return "STATUS_SCHEDULED"


def save_game_scores_to_db(scores: list[dict], week: int) -> str:
    """
    scores: each item should expose at least:
      - home_team / away_team
      - home_score / away_score
      - status (optional)
      - (optional) any of: id / gameId / game_id / fixture_id / event_id
    """

    games = Game.query.filter_by(week=week).all()

    # maps
    by_id = {}
    for g in games:
        if getattr(g, "game_id", None):
            by_id[str(g.game_id)] = g

    by_key = { _tkey(g.home_team, g.away_team): g for g in games }
    # sometimes feeds flip home/away — include reverse key too
    for g in games:
        by_key.setdefault(_tkey(g.away_team, g.home_team), g)

    updated, skipped = 0, []

    for item in scores:
        # pull fields with fallbacks
        api_id = str(
            item.get("id")
            or item.get("gameId")
            or item.get("game_id")
            or item.get("fixture_id")
            or item.get("event_id")
            or ""
        )
        home = item.get("home_team") or item.get("homeTeam") or item.get("home")
        away = item.get("away_team") or item.get("awayTeam") or item.get("away")
        hs   = item.get("home_score") or item.get("homeTeamScore") or item.get("home_score_total")
        as_  = item.get("away_score") or item.get("awayTeamScore") or item.get("away_score_total")
        st   = _map_status(item.get("status") or item.get("state") or item.get("match_status"))

        g = None
        if api_id and api_id in by_id:
            g = by_id[api_id]
        elif home and away:
            g = by_key.get(_tkey(home, away))

        if not g:
            skipped.append({"home": home, "away": away, "api_id": api_id})
            continue

        # write scores/status
        if hs is not None and as_ is not None:
            try:
                g.home_team_score = int(hs)
                g.away_team_score = int(as_)
            except Exception:
                # leave as-is if parse error
                pass
        g.status = st
        updated += 1

    db.session.commit()
    return f"updated={updated} skipped={len(skipped)}"
    

    # Utility function to determine the highest available confidence points
# given the list of available points and picks already made.
def get_highest_available_confidence(available_confidences, used_confidences):
    available_confidences = sorted(list(set(available_confidences) - set(used_confidences)), reverse=True)
    return available_confidences[0] if available_confidences else None

# Utility function to check if a game can still be picked (based on kickoff time).
def is_game_open_for_pick(kickoff_time):
    now = datetime.now()
    return now < kickoff_time

# Utility function to determine points for a missed pick.
def assign_missed_pick_confidence(available_confidences):
    return max(available_confidences) if available_confidences else 0




import requests
import requests



def fetch_live_scores():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        live_scores = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching live scores: {e}")
        return {'live_games': [], 'last_week_games': fetch_last_week_scores()}

    live_games = []

    for game in live_scores.get('events', []):
        competition = game.get('competitions', [{}])[0]
        competitors = competition.get('competitors', [])
        status = game.get('status', {}).get('type', {})

        if len(competitors) < 2:
            continue

        # Team Data
        home_team = competitors[0].get('team', {}).get('displayName', 'Unknown')
        away_team = competitors[1].get('team', {}).get('displayName', 'Unknown')
        home_score = competitors[0].get('score', '0')
        away_score = competitors[1].get('score', '0')

        # Game Status Data
        clock = game.get('status', {}).get('displayClock', '0:00')
        period = game.get('status', {}).get('period', 1)
        game_status = status.get('description', 'Unknown')

        # Situation Data (down, distance, possession, yard line)
        situation = competition.get('situation', {})
        

        # Default values if data isn't present
        down = situation.get('down')
        distance = situation.get('distance')
        yard_line = situation.get('yardLine')
        possession_team = None

        # Check possession and map it to the correct team name if it's an ID
        possession_team_id = situation.get('possession')
        if possession_team_id:
            # Attempt to match possession_team_id with team IDs in competitors
            for competitor in competitors:
                if competitor.get('team', {}).get('id') == possession_team_id:
                    possession_team = competitor.get('team', {}).get('displayName')
                    break

        # Append all relevant data to live_games list
        live_games.append({
            'game_id': game.get('id', None),
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'status': game_status,
            'clock': clock,
            'period': period,
            'down': down,
            'distance': distance,
            'possession': possession_team,
            'yardLine': yard_line,
        })

    # Return live games data or fallback to last week's games if no live data
    if not live_games:
        last_week_games = fetch_last_week_scores()  # Fetch last week's games if needed
        return {'live_games': live_games, 'last_week_games': last_week_games}
    
    return {'live_games': live_games, 'last_week_games': None}


def fetch_detailed_game_stats(game_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}"
    print(f"Fetching detailed stats for game {game_id}...")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        game_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching detailed stats: {e}")
        return None

    # Fetch team and player stats
    boxscore = game_data.get('boxscore', {})
    teams = boxscore.get('teams', [])
    
    if len(teams) < 2:
        return None

    # Home and Away team stats
    home_team = teams[0].get('team', {}).get('displayName', 'Unknown')
    away_team = teams[1].get('team', {}).get('displayName', 'Unknown')
    
    # Team statistics like total yards, passing yards, etc.
    home_stats = teams[0].get('statistics', [])
    away_stats = teams[1].get('statistics', [])
    
    # Parse team stats
    home_team_stats = {stat.get('name', 'Unknown'): stat.get('displayValue', 'N/A') for stat in home_stats}
    away_team_stats = {stat.get('name', 'Unknown'): stat.get('displayValue', 'N/A') for stat in away_stats}

    # Fetch individual player stats (passing, rushing, receiving)
    players = boxscore.get('players', [])
    player_stats = {}

    for team_players in players:
        team = team_players.get('team', {}).get('displayName', 'Unknown')
        player_stats[team] = []
        
        for stat_category in team_players.get('statistics', []):
            stat_name = stat_category.get('name', 'Unknown')
            
            for player in stat_category.get('athletes', []):
                player_data = {
                    'name': player.get('athlete', {}).get('displayName', 'Unknown'),
                    'position': player.get('athlete', {}).get('position', {}).get('abbreviation', 'N/A'),
                    'stats': {
                        'passingYards': player.get('stats', [])[1] if stat_name == 'passing' else 'N/A',
                        'rushingYards': player.get('stats', [])[1] if stat_name == 'rushing' else 'N/A',
                        'receivingYards': player.get('stats', [])[1] if stat_name == 'receiving' else 'N/A',
                        'touchdowns': player.get('stats', [])[3] if len(player.get('stats', [])) > 3 else 'N/A',
                    }
                }
                player_stats[team].append(player_data)

    # Return combined detailed stats
    return {
        'home_team': home_team,
        'away_team': away_team,
        'home_team_stats': home_team_stats,
        'away_team_stats': away_team_stats,
        'player_stats': player_stats
    }




def fetch_last_week_scores():
    # Fetch last week's scores (this is just an example, modify based on your actual logic)
    # You could use the ESPN API or your own database to get last week's data.
    last_week_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week=LAST_WEEK"
    response = requests.get(last_week_url)
    last_week_scores = response.json()

    last_week_games = []
    for game in last_week_scores['events']:
        home_team = game['competitions'][0]['competitors'][0]['team']['displayName']
        away_team = game['competitions'][0]['competitors'][1]['team']['displayName']
        home_score = game['competitions'][0]['competitors'][0]['score']
        away_score = game['competitions'][0]['competitors'][1]['score']
        status = game['status']['type']['description']  # "Final"

        last_week_games.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'status': status
        })

    return last_week_games

def save_pick_to_db(user_id, week, game_id, pick, confidence):
    """
    Save or update the user's pick for a specific game in the database.
    """
    existing_pick = Pick.query.filter_by(user_id=user_id, week=week, game_id=game_id).first()

    if existing_pick:
        # Debugging: Log the update action
        print(f"Updating pick for user {user_id} in week {week}, game {game_id}: {pick}, confidence {confidence}")
        # Update the existing pick
        existing_pick.team = pick
        existing_pick.confidence = confidence
    else:
        # Debugging: Log the new pick action
        print(f"Saving new pick for user {user_id} in week {week}, game {game_id}: {pick}, confidence {confidence}")
        # Create a new pick
        new_pick = Pick(user_id=user_id, week=week, game_id=game_id, team_picked=pick, confidence=confidence)
        db.session.add(new_pick)

    db.session.commit()

def get_user_picks(user_id, week):
    """
    Retrieve the user's picks from the database for the given week.
    """
    picks = Pick.query.filter_by(user_id=user_id, week=week).all()
    user_picks = {pick.game_id: (pick.team_picked, pick.confidence) for pick in picks}

    # Debugging: Log the retrieved picks
    print(f"Retrieved picks for user {user_id} in week {week}: {user_picks}")

    return user_picks


def get_picks(user_id, week):
    # Query picks for the specified user and week
    picks = Pick.query.filter_by(user_id=user_id, week=week).all()
    # Format the picks data as needed for Excel or email
    picks_data = [
        {
            "home_team": pick.game.home_team,
            "away_team": pick.game.away_team,
            "spread": pick.game.spread,
            "favorite_team": pick.game.favorite_team,
            "team_picked": pick.team_picked,
            "confidence": pick.confidence
        }
        for pick in picks
    ]
    return picks_data

import requests

def get_nfl_playoff_picture():
    import requests

    url = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return None
    
    data = response.json()

    # Define conference mapping
    conference_map = {
        "American Football Conference": "AFC",
        "National Football Conference": "NFC"
    }
    
    playoff_picture = {
        "AFC": {"clinched": [], "in_hunt": [], "bubble": [], "eliminated": []},
        "NFC": {"clinched": [], "in_hunt": [], "bubble": [], "eliminated": []}
    }
    
    for conference in data.get('children', []):
        # Map the conference name
        conf_name = conference_map.get(conference.get('name'), conference.get('name'))
        
        # Access the standings entries directly under each conference
        if 'standings' in conference and 'entries' in conference['standings']:
            for entry in conference['standings']['entries']:
                team_data = entry['team']
                stats = {stat['name']: stat.get('value', 0) for stat in entry.get('stats', [])}
                
                # Extract the clincher display value if present
                clincher_stat = next((stat for stat in entry.get('stats', []) if stat['name'] == 'clincher'), {})
                clincher_display_value = clincher_stat.get('displayValue', '')

                # Determine clinched/eliminated status based on the display value
                clinched_playoff = clincher_display_value in ['x', 'y', 'z']
                clinched_division = clincher_display_value in ['y', 'z']
                eliminated = clincher_display_value == 'e'

                team_info = {
                    'name': team_data.get('displayName', 'Unknown Team'),
                    'logo': team_data.get('logos', [{}])[0].get('href', ''),
                    'wins': stats.get('wins', 0),
                    'losses': stats.get('losses', 0),
                    'ties': stats.get('ties', 0),
                    'points_for': stats.get('pointsFor', 0),
                    'points_against': stats.get('pointsAgainst', 0),
                    'point_differential': stats.get('pointDifferential', 0),
                    'streak': stats.get('streak', ''),
                    'division_record': stats.get('divisionWinPercent', 0),
                    'conference_record': stats.get('conferenceWinPercent', 0),
                    'playoff_seed': stats.get('playoffSeed'),
                    'clinched_playoff': clinched_playoff,
                    'clinched_division': clinched_division,
                    'eliminated': eliminated
                }

                # Classify teams based on clinched/eliminated status
                if eliminated:
                    playoff_picture[conf_name]["eliminated"].append(team_info)
                elif clinched_playoff:
                    playoff_picture[conf_name]["clinched"].append(team_info)
                elif team_info['playoff_seed'] and team_info['playoff_seed'] <= 7:
                    playoff_picture[conf_name]["in_hunt"].append(team_info)
                elif team_info['playoff_seed']:
                    playoff_picture[conf_name]["bubble"].append(team_info)

    return playoff_picture


def map_bracket_data(standings):
    def format_matchup(team1, team2):
        """
        Format a matchup as a list of two dictionaries representing the teams.
        If a team is None (e.g., empty slot), it returns None for that team.
        """
        return [
            {"seed": team1.get("playoff_seed"), "name": team1.get("name")} if team1 else None,
            {"seed": team2.get("playoff_seed"), "name": team2.get("name")} if team2 else None
        ]

    # Check for empty lists in standings and handle safely
    afc_clinched = standings["AFC"]["clinched"] if "clinched" in standings["AFC"] else []
    nfc_clinched = standings["NFC"]["clinched"] if "clinched" in standings["NFC"] else []
    afc_in_hunt = standings["AFC"]["in_hunt"] if "in_hunt" in standings["AFC"] else []
    nfc_in_hunt = standings["NFC"]["in_hunt"] if "in_hunt" in standings["NFC"] else []

    afc_bracket = {
        "wildcard": [
            format_matchup(afc_in_hunt[0] if len(afc_in_hunt) > 0 else None, afc_in_hunt[3] if len(afc_in_hunt) > 3 else None),
            format_matchup(afc_in_hunt[1] if len(afc_in_hunt) > 1 else None, afc_in_hunt[2] if len(afc_in_hunt) > 2 else None)
        ],
        "divisional": [
            format_matchup(afc_clinched[0] if len(afc_clinched) > 0 else None, None),  # Top-seeded team gets a bye
            format_matchup(None, None)  # Placeholder for wildcard winners
        ],
        "championship": [
            format_matchup(None, None)  # Placeholder for divisional winners
        ],
    }

    nfc_bracket = {
        "wildcard": [
            format_matchup(nfc_in_hunt[0] if len(nfc_in_hunt) > 0 else None, nfc_in_hunt[3] if len(nfc_in_hunt) > 3 else None),
            format_matchup(nfc_in_hunt[1] if len(nfc_in_hunt) > 1 else None, nfc_in_hunt[2] if len(nfc_in_hunt) > 2 else None)
        ],
        "divisional": [
            format_matchup(nfc_clinched[0] if len(nfc_clinched) > 0 else None, None),  # Top-seeded team gets a bye
            format_matchup(None, None)  # Placeholder for wildcard winners
        ],
        "championship": [
            format_matchup(None, None)  # Placeholder for divisional winners
        ],
    }

    # Format Super Bowl matchup
    super_bowl = {
        "afc_champion": "TBD",
        "nfc_champion": "TBD"
    }

    return afc_bracket, nfc_bracket, super_bowl

def get_odds_data():
    """
    Fetch odds for all games from The Odds API and print the raw response for debugging.
    """
    API_KEY = "8b42837961f5ba838a1e1fc381e7600c"  # Replace with your actual API key
    URL = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
    
    params = {
        "apiKey": API_KEY,
        "regions": "us",  # US odds
        "markets": "h2h,spreads,totals",  # Desired markets
        "oddsFormat": "american",  # American odds format
    }

    try:
        # Make the API request
        response = requests.get(URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Print the raw JSON response for debugging
        print("API Response (Raw JSON):")
        print(response.json())

        # Return parsed JSON data
        return response.json()

    except requests.RequestException as e:
        print(f"Error fetching odds data: {e}")
        return []

def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def generate_game_id(home_abbr, away_abbr, kickoff_dt):
    return f"2025-{home_abbr}-vs-{away_abbr}-{kickoff_dt.strftime('%Y%m%d')}"

def resolve_selected_week(default_week_provider):
    """
    Try to get the selected week from form/querystring.
    Falls back to default_week_provider() (your get_current_week).
    Supports common field names from your templates.
    """
    for key in ("week", "selected_week", "week_number"):
        val = request.values.get(key)  # works for both form and query args
        if val is not None:
            try:
                wk = int(val)
                if 1 <= wk <= 18:  # regular season + playoffs if you use them
                    return wk
            except ValueError:
                pass
    return default_week_provider()

