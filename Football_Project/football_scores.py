import requests
import pandas as pd
from datetime import datetime
import pytz
from .models import db, Game
import os

# Ensure the directory path is properly formatted
save_directory = r"C:\Users\lines\OneDrive\dev\Football_Retry\Football_Project"

# Define time zones
utc = pytz.utc
mountain = pytz.timezone('US/Mountain')

# Function to convert UTC time string to Mountain Time
def convert_to_mountain_time(utc_time_str):
    # Parse the UTC time string
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%MZ")
    utc_time = utc.localize(utc_time)  # Localize it to UTC
    
    # Convert to Mountain Time
    mt_time = utc_time.astimezone(mountain)
    
    # Return the time as a string in Mountain Time zone
    return mt_time.strftime("%Y-%m-%d %H:%M:%S %Z")

# Function to convert Mountain Time string back to UTC
def convert_mountain_time_to_utc(mt_time_str):
    # Split the string into the datetime part and timezone abbreviation
    dt_str, tz_abbr = mt_time_str.rsplit(' ', 1)
    
    # Parse the datetime string
    naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    # Localize based on the timezone abbreviation
    if tz_abbr == 'MDT':
        mt_time = mountain.localize(naive_dt)
    elif tz_abbr == 'MST':
        mt_time = mountain.localize(naive_dt)
    else:
        raise ValueError(f"Unknown timezone abbreviation: {tz_abbr}")
    
    # Convert to UTC and return
    return mt_time.astimezone(utc).strftime("%Y-%m-%d %H:%M:%S %Z")

# Function to get football scores from ESPN API based on the year, season type, and week number
def get_football_scores(year, seasontype, weeknum):
    # Construct the URL
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={year}&seasontype={seasontype}&week={weeknum}"
    
    # Fetch data from the ESPN API
    response = requests.get(url)
    
    # Check if the response is OK
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return None
    
    data = response.json()
    
    # Parse the JSON data
    games = []
    for event in data['events']:
        for competition in event['competitions']:
            game = {
                "date": convert_to_mountain_time(event['date']),  # Convert date to Mountain Time
                "home_team": competition['competitors'][0]['team']['displayName'],
                "home_score": competition['competitors'][0]['score'],
                "away_team": competition['competitors'][1]['team']['displayName'],
                "away_score": competition['competitors'][1]['score'],
                "status": competition['status']['type']['name']
            }
            games.append(game)
    
    # Return the list of games
    return games

# Function to save the scores to a CSV file
def save_scores_to_csv(games, filepath):
    if games:
        # Debug: Print the filepath to check if it is correct
        print(f"Saving to file: {filepath}")
        
        # Ensure the directory exists
        directory = os.path.dirname(filepath)
        print(f"Checking if directory exists: {directory}")
        if not os.path.exists(directory):
            print(f"Directory does not exist. Creating: {directory}")
            os.makedirs(directory, exist_ok=True)

        # Convert the games data into a DataFrame
        df = pd.DataFrame(games)
        
        # Save the DataFrame to a CSV file
        df.to_csv(filepath, index=False)
        print(f"Football scores saved to {filepath}")
    else:
        print("No data to save.")

# Function to get user input for the parameters
def get_user_input():
    # Ask the user for the year
    year = input("Enter the year (e.g., 2024): ")
    
    # Ask the user for the season type
    print("Season type: 1 = Preseason, 2 = Regular season, 3 = Postseason")
    seasontype = input("Enter the season type (1, 2, or 3): ")
    
    # Ask the user for the week number
    weeknum = input("Enter the week number: ")
    
    return year, seasontype, weeknum

# Main function to run the program
def main():
    # Get user input
    year, seasontype, weeknum = get_user_input()

    # Get the football scores
    football_scores = get_football_scores(year, seasontype, weeknum)

    # Save the scores to a CSV file
    filename = os.path.join(save_directory, f"football_scores_week{weeknum}.csv")
    print(f"Constructed file path: {filename}")  # Debug: Print the full path to check if it's correct
    save_scores_to_csv(football_scores, filename)

def save_scores_to_db(games, week):    
    if games:
        for game in games:
            print(f"Saving game: {game}")
            existing_game = Game.query.filter_by(
                home_team=game['home_team'],
                away_team=game['away_team'],
                week=week
            ).first()

            if existing_game:
                existing_game.home_team_score = game['home_score']
                existing_game.away_team_score = game['away_score']
                existing_game.status = game['status']  # Save the game status
                db.session.commit()
        print(f"Scores for week {week} saved to the database.")
    else:
        print("No data to save.")

# Run the main function
if __name__ == "__main__":
    main()
