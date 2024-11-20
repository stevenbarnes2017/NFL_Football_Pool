import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import User
from .extensions import db
from .utils import auto_fetch_scores, fetch_and_cache_scores
import atexit
import logging
# Import the Mountain timezone
from pytz import timezone


# Define the global variable to track scheduler state
scheduler_started = False
scheduler = BackgroundScheduler()

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

    # Register blueprints
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Define the user_loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    global scheduler_started

    # Set the scheduler timezone to Mountain Time
    mountain_tz = timezone('US/Mountain')
    scheduler = BackgroundScheduler(timezone=mountain_tz)
    # Scheduler Job Initialization
    #job_id = "auto_fetch_scores_job"
    # Check if the app is running in the main process (to avoid duplicate scheduler instances)
    if not scheduler_started and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    # Clear existing jobs
        scheduler.remove_all_jobs(jobstore='default')

    # Define game days and hours
    game_days = ['thu', 'fri', 'sat', 'sun', 'mon']
    game_hours = {
        'thu': {'start': 17, 'end': 23},  # 7 PM - 11 PM MT
        'fri': {'start': 5, 'end': 23},  # Friday evening games
        'sat': {'start': 5, 'end': 23},  # Saturday all-day games
        'sun': {'start': 5, 'end': 23},  # Sunday afternoon/evening
        'mon': {'start': 17, 'end': 23}   # Monday evening games
    }

    # Add jobs for each game day
    for day in game_days:
        hours = game_hours.get(day, {})
        scheduler.add_job(
            fetch_and_cache_scores, 
            'cron', 
            day_of_week=day, 
            hour=f"{hours['start']}-{hours['end']}", 
            minute='*/5', 
            id=f"fetch_and_cache_scores_{day}", 
            replace_existing=True
        )
        scheduler.add_job(
            auto_fetch_scores, 
            'cron', 
            day_of_week=day, 
            hour=f"{hours['start']}-{hours['end']}", 
            minute='*/5', 
            id=f"auto_fetch_scores_{day}", 
            replace_existing=True
        )
    # Ensure the scheduler shuts down properly on app exit
    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)

    return app
