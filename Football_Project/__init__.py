import os
import atexit
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from dotenv import load_dotenv

from .extensions import db
from .models import User
from .utils import auto_fetch_scores, fetch_and_cache_scores

# Load environment variables as early as possible
load_dotenv()

# Global scheduler
scheduler = BackgroundScheduler(timezone=timezone('US/Mountain'))


def auto_fetch_scores_with_context(app):
    with app.app_context():
        auto_fetch_scores()


def fetch_and_cache_scores_with_context(app):
    with app.app_context():
        fetch_and_cache_scores()


def create_app():
    app = Flask(__name__)

    # App configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///picks.db')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'password')

    # Point Migrate to the correct directory (inside your package)
    migrations_dir = os.path.join(app.root_path, "migrations")
    Migrate(app, db, directory=migrations_dir)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Start scheduled jobs only if not already scheduled
    if not scheduler.get_jobs():
        scheduler.remove_all_jobs(jobstore='default')

        scheduler.add_job(
            auto_fetch_scores_with_context,
            'cron',
            args=[app],
            day_of_week='sun, mon, tue, thu, fri, sat',
            hour='1-23',
            minute='*/5',
            id="auto_fetch_scores_job",
            replace_existing=True
        )

        scheduler.add_job(
            fetch_and_cache_scores_with_context,
            'cron',
            args=[app],
            day_of_week='sun, mon, tue, thu, fri, sat',
            hour='1-23',
            minute='*/5',
            id="fetch_and_cache_scores_job",
            replace_existing=True
        )

        scheduler.start()  # Enable if you want to start it right away

    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)

    return app
