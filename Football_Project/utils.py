from datetime import datetime
import pytz
import platform
from .models import db, Game, Pick, UserScore
from get_the_odds import get_current_week
from football_scores import save_scores_to_db, get_football_scores
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from flask import render_template
from pytz import timezone  # Add this


 # Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler_started = False

def start_scheduler():
    global scheduler_started  # Make sure to modify the global variable
    if not scheduler_started:  # Only start the scheduler if it's not already running
        scheduler.start()
        scheduler_started = True
        print("Scheduler started")

# Ensure the scheduler shuts down properly when the app stops
atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler_started else None)


def auto_fetch_scores():
    from Football_Project import create_app
    app = create_app()
    with app.app_context():
        year = 2024  # You can replace this with logic to determine the current year
        seasontype = 2  # Adjust as needed for preseason/postseason
        current_week = 6  # A function to get the current week number

        try:
            # This will call get_football_scores() through save_week_scores_to_db()
            result = save_week_scores_to_db(year, seasontype, current_week)
            
        except Exception as e:
            print(f"Error in auto_fetch_scores: {e}")  # Log any errors that occur

        print("Finished running auto_fetch_scores")



# Sunday: Every hour from 12:00 PM to 11:00 PM
scheduler.add_job(auto_fetch_scores, 'cron', day_of_week='sun', hour='12-23')

# Thursday & Monday: Every 30 minutes from 7:00 PM to 11:00 PM
scheduler.add_job(auto_fetch_scores, 'cron', day_of_week='thu,mon', hour='19-23', minute='0,30')

# Start the scheduler
scheduler.start()

# Ensure the scheduler shuts down properly only if it's running
atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)

def save_week_scores_to_db(year, seasontype, weeknum):
    """
    Fetch and save the football game scores for a given year, season type, and week.
    """
    try:
        # Fetch the football game scores for the given week
        scores = get_football_scores(year, seasontype, weeknum)  # Replace this with your actual function to fetch scores
        

        # Save the fetched scores to the database
        save_game_scores_to_db(scores, weeknum)
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

    # Commit the updated user scores for the week
    db.session.commit()

    return user_scores  # Return the scores for this week



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
        "Thursday": [],
        "Friday": [],
        "Sunday": [],
        "Monday": []
    }

    for game in games_list:
        commence_time_mt = game['commence_time_mt_display']  # Mountain Time for grouping
        day_of_week = commence_time_mt.strftime("%A")

        if day_of_week == "Thursday":
            grouped_games["Thursday"].append(game)
        elif day_of_week == "Friday":
            grouped_games["Friday"].append(game)
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

        # Ensure 'situation' is a dictionary
        if isinstance(situation, dict):
            down = situation.get('down')
            distance = situation.get('distance')
            # Ensure situation is a dictionary before accessing 'possession'
            if isinstance(situation, dict):
                possession_team = situation.get('possession', {}).get('displayName') if isinstance(situation.get('possession'), dict) else None
            else:
                # Handle case where 'situation' is not a dictionary
                print("Error: 'situation' is not a dictionary, it is:", type(situation))
                possession_team = None
            yard_line = situation.get('yardLine')
        else:
            down = None
            distance = None
            possession_team = None
            yard_line = None

        # Append all relevant data to live_games list
        live_games.append({
            'game_id': game.get('id', None),  # Add this line to include the game_id
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

    # Debugging: Print live games
    print(f"Live Games: {live_games}")

    # Return the result (or empty last_week_games if no live games)
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



scheduler = BackgroundScheduler()

def auto_fetch_scores():
    # Call fetch_live_scores and process final scores
    scores = fetch_live_scores()
    live_games = scores['live_games']
    
    # Process each game to check if it is 'Final'
    for game in live_games:
        if game['status'] == 'Final':
            save_scores_to_db(game)
            calculate_user_scores(get_current_week)

# Schedule job for Sunday: every hour from 12:00 PM to 11:00 PM
scheduler.add_job(auto_fetch_scores, 'cron', day_of_week='sun', hour='12-23')

# Schedule job for Thursday: every 30 minutes from 7:00 PM to 11:00 PM
scheduler.add_job(auto_fetch_scores, 'cron', day_of_week='thu', hour='19-23', minute='0,30')

# Schedule job for Monday: every 30 minutes from 7:00 PM to 11:00 PM
scheduler.add_job(auto_fetch_scores, 'cron', day_of_week='mon', hour='19-23', minute='0,30')

# Start the scheduler
scheduler.start()

# Ensure the scheduler shuts down properly on exit
atexit.register(lambda: scheduler.shutdown())