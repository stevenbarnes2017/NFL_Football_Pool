# Football_Project/__init__.py
import os
import atexit
from flask import Flask, session
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from dotenv import load_dotenv
from Football_Project.time_utils import fmt_mt
from sqlalchemy.exc import OperationalError  # ✅ NEW
import sys
from .extensions import db
from .models import User, JobRun
from .utils import auto_fetch_scores, fetch_and_cache_scores
from .services import attempt_import_odds, is_week_odds_complete, send_admin_email
from Football_Project.services.season import get_current_week
from .services.sms_helpers import sms_week_reminder_job, schedule_first_kick_sms_for_week
from Football_Project.services.odds_care import attempt_import_odds, is_week_odds_complete


load_dotenv()

# Global scheduler (Mountain time)
scheduler = BackgroundScheduler(timezone=timezone("US/Mountain"))
migrate = Migrate()
csrf = CSRFProtect()

from Football_Project.services.season import get_current_season_context
from Football_Project.services.schedule_service import update_schedule
from Football_Project.models import JobRun
from Football_Project.extensions import db

def _is_migration_command() -> bool:
    return (
        "db" in sys.argv
        or "alembic" in sys.argv
        or os.getenv("SKIP_SCHEDULER") == "1"
    )

def schedule_update_job_with_context(app):
    with app.app_context():
        try:
            season_year, st = get_current_season_context()
            st_upper = (st or "REG").upper()
            st_int = {"PRE": 1, "REG": 2, "POST": 3}.get(st_upper, 2)

            # sensible week ranges
            week_end = 5 if st_upper == "POST" else (4 if st_upper == "PRE" else 18)

            result = update_schedule(
                season_year=season_year,
                season_type=st_int,
                week_start=1,
                week_end=week_end
            )

            db.session.add(JobRun(
                job_name="schedule_update",
                ok=(result.get("failed_weeks", 0) == 0),
                inserted=result.get("inserted", 0),
                updated=result.get("updated", 0),
                unchanged=result.get("unchanged", 0),
                failed_weeks=result.get("failed_weeks", 0),
                message=f"{season_year} {st_upper} W1-{week_end}"
            ))
            db.session.commit()

            print(f"[SCHEDULE] Auto-run OK: {result}")

        except Exception as e:
            db.session.rollback()
            db.session.add(JobRun(
                job_name="schedule_update",
                ok=False,
                message=str(e)[:250]
            ))
            db.session.commit()
            print(f"[SCHEDULE] Auto-run FAILED: {e}")

        finally:
            db.session.remove()


def auto_fetch_scores_with_context(app):
    with app.app_context():
        try:
            auto_fetch_scores()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.remove()  # ✅ NEW: prevents stale/broken sessions


def fetch_and_cache_scores_with_context(app):
    with app.app_context():
        try:
            fetch_and_cache_scores()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.remove()  # ✅ NEW


def odds_window_job_with_context(app, label: str):
    from flask import current_app
    from .extensions import db
    from .models import Settings
    from .services.odds_care import (
        games_count_for_week,
        is_week_odds_complete,
        attempt_import_odds,
    )
    from .services import send_admin_email

    with app.app_context():
        try:
            settings = Settings.query.first()
            if not settings:
                current_app.logger.warning(f"[odds] {label} no Settings row found; skipping")
                return

            week = settings.current_week
            season_year = settings.season_year
            season_type = settings.season_type

            if games_count_for_week(week, season_year, season_type) == 0:
                current_app.logger.info(
                    f"[odds] {label} no games for {season_type} {season_year} week={week}; skipping"
                )
                return

            if is_week_odds_complete(week, season_year, season_type):
                current_app.logger.info(
                    f"[odds] {label} {season_type} {season_year} week={week} already complete; skipping"
                )
                return

            status, csv_bytes, details = attempt_import_odds(
                week=week,
                season_year=season_year,
                season_type=season_type
            )

            current_app.logger.info(
                f"[odds] {label} {season_type} {season_year} week={week} status={status} details={details}"
            )

            subject_prefix = f"[Odds] {season_type} {season_year} Week {week}"

            if status == "success":
                send_admin_email(
                    subject=f"{subject_prefix} SUCCESS ({label})",
                    html=f"<p>Imported spreads for {season_type} {season_year} week {week}.</p><pre>{details}</pre>",
                    attachment_bytes=csv_bytes,
                    filename=f"odds_{season_type.lower()}_{season_year}_week_{week}.csv"
                )
            elif status == "not_ready":
                send_admin_email(
                    subject=f"{subject_prefix} NOT READY ({label})",
                    html=f"<pre>{details}</pre>"
                )
            else:
                send_admin_email(
                    subject=f"{subject_prefix} ERROR ({label})",
                    html=f"<pre>{details}</pre>"
                )

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.remove()


