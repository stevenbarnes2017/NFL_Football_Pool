import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
from pathlib import Path

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
    nfl_start_date = datetime(2024, 9, 5)  # Example start date
    current_date = datetime.now()
    week = ((current_date - nfl_start_date).days // 7) + 1
    return week

# Function to convert commence time to Mountain Time
def convert_to_mountain_time(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc.localize(utc_time)
    mt_time = utc_time.astimezone(mountain)
    return mt_time.strftime("%Y-%m-%d %H:%M:%S %Z")

# Function to filter games within the next 7 days
def is_within_next_7_days(utc_time_str):
    current_time = datetime.utcnow().replace(tzinfo=utc)
    game_time = utc.localize(datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ"))
    return current_time <= game_time <= current_time + timedelta(days=14)

# Function to parse and extract relevant spreads data
def parse_spreads_data(odds_data):
    
    games_list = []
    for game in odds_data:
        home_team = game['home_team']
        away_team = game['away_team']
        commence_time_utc = game['commence_time']
        # Add these print statements in parse_spreads_data
        # Print the home and away teams at the start of each loop iteration
        print(f"Checking game: {home_team} vs {away_team} at {commence_time_utc}")
        
        if not is_within_next_7_days(commence_time_utc):
            continue
        
        commence_time_mt = convert_to_mountain_time(commence_time_utc)

        for bookmaker in game['bookmakers']:
            if bookmaker['title'].lower() == "draftkings":
                for market in bookmaker['markets']:
                    if market['key'] == 'spreads':
                        home_spread = None
                        away_spread = None
                        
                        for outcome in market['outcomes']:
                            if outcome['name'] == home_team:
                                home_spread = outcome['point']
                            elif outcome['name'] == away_team:
                                away_spread = outcome['point']

                        if home_spread < 0:
                            favorite_team = home_team
                            spread = home_spread
                        elif away_spread < 0:
                            favorite_team = away_team
                            spread = away_spread
                        else:
                            favorite_team = "Even"
                            spread = None

                        games_list.append({
                            "home_team": home_team,
                            "away_team": away_team,
                            "spread": spread,
                            "favorite_team": favorite_team,
                            "commence_time_mt": commence_time_mt
                        })

    return games_list

# Function to save spreads data to CSV in a writable directory
def save_to_csv(games_list, filename):
    try:
        # Get the user's home directory
        home = Path.home()

        # Create the path to the Downloads folder
        downloads_dir = home / "Downloads"

        # Ensure the folder exists (it should, but this is a safeguard)
        if not downloads_dir.exists() or not os.access(downloads_dir, os.W_OK):
            print("Unable to access Downloads folder. Saving to current directory.")
            downloads_dir = Path.cwd()  # Fallback to current working directory

        # Combine the path with the desired filename
        filepath = downloads_dir / filename

        # Save the dataframe to the CSV file
        df = pd.DataFrame(games_list)
        df.to_csv(filepath, index=False)
        
        print(f"Spreads data saved to {filepath}")
    except PermissionError as e:
        print(f"An error occurred: {e}")
        print("Permission denied. Please check your file permissions.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Function to save spreads data to the database
def save_spreads_to_db(games_list, week):     
    from app import app, db, Game    
    with app.app_context():
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
        
        db.session.commit()  
