import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
from Football_Project.models import db, Game



# Your API key and the base URL for The Odds API
API_KEY = '0d35bd240841f8d2de6fe3669eece601'
BASE_URL = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/?apiKey={API_KEY}&regions=us&markets=h2h,spreads&oddsFormat=american"



# Define time zones
utc = pytz.utc
mountain = pytz.timezone('US/Mountain')

# Function to fetch the odds data
def get_nfl_spreads():
    response = requests.get(BASE_URL)
    
    if response.status_code == 200:
        odds_data = response.json()
        games_list = parse_spreads_data(odds_data)
        num_of_games = len(games_list)
        return games_list, num_of_games
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return [], 0

def get_current_week():
    # Assuming NFL season starts on a known date
    nfl_start_date = datetime(2024, 9, 1)  # Example start date
    current_date = datetime.utcnow()
    week = ((current_date - nfl_start_date).days // 7) + 1
    return week

# Function to convert commence time to Mountain Time
def convert_to_mountain_time(utc_time_str):
    # Parse the time string and assume it's in UTC
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc.localize(utc_time)
    
    # Convert to Mountain Time
    mt_time = utc_time.astimezone(mountain)
    
    # Return the time as a string in Mountain Time zone
    return mt_time.strftime("%Y-%m-%d %H:%M:%S %Z")

# Function to filter games within the next 7 days
def is_within_next_7_days(utc_time_str):
    current_time = datetime.now(utc)
    game_time = utc.localize(datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ"))
    
    return current_time <= game_time <= current_time + timedelta(days=7)

# Function to parse and extract relevant spreads data
def parse_spreads_data(odds_data):
    games_list = []

    for game in odds_data:
        home_team = game['home_team']
        away_team = game['away_team']
        commence_time_utc = game['commence_time']

        # Filter by games within the next 7 days
        if not is_within_next_7_days(commence_time_utc):
            continue
        
        commence_time_mt = convert_to_mountain_time(commence_time_utc)
        
        for bookmaker in game['bookmakers']:
            # Filter by bookmaker "BetUS"
            
            if bookmaker['title'].lower() == "bovada":
                
                for market in bookmaker['markets']:
                    if market['key'] == 'spreads':
                        # Initialize spread variables
                        home_spread = None
                        away_spread = None
                        
                        for outcome in market['outcomes']:
                            if outcome['name'] == home_team:
                                home_spread = outcome['point']
                            elif outcome['name'] == away_team:
                                away_spread = outcome['point']
                                
                        # Determine the favorite team and its spread
                        if home_spread < 0:
                            favorite_team = home_team
                            spread = home_spread
                        elif away_spread < 0:
                            favorite_team = away_team
                            spread = away_spread
                        else:
                            favorite_team = "Even"
                            spread = None  # No spread if it's even

                        games_list.append({
                            "home_team": home_team,
                            "away_team": away_team,
                            "spread": spread,  # Add favorite spread column
                            "favorite_team": favorite_team,  # Add favorite team column                            
                            "commence_time_mt": commence_time_mt  # Use the converted Mountain Time
                        })

    return games_list

# Function to save spreads data to CSV
def save_to_csv(games_list, filename):
    df = pd.DataFrame(games_list)
    df.to_csv(filename, index=False)
    print(f"Spreads data saved to {filename}")

# Main function to fetch, parse, and return NFL spreads
def main(save_csv=False):
    games_list, num_of_games = get_nfl_spreads()
    # Print the games that were parsed
    print("Number of games found:", num_of_games)
    print("Games List:")
    if save_csv:
        save_to_csv(games_list, 'nfl_spreads_next_7_days.csv')
    
    return games_list, num_of_games

# Function to save spreads data to the database
def save_spreads_to_db(games_list, week):     
    
    
        for game_data in games_list:
            existing_game = Game.query.filter_by(
                home_team=game_data['home_team'],
                away_team=game_data['away_team'],
                week=week
            ).first()

            if not existing_game:
                new_game = Game(
                    home_team=game_data['home_team'],
                    away_team=game_data['away_team'],
                    spread=game_data['spread'],
                    favorite_team=game_data['favorite_team'],
                    commence_time_mt=game_data['commence_time_mt'],
                    week=week
                )
                db.session.add(new_game)
        
        db.session.commit()  # This should be inside the `with` block
   
# Run the main function
if __name__ == "__main__":
    main(save_csv=True)

