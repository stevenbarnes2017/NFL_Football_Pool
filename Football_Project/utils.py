from datetime import datetime
import pytz
import platform
from .models import db, Game, Pick, UserScore
from get_the_odds import get_current_week
import requests


# Function to parse datetime with timezone and format it
def parse_datetime_with_timezone(datetime_str, timezone_abbr):
    naive_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    
    if timezone_abbr == "MDT":
        timezone = pytz.timezone("America/Denver")
    elif timezone_abbr == "MST":
        timezone = pytz.timezone("America/Denver")
    else:
        raise ValueError(f"Unrecognized timezone abbreviation: {timezone_abbr}")
    
    localized_datetime = timezone.localize(naive_datetime)
    
    if platform.system() == 'Windows':
        formatted_datetime = localized_datetime.strftime("%b %d %Y %#I:%M%p %Z")
    else:
        formatted_datetime = localized_datetime.strftime("%b %d %Y %-I:%M%p %Z")
    
    return formatted_datetime

def group_games_by_day(games_list):
    grouped_games = {
        "Thursday": [],
        "Friday": [],
        "Sunday": [],
        "Monday": []
    }

    for game in games_list:
        commence_time = game['commence_time_mt']

        # Check if it's a datetime object, else parse it as string
        if isinstance(commence_time, datetime):
            # If datetime has timezone info, extract it
            if commence_time.tzinfo is not None:
                timezone_abbr = commence_time.tzname()
            else:
                # Default to 'UTC' if no timezone info present
                timezone_abbr = 'UTC'
        else:
            # Parse string representation into a datetime object
            commence_time = datetime.strptime(commence_time, '%Y-%m-%d %H:%M:%S')
            timezone_abbr = 'UTC'  # Handle the default timezone if none is present in the string

        # Format the datetime object
        game['commence_time_mt'] = commence_time

        # Extract the day of the week
        day_of_week = commence_time.strftime("%A")

        if day_of_week == "Thursday":
            grouped_games["Thursday"].append(game)
        elif day_of_week == "Friday":
            grouped_games["Friday"].append(game)
        elif day_of_week == "Sunday":
            grouped_games["Sunday"].append(game)
        elif day_of_week == "Monday":
            grouped_games["Monday"].append(game)

    return grouped_games

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


def get_football_scores(year, seasontype, weeknum):
    """
    Fetch football scores from an external API or another data source.
    This function needs to return a list of dictionaries, where each dictionary represents a game's scores.
    """
    # Example data structure returned:
    # [{'home_team': 'Team A', 'away_team': 'Team B', 'home_score': '10', 'away_score': '20', 'status': 'STATUS_FINAL'}]
    # Make sure your real implementation returns the data in this format.
    # (Actual API call logic goes here...)
    pass

def lock_picks_for_commenced_games(user_id):
    current_week = get_current_week()  # Function that returns the current week

    # Get all games for the current week that have commenced
    commenced_games = Game.query.filter(
        Game.week == current_week,
        Game.commence_time_mt <= datetime.utcnow()
    ).all()

    for game in commenced_games:
        # Check if user has already made a pick for this game
        existing_pick = Pick.query.filter_by(user_id=user_id, game_id=game.id).first()

        if not existing_pick:
            # Assign the highest available confidence point to the user and mark pick as missed
            available_points = get_highest_available_confidence(user_id, current_week)
            missed_pick = Pick(
                user_id=user_id,
                game_id=game.id,
                confidence_points=available_points,
                points_earned=0  # No points if missed pick
            )
            db.session.add(missed_pick)

    db.session.commit()

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
            down = situation.get('down', None)
            distance = situation.get('distance', None)
            possession_team = situation.get('possession', {}).get('displayName', None)
            yard_line = situation.get('yardLine', None)
        else:
            down = None
            distance = None
            possession_team = None
            yard_line = None

        # Append all relevant data to live_games list
        live_games.append({
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
