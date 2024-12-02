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
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler

def auto_fetch_scores_with_context(app):
    """Wrapper for auto_fetch_scores to run with the app context."""
    with app.app_context():
        auto_fetch_scores()

def fetch_and_cache_scores_with_context(app):
    """Wrapper for fetch_and_cache_scores to run with the app context."""
    with app.app_context():
        fetch_and_cache_scores()

# Define the global variable to track scheduler state
scheduler_started = False

# Global Scheduler Definition
scheduler = BackgroundScheduler(timezone=timezone('US/Mountain'))

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

    # Start the scheduler only once
    global scheduler_started
    if not scheduler_started and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler_started = True

        # Remove all existing jobs (if any)
        scheduler.remove_all_jobs(jobstore='default')

        # Add jobs to run every 5 minutes during active game times
        scheduler.add_job(
            lambda: auto_fetch_scores_with_context(app),
            'cron',
            day_of_week='sun, mon, thu, fri, sat',
            hour='5-23',
            minute='*/5',
            id="auto_fetch_scores_job",
            replace_existing=True
        )

        scheduler.add_job(
            lambda: fetch_and_cache_scores_with_context(app),
            'cron',
            day_of_week='sun, mon, thu, fri, sat',
            hour='5-23',
            minute='*/5',
            id="fetch_and_cache_scores_job",
            replace_existing=True
        )

        scheduler.start()

    # Ensure the scheduler shuts down properly on app exit
    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)

    return app