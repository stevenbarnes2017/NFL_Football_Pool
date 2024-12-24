from datetime import datetime
import pytz
import platform
from .models import db, Game, Pick, UserScore
from Football_Project.get_the_odds import get_current_week
from football_scores import save_scores_to_db, get_football_scores
import requests
from flask import render_template, current_app
from pytz import timezone  # Add this
import logging  # Ensure logging is imported at the top
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "api-key": os.getenv("BREVO_API_KEY") or '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',
        "content-type": "application/json"
    }

    # Email content with the formatted picks
    email_data = {
        "sender": {"name": "Your Name", "email": "lines31@hotmail.com"},
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
def calculate_user_scores(week):
    user_scores = {}
    tolerance = 0.001  # A small value to handle floating-point comparison issues

    # Get all games and picks for the specified week
    games = Game.query.filter_by(week=week).all()
    picks = Pick.query.filter_by(week=week).all()

    for pick in picks:
        # Skip recalculating if the score has been manually overridden
        if pick.is_overridden:
            if pick.user_id in user_scores:
                user_scores[pick.user_id] += pick.points_earned
            else:
                user_scores[pick.user_id] = pick.points_earned
            continue

        # Existing logic for calculating points based on game data
        game = next((g for g in games if g.id == pick.game_id), None)
        if not game:
            continue  # Skip if the game is not found

        # Skip games that are not in progress or finished
        if game.status not in ['STATUS_IN_PROGRESS', 'STATUS_FINAL']:
            continue

        points = 0
        # Ensure that home_team_score, away_team_score, and spread are not None
        if game.home_team_score is not None and game.away_team_score is not None and game.spread is not None:
            # Calculate points for favorite and underdog based on spread
            if pick.team_picked == game.favorite_team:
                if (game.home_team == game.favorite_team and game.home_team_score - game.away_team_score > abs(game.spread)) or \
                   (game.away_team == game.favorite_team and game.away_team_score - game.home_team_score > abs(game.spread)):
                    points = pick.confidence
            else:
                if (game.home_team == pick.team_picked and (game.home_team_score > game.away_team_score or (game.away_team_score - game.home_team_score < abs(game.spread)))) or \
                   (game.away_team == pick.team_picked and (game.away_team_score > game.home_team_score or (game.home_team_score - game.away_team_score < abs(game.spread)))):
                    points = pick.confidence

        # Update the points_earned field
        pick.points_earned = points
        
        db.session.add(pick)

        # Sum up the user's total points for the week
        if pick.user_id in user_scores:
            user_scores[pick.user_id] += points
        else:
            user_scores[pick.user_id] = points

    # Commit the updated points_earned values to the database
    db.session.commit()
    
    # Save or update the user scores for this week in the UserScore table
    for user_id, score in user_scores.items():
        user_score = UserScore.query.filter_by(user_id=user_id, week=week).first()
        if user_score:
            user_score.score = score  # Update existing record
        else:
            user_score = UserScore(user_id=user_id, week=week, score=score)
            db.session.add(user_score)
    print(f"User Score updated in DB for user_id: {user_id}, week: {week}, score: {score}")
    # Commit the updated user scores for the week
    db.session.commit()

    return user_scores  # Return the scores for this week


def auto_fetch_scores():
    """Fetch and process scores automatically."""
    try:
        logger.debug("Executing auto_fetch_scores job")
        print("auto_fetch_scores triggered")

        # Use the current Flask app context
        with current_app.app_context():
            year = 2024
            seasontype = 2

            current_week = get_current_week()
            previous_week = current_week
            print(f"Current Week: {current_week}, Fetching scores for Previous Week: {previous_week}")

            # Fetch and process scores
            games = get_football_scores(year, seasontype, previous_week)
            result = save_week_scores_to_db(year, seasontype, previous_week)
            print(f"Result of save_week_scores_to_db: {result}")

            # Calculate user scores
            calculate_user_scores(previous_week)
            print(f"User scores calculated and updated for week {previous_week}.")
    except Exception as e:
        print(f"Error in auto_fetch_scores: {e}")
    finally:
        print("Finished running auto_fetch_scores")

def get_unpicked_games_for_week(user_picks, week):
    # Get the IDs of the games the user has already picked
    picked_game_ids = [pick.game_id for pick in user_picks]

    # Fetch all games for the selected week
    all_games_for_week = Game.query.filter_by(week=week).all()

    # Return only the games that the user has not picked
    unpicked_games = [game for game in all_games_for_week if game.id not in picked_game_ids]

    return unpicked_games

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


def lock_picks_for_commenced_games(user_id):
    current_week = get_current_week()  # Get current NFL week
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)  # Get current time in UTC

    # Fetch all games for the current week
    commenced_games = Game.query.filter(Game.week == current_week).all()

    games_list = []

    for game in commenced_games:
        if isinstance(game.commence_time_mt, str):
            # Convert the commence time (with timezone abbreviation) to UTC
            game_commence_time_utc = convert_to_utc(game.commence_time_mt)
        elif isinstance(game.commence_time_mt, datetime):
            # If it's already a datetime object, ensure it's converted to UTC
            game_commence_time_utc = game.commence_time_mt.astimezone(pytz.utc)
        else:
            raise ValueError(f"Invalid commence_time format for game {game.id}")

        # Add the game to the list with the UTC commence time
        game_dict = {
            'id': game.id,
            'home_team': game.home_team,
            'away_team': game.away_team,
            'spread': game.spread,
            'favorite_team': game.favorite_team,
            'commence_time_utc': game_commence_time_utc,
            'commence_time_mt': game.commence_time_mt  # Optional, for display
        }
        games_list.append(game_dict)

        # Lock the game if it has already started (compare with now_utc)
        if game_commence_time_utc <= now_utc:
            existing_pick = Pick.query.filter_by(user_id=user_id, game_id=game.id).first()
            if not existing_pick:
                available_points = get_highest_available_confidence(user_id, current_week)
                missed_pick = Pick(
                    user_id=user_id,
                    game_id=game.id,
                    confidence_points=available_points,
                    points_earned=0  # No points for missed pick
                )
                db.session.add(missed_pick)

    # Commit the locked picks to the database
    db.session.commit()

    # Render the picks page with the games
    return render_template('nfl_picks.html', now_utc=now_utc, games=games_list, selected_week=current_week)

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




def save_game_scores_to_db(game_scores, week):
    """
    Save or update game scores in the database for a specific week.
    """
    for game in game_scores:
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        home_score = game.get('home_score')
        away_score = game.get('away_score')
        status = game.get('status')

        # Find the existing game record or create a new one
        game_record = Game.query.filter_by(home_team=home_team, away_team=away_team, week=week).first()

        if game_record:
            # Update the existing game record
            game_record.home_team_score = home_score
            game_record.away_team_score = away_score
            game_record.status = status
        else:
            # Create a new game record if it doesn't exist
            game_record = Game(
                home_team=home_team,
                away_team=away_team,
                home_team_score=home_score,
                away_team_score=away_score,
                status=status,
                week=week
            )
            db.session.add(game_record)

    db.session.commit()  # Commit all changes to the database
    

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
