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
from .utils import auto_fetch_scores, fetch_and_cache_scores

# 🔽 ADD THESE IMPORTS
from .utils import get_current_week
# helper modules you’ll add below
from .services import attempt_import_odds, is_week_odds_complete
from .services import send_admin_email
from .services.sms_helpers import send_sms
from .models import User  # make sure your User model has a phone field
load_dotenv()

# Global scheduler (Mountain time)
scheduler = BackgroundScheduler(timezone=timezone('US/Mountain'))
migrate = Migrate()
csrf = CSRFProtect()

def sms_reminders_job_with_context(app):
    with app.app_context():
        week = get_current_week()
        # Replace with actual DB query: users who have picks left
        targets = []  # e.g., User.query.filter(...).all()
        for user in targets:
            try:
                send_sms(
                    user.phone,
                    f"Reminder: Set your picks for Week {week} before kickoff!",
                    tag=f"wk{week}_reminder",
                )
            except Exception as e:
                app.logger.exception(f"SMS send failed for {user.id}: {e}")

def auto_fetch_scores_with_context(app):
    with app.app_context():
        auto_fetch_scores()

def fetch_and_cache_scores_with_context(app):
    with app.app_context():
        fetch_and_cache_scores()

# 🔽 ADD: odds jobs wrapped with app context
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
        else:  # error
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
    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///picks.db')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'password')
    app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY', 'csrf-key-value')

    # Init extensions
    db.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection
    
    # Init migrations
    migrations_dir = os.path.join(app.root_path, "migrations")  # Football_Project/migrations
    migrate.init_app(app, db, directory=migrations_dir)

    # Auth
    login_manager = LoginManager()
    login_manager.init_app(app)
    # 🚨 point Flask-Login at the new login view
    login_manager.login_view = "auth.login"      # was 'main.login'
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .auth import auth_bp          # ← add this import
    app.register_blueprint(auth_bp)    # ← and register it

    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Start APScheduler only for the running web app (not CLI / migrations)
    disable_sched = os.environ.get("DISABLE_APSCHEDULER") == "1"
    is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    if not disable_sched:
        if (is_reloader_child or os.environ.get("FLASK_ENV") != "development") and not scheduler.running:
            scheduler.remove_all_jobs(jobstore='default')

            # existing every-5-min jobs
            scheduler.add_job(
                auto_fetch_scores_with_context, 'cron',
                args=[app], day_of_week='mon,tue,wed,thu,fri,sat,sun',
                hour='0-23', minute='*/5',
                id="auto_fetch_scores_job", replace_existing=True
            )
            scheduler.add_job(
                fetch_and_cache_scores_with_context, 'cron',
                args=[app], day_of_week='mon,tue,wed,thu,fri,sat,sun',
                hour='0-23', minute='*/5',
                id="fetch_and_cache_scores_job", replace_existing=True
            )

            # 🔽 ADD: odds retry windows (Mountain time)
            scheduler.add_job(
                odds_window_job_with_context, 'cron',
                args=[app, 'TueAM'], day_of_week='tue', hour=7, minute=0,
                id="odds_tue_am", replace_existing=True
            )
            scheduler.add_job(
                odds_window_job_with_context, 'cron',
                args=[app, 'TuePM'], day_of_week='tue', hour=19, minute=0,
                id="odds_tue_pm", replace_existing=True
            )
            scheduler.add_job(
                odds_window_job_with_context, 'cron',
                args=[app, 'WedAM'], day_of_week='wed', hour=7, minute=0,
                id="odds_wed_am", replace_existing=True
            )
            scheduler.add_job(
                odds_window_job_with_context, 'cron',
                args=[app, 'WedPM'], day_of_week='wed', hour=19, minute=0,
                id="odds_wed_pm", replace_existing=True
            )
            # 🔽 ADD: escalation Thursday morning if still not complete
            scheduler.add_job(
                odds_escalation_job_with_context, 'cron',
                args=[app], day_of_week='thu', hour=7, minute=0,
                id="odds_escalation", replace_existing=True
            )

            # Scheduler to remind users of the picks
            scheduler.add_job(
            func=lambda: sms_reminders_job_with_context(app),
            trigger="cron",
            day_of_week="thu,sun,mon",
            hour=16,   # 4 PM Mountain
            minute=0,
            id="sms_reminders_cron",
        )

            scheduler.start()

    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)
    return app