def odds_escalation_job_with_context(app):
    from flask import current_app
    with app.app_context():
        try:
            settings = Settings.query.first()
            week = settings.current_week
            season_year = settings.season_year
            season_type = settings.season_type

            # ✅ Prevent false escalation if schedule isn't loaded yet
            if games_count_for_week(week, season_year, season_type) == 0:
                current_app.logger.info(
                    f"[odds] No games found for {season_type} {season_year} week {week}; skipping escalation"
                )
                return

            if not is_week_odds_complete(week, season_year, season_type):
                current_app.logger.warning(
                    f"[odds] {season_type} {season_year} Week {week} still not ready; escalating"
                )
                send_admin_email(
                    subject=f"[Odds] {season_type} {season_year} Week {week} STILL NOT READY",
                    html="<p>Multiple attempts failed. Please investigate.</p>"
                )

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.remove()


def create_app():
    app = Flask(__name__)

    db_url = os.getenv("DATABASE_URL", "sqlite:///picks.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "password")
    app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("WTF_CSRF_SECRET_KEY", "csrf-key-value")

    #fix timezone
    app.jinja_env.filters["fmt_mt"] = fmt_mt

    # ✅ NEW: make Postgres on Render resilient to dropped SSL connections
    # Only apply when using Postgres; SQLite doesn't accept these engine options.
    if db_url.startswith("postgresql://"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,  # seconds
            "pool_size": 5,
            "max_overflow": 10,
            "connect_args": {"sslmode": "require"},
        }

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
        try:
            return db.session.get(User, int(user_id))
        except OperationalError:
            db.session.rollback()
            return None

    @app.context_processor
    def inject_view_as_user():
        view_as_id = session.get("view_as_user_id") or session.get("admin_view_as_user_id")
        view_as_user = None

        if current_user.is_authenticated and getattr(current_user, "is_admin", False) and view_as_id:
            view_as_user = db.session.get(User, int(view_as_id))

        return {"view_as_user": view_as_user, "view_as_id": view_as_id}
    

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
                    try:
                        settings = Settings.query.first()
                        if not settings:
                            app.logger.warning("[SMS] Settings missing; skipping SMS reschedule.")
                            return

                        week = get_current_week(settings.season_year, settings.season_type)
                        schedule_first_kick_sms_for_week(app, week, scheduler)
                        db.session.commit()

                    except Exception:
                        db.session.rollback()
                        raise
                    finally:
                        db.session.remove()

            # Run once at startup
            reschedule_current_week_sms(app)

            # Safety: re-evaluate each morning in case week/kickoff changes
            scheduler.add_job(
                func=lambda: reschedule_current_week_sms(app),
                trigger="cron",
                hour=3, minute=5,  # Mountain time
                id="sms_rescheduler_daily",
                replace_existing=True,
            )

            scheduler.add_job(
                func=lambda: schedule_update_job_with_context(app),
                trigger="cron",
                day_of_week="tue",
                hour=6, minute=20,
                id="schedule_update_tue_am",
                replace_existing=True,
            )

            scheduler.start()

    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)
    return app
