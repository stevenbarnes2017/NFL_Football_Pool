from Football_Project import create_app, db
app = create_app()
with app.app_context():
    try:
        db.drop_all()
        db.create_all()
        print("Database tables created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
  