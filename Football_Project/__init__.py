# Football_Project/__init__.py
import os
import atexit
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from dotenv import load_dotenv

from .extensions import db
from .models import User
from .utils import auto_fetch_scores, fetch_and_cache_scores

load_dotenv()

# Global scheduler (Mountain time)
scheduler = BackgroundScheduler(timezone=timezone('US/Mountain'))
migrate = Migrate()  # use init_app pattern

def auto_fetch_scores_with_context(app):
    with app.app_context():
        auto_fetch_scores()

def fetch_and_cache_scores_with_context(app):
    with app.app_context():
        fetch_and_cache_scores()

def create_app():
    app = Flask(__name__)

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///picks.db')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'password')

    # Init DB, then Migrate (point to package migrations dir)
    db.init_app(app)
    migrations_dir = os.path.join(app.root_path, "migrations")  # Football_Project/migrations
    migrate.init_app(app, db, directory=migrations_dir)

    # Auth
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from .admin import admin_bp
    app.register_blueprint(admin_bp)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Start APScheduler only for the running web app (not CLI / migrations)
    disable_sched = os.environ.get("DISABLE_APSCHEDULER") == "1"
    is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"  # true only in dev reloader child

    if not disable_sched:
        # In dev, guard against double-start with reloader; in prod (gunicorn), this var is absent so it runs once.
        if (is_reloader_child or os.environ.get("FLASK_ENV") != "development") and not scheduler.running:
            # Clear any stale jobs and (re)register
            scheduler.remove_all_jobs(jobstore='default')

            # Run every 5 minutes, all days, all hours (including midnight)
            scheduler.add_job(
                auto_fetch_scores_with_context,
                'cron',
                args=[app],
                day_of_week='mon,tue,wed,thu,fri,sat,sun',
                hour='0-23',
                minute='*/5',
                id="auto_fetch_scores_job",
                replace_existing=True
            )
            scheduler.add_job(
                fetch_and_cache_scores_with_context,
                'cron',
                args=[app],
                day_of_week='mon,tue,wed,thu,fri,sat,sun',
                hour='0-23',
                minute='*/5',
                id="fetch_and_cache_scores_job",
                replace_existing=True
            )

            scheduler.start()

    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)
    return app
