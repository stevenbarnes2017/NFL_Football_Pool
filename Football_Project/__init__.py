import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import User
from .extensions import db
from .utils import auto_fetch_scores
import atexit
import logging

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

    # Scheduler Job Initialization
    job_id = "auto_fetch_scores_job"
    # Check if the app is running in the main process (to avoid duplicate scheduler instances)
    if not scheduler_started and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Clear existing jobs to avoid duplicates
        scheduler.remove_all_jobs(jobstore='default')

        scheduler.add_job(
        auto_fetch_scores, 
        'interval', 
        minutes=1, 
        id="auto_fetch_scores_test",
        replace_existing=True
        )

        # Set cron-based jobs for Sundays, Thursdays, and Mondays
        scheduler.add_job(auto_fetch_scores, 'cron', day_of_week='sun', hour='12-23', minute='*/1', id=job_id, replace_existing=True)
        scheduler.add_job(auto_fetch_scores, 'cron', day_of_week='thu,mon', hour='19-23', minute='*/1', id=job_id, replace_existing=True)
        print(f"Job {job_id} added to scheduler.")

        # Start the scheduler and mark it as started
        scheduler.start()
        scheduler_started = True
        print("Scheduler started.")

    # Ensure the scheduler shuts down properly on app exit
    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)

    return app
