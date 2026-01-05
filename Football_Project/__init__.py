# Football_Project/__init__.py
import os
import atexit
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from dotenv import load_dotenv

from .extensions import db
from .models import User
from .utils import auto_fetch_scores, fetch_and_cache_scores, get_current_week
from .services import attempt_import_odds, is_week_odds_complete, send_admin_email
from .services.sms_helpers import sms_week_reminder_job, schedule_first_kick_sms_for_week


load_dotenv()

# Global scheduler (Mountain time)
scheduler = BackgroundScheduler(timezone=timezone("US/Mountain"))
migrate = Migrate()
csrf = CSRFProtect()


def auto_fetch_scores_with_context(app):
    with app.app_context():
        auto_fetch_scores()


def fetch_and_cache_scores_with_context(app):
    with app.app_context():
        fetch_and_cache_scores()


def odds_window_job_with_context(app, label: str):
    from flask import current_app
    with app.app_context():
        week = get_current_week()
        if is_week_odds_complete(week):
            current_app.logger.info(f"[odds] Week {week} already complete; skipping {label}")
            return
        status, csv_bytes, details = attempt_import_odds(week)
        current_app.logger.info(f"[odds] {label} week={week} status={status} details={details}")
        if status == "success":
            send_admin_email(
                subject=f"[Odds] Week {week} SUCCESS ({label})",
                html=f"<p>Imported spreads for week {week}.</p><pre>{details}</pre>",
                attachment_bytes=csv_bytes,
                filename=f"odds_week_{week}.csv"
            )
        elif status == "not_ready":
            send_admin_email(
                subject=f"[Odds] Week {week} NOT READY ({label})",
                html=f"<pre>{details}</pre>"
            )
        else:
            send_admin_email(
                subject=f"[Odds] Week {week} ERROR ({label})",
                html=f"<pre>{details}</pre>"
            )


def odds_escalation_job_with_context(app):
    from flask import current_app
    with app.app_context():
        week = get_current_week()
        if not is_week_odds_complete(week):
            current_app.logger.warning(f"[odds] Week {week} still not ready; escalating")
            send_admin_email(
                subject=f"[Odds] Week {week} STILL NOT READY",
                html="<p>Multiple attempts failed. Please investigate.</p>"
            )


def create_app():
    app = Flask(__name__)

    db_url = os.getenv("DATABASE_URL", "sqlite:///picks.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    #app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///picks.db")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "password")
    app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("WTF_CSRF_SECRET_KEY", "csrf-key-value")

    # Init extensions
    db.init_app(app)
    csrf.init_app(app)

    # Init migrations (explicit directory to match your layout)
    migrations_dir = os.path.join(app.root_path, "migrations")
    migrate.init_app(app, db, directory=migrations_dir)

    # Auth
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    # --- APScheduler wiring ---
    disable_sched = os.environ.get("DISABLE_APSCHEDULER") == "1"
    is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    if not disable_sched:
        # Only start the scheduler in the serving process (not on flask CLI commands)
        if (is_reloader_child or os.environ.get("FLASK_ENV") != "development") and not scheduler.running:
            scheduler.remove_all_jobs(jobstore="default")

            # Scores/odds recurring jobs
            scheduler.add_job(
                auto_fetch_scores_with_context, "cron",
                args=[app], day_of_week="mon,tue,wed,thu,fri,sat,sun",
                hour="0-23", minute="*/5",
                id="auto_fetch_scores_job", replace_existing=True
            )
            scheduler.add_job(
                fetch_and_cache_scores_with_context, "cron",
                args=[app], day_of_week="mon,tue,wed,thu,fri,sat,sun",
                hour="0-23", minute="*/5",
                id="fetch_and_cache_scores_job", replace_existing=True
            )

            # Odds retry windows
            scheduler.add_job(
                odds_window_job_with_context, "cron",
                args=[app, "TueAM"], day_of_week="tue", hour=7, minute=0,
                id="odds_tue_am", replace_existing=True
            )
            scheduler.add_job(
                odds_window_job_with_context, "cron",
                args=[app, "TuePM"], day_of_week="tue", hour=19, minute=0,
                id="odds_tue_pm", replace_existing=True
            )
            scheduler.add_job(
                odds_window_job_with_context, "cron",
                args=[app, "WedAM"], day_of_week="wed", hour=7, minute=0,
                id="odds_wed_am", replace_existing=True
            )
            scheduler.add_job(
                odds_window_job_with_context, "cron",
                args=[app, "WedPM"], day_of_week="wed", hour=19, minute=0,
                id="odds_wed_pm", replace_existing=True
            )
            scheduler.add_job(
                odds_escalation_job_with_context, "cron",
                args=[app], day_of_week="thu", hour=7, minute=0,
                id="odds_escalation", replace_existing=True
            )

            # --- SMS: schedule 2h before first kickoff of current week ---
            def reschedule_current_week_sms(app):
                """Schedules (or reschedules) the first-kickoff reminder for the current week."""
                with app.app_context():
                    week = get_current_week()  # needs app context for DB session
                    schedule_first_kick_sms_for_week(app, week, scheduler)
            from pytz import timezone as pytz_timezone
            # Run once at startup
            reschedule_current_week_sms(app)
            
            from datetime import datetime, timedelta
            
            # Safety: re-evaluate each morning in case week/kickoff changes
            scheduler.add_job(
                func=lambda: reschedule_current_week_sms(app),   # pass app; wrap in lambda
                trigger="cron",
                hour=3, minute=5,                                 # Mountain time
                id="sms_rescheduler_daily",
                replace_existing=True,
            )

            scheduler.start()

    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)
    return app
