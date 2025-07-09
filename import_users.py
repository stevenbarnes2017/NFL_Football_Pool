import pandas as pd
from Football_Project import create_app, db
from Football_Project.models import User
from datetime import datetime

# Replace 'your_application' with the actual name of your Flask app's module

def import_users_from_csv(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Create a new User instance
            new_user = User(
                id=int(row['id']),
                username=row['username'],
                password=row['password'],  # Assuming this is a hashed password
                email=row['email'],
                is_admin=bool(int(row['is_admin']))
            )
            # Add to the database session
            db.session.add(new_user)

        # Commit the session to the database
        db.session.commit()
        print("Users imported successfully.")

if __name__ == "__main__":
    import_users_from_csv('import_users.csv')