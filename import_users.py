import csv
from Football_Project import create_app, db
from Football_Project.models import User

def import_users_from_csv(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            new_user = User(
                id=int(row['id']),
                username=row['username'],
                password=row['password'],  # Already hashed
                email=row['email'],
                is_admin=bool(int(row['is_admin']))
            )
            db.session.add(new_user)
        db.session.commit()
        print("Users imported successfully.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        import_users_from_csv('import_users.csv')
