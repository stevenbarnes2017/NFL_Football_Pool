# __init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import User
from .extensions import db
from .utils import scheduler, auto_fetch_scores  # Import scheduler and task
import atexit
import logging  # Ensure logging is imported at the top

# Track scheduler state globally
scheduler_started = False

def create_app():
    app = Flask(__name__)

    # App configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///picks.db'
    app.config['SECRET_KEY'] = 'password'
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize the login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints (after initializing extensions)
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Define the user_loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    global scheduler_started

    # Scheduler Job Initialization
    job_id = "auto_fetch_scores_job"
    if not scheduler_started:
        # Remove all jobs to avoid duplicates on restart
        scheduler.remove_all_jobs()

        # Add the job if not already present
        scheduler.add_job(auto_fetch_scores, 'interval', minutes=1, id=job_id)
        print(f"Job {job_id} added to scheduler.")

        # Start the scheduler and mark it as started
        scheduler.start()
        scheduler_started = True
        print("Scheduler started.")

    # Ensure scheduler shuts down properly on app exit
    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)

    return app
