import requests
import pandas as pd
from datetime import datetime
import pytz
from Football_Project.models import db, Game

# Define time zones
utc = pytz.utc
mountain = pytz.timezone('US/Mountain')

def convert_to_mountain_time(utc_time_str):
    # Parse the time string and assume it's in UTC
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%MZ")
    utc_time = utc.localize(utc_time)
    
    # Convert to Mountain Time
    mt_time = utc_time.astimezone(mountain)
    
    # Return the time as a string in Mountain Time zone
    return mt_time.strftime("%Y-%m-%d %H:%M:%S %Z")

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
def save_scores_to_csv(games, filename):
    if games:
        # Convert the games data into a DataFrame
        df = pd.DataFrame(games)
        
        # Save the DataFrame to a CSV file
        df.to_csv(filename, index=False)
        print(f"Football scores saved to {filename}")
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
    filename = f"football_scores_week{weeknum}.csv"
    save_scores_to_csv(football_scores, filename)

def save_scores_to_db(games, week):
        if games:
            for game in games:                
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