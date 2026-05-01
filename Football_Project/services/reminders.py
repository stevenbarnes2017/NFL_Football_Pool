from datetime import timedelta
from zoneinfo import ZoneInfo

from flask import current_app

from Football_Project.extensions import db
from Football_Project.models import Game, PoolGroup, GroupMember, ReminderJob, User, Settings
from Football_Project.services.season import get_current_season_context


MT = ZoneInfo("America/Denver")


def active_groups():
    return PoolGroup.query.filter_by(is_active=True).all()


def get_week_games(season_year, season_type, week):
    return (
        Game.query
        .filter_by(
            season_year=season_year,
            season_type=season_type,
            week=week,
        )
        .order_by(Game.commence_time_mt.asc())
        .all()
    )


def upsert_reminder(group_id, season_year, season_type, week, reminder_type, channel, scheduled_for):
    existing = ReminderJob.query.filter_by(
        group_id=group_id,
        season_year=season_year,
        season_type=season_type,
        week=week,
        reminder_type=reminder_type,
        channel=channel,
    ).first()

    if existing:
        existing.scheduled_for = scheduled_for
        existing.status = "pending" if existing.status in ("pending", "failed") else existing.status
        return existing

    job = ReminderJob(
        group_id=group_id,
        season_year=season_year,
        season_type=season_type,
        week=week,
        reminder_type=reminder_type,
        channel=channel,
        scheduled_for=scheduled_for,
        status="pending",
    )
    db.session.add(job)
    return job


def plan_current_week_reminders():
    settings = Settings.query.first()
    if not settings:
        current_app.logger.warning("[REMINDERS] No Settings row found; skipping reminder planning")
        return

    season_year = settings.season_year
    season_type = settings.season_type
    week = settings.current_week

    games = get_week_games(season_year, season_type, week)

    if not games:
        current_app.logger.info(f"[REMINDERS] No games found for {season_type} {season_year} week={week}")
        return

    # 👇 THIS LINE ALREADY EXISTS
    first_kickoff = games[0].commence_time_mt

    # 👇 ADD THIS BLOCK RIGHT HERE
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    if first_kickoff <= now:
        current_app.logger.warning(
            f"[REMINDERS] First kickoff already passed for {season_type} {season_year} week={week}; skipping"
        )
        return

    # 👇 existing loop continues
    for group in active_groups():
        # Main weekly email
        upsert_reminder(
            group_id=group.id,
            season_year=season_year,
            season_type=season_type,
            week=week,
            reminder_type="weekly_make_picks",
            channel="email",
            scheduled_for=first_kickoff - timedelta(hours=24),
        )

        # Last chance email
        upsert_reminder(
            group_id=group.id,
            season_year=season_year,
            season_type=season_type,
            week=week,
            reminder_type="last_chance",
            channel="email",
            scheduled_for=first_kickoff - timedelta(hours=3),
        )

        # Later when Twilio is ready
        upsert_reminder(
            group_id=group.id,
            season_year=season_year,
            season_type=season_type,
            week=week,
            reminder_type="last_chance",
            channel="sms",
            scheduled_for=first_kickoff - timedelta(hours=3),
        )

    db.session.commit()

    current_app.logger.info(
        f"[REMINDERS] Planned reminders for {season_type} {season_year} week={week} groups={len(active_groups())}"
    )