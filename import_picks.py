import pandas as pd
from Football_Project import create_app, db
from Football_Project.models import Pick
from datetime import datetime

# Create the application context
app = create_app()
app.app_context().push()

# Load the CSV data
df = pd.read_csv('import_picks_week1_week2.csv')

# Iterate over each row in the DataFrame and insert it into the database
for index, row in df.iterrows():    
        new_pick = Pick(
            user_id=row['user_id'],
            game_id=row['game_id'],
            team_picked=row['team_picked'],
            confidence=row['confidence'],
            week=row['week']
        )

        # Add the new game to the session
        db.session.add(new_pick)

# Commit the session to insert all games into the database
db.session.commit()

print("Historical odds have been successfully loaded into the database.")
