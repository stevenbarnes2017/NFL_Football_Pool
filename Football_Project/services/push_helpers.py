from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func

from Football_Project import db
from Football_Project.models import Game
from Football_Project.notifications.service import send_push_notification
from Football_Project.models import User

MT = ZoneInfo("America/Denver")


def schedule_first_kick_sms_for_week(app, week: int, scheduler):
    """
    Schedule a one-time job 2h before first kickoff of 'week'.
    """
    with app.app_context():
        first_dt = (
            db.session.query(func.min(Game.commence_time_mt))
            .filter(Game.week == week)
            .scalar()
        )
        if not first_dt:
            app.logger.info(f"[PUSH] No games found for week {week}; not scheduling.")
            return
        if first_dt.tzinfo is None:
            first_dt = first_dt.replace(tzinfo=ZoneInfo("America/Denver"))

        run_dt_mtn = first_dt.astimezone(MT) - timedelta(hours=2)
        now_mtn = datetime.now(MT)
        job_id = f"push_first_kick_wk_{week}"

        if run_dt_mtn <= now_mtn:
            try:
                scheduler.remove_job(job_id)
            except Exception:
                pass
            app.logger.info(f"[PUSH] Week {week} reminder window already passed ({run_dt_mtn.isoformat()} MT). Not scheduling.")
            return

        scheduler.add_job(
            func=lambda: push_week_reminder_job(app, week),
            trigger="date",
            run_date=run_dt_mtn,
            id=job_id,
            replace_existing=True,
        )
        app.logger.info(f"[PUSH] Scheduled week {week} reminder at {run_dt_mtn.isoformat()} MT.")


def push_week_reminder_job(app):
    with app.app_context():
        users = User.query.all()
        for user in users:
            for subscription in user.notification_subscriptions:
                send_push_notification(
                    subscription,
                    "Sunday Pickems Reminder",
                    f"kickoff is in 2 hours. Make sure your picks are submitted!"
                )