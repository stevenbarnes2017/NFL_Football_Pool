import pandas as pd
from Football_Project import create_app, db
from Football_Project.models import Pick
from flask import Flask

# Create the application context
app = create_app()

# Use Flask app context to work with the database
with app.app_context():
    # Load the CSV data using pandas
    try:
        df = pd.read_csv('import_picks_week11.csv')
        print(df.head())  # Debug: Print the first few rows to ensure CSV is loaded properly
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit()

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        try:
            # Debug: Print row to ensure proper data access
            print(f"Processing row {index}: {row.to_dict()}")

            # Create a new Pick object from the row data
            new_pick = Pick(
                user_id=row['user_id'],         # Ensure the column names match the CSV header
                game_id=row['game_id'],
                team_picked=row['team_picked'],
                confidence=row['confidence'],
                week=row['week']
            )

            # Add the new pick to the session
            db.session.add(new_pick)

        except Exception as e:
            print(f"Error inserting row {index}: {e}")
            continue  # Skip this row if there's an error

    # Commit the session to insert all picks into the database
    try:
        db.session.commit()
        print("Picks have been successfully loaded into the database.")
    except Exception as commit_error:
        print(f"Error committing to the database: {commit_error}")
        db.session.rollback()  # Rollback in case of error
