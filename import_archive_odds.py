import pandas as pd
from Football_Project import create_app, db
from Football_Project.models import Game
from datetime import datetime

# Create the application context
app = create_app()
app.app_context().push()

# Load the CSV data
df = pd.read_csv('nfl_spreads_week_15.csv')

# Iterate over each row in the DataFrame and insert it into the database
for index, row in df.iterrows():
    # Check if the game already exists to avoid duplicates
    existing_game = Game.query.filter_by(
        home_team=row['home_team'],
        away_team=row['away_team'],
        week=row['week']
    ).first()

    if not existing_game:
        # Create a new Game instance
        new_game = Game(
            week=row['week'],
            home_team=row['home_team'],
            away_team=row['away_team'],
            spread=row['spread'],
            favorite_team=row['favorite_team'],
            commence_time_mt=row['commence_time_mt']
        )

        # Add the new game to the session
        db.session.add(new_game)

# Commit the session to insert all games into the database
db.session.commit()

print("Historical odds have been successfully loaded into the database.")
