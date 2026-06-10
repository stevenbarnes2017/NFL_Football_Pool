from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo

from flask import current_app

from Football_Project.extensions import db
from Football_Project.models import Game, PoolGroup, GroupMember, ReminderJob, User, Settings
from Football_Project.services.season import get_current_season_context
from Football_Project.services.email_helpers import send_user_email

MAX_REMINDER_LATENESS = timedelta(hours=6)
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


def send_reminder_email(job):
    group = PoolGroup.query.get(job.group_id)

    if not group:
        raise Exception(f"group_id={job.group_id} not found")

    members = GroupMember.query.filter_by(group_id=group.id, is_active=True).all()

    users = []
    for m in members:
        user = User.query.get(m.user_id)
        if user and user.email:
            users.append(user)

    if not users:
        raise Exception(f"No users found for group_id={group.id}")

    if job.reminder_type == "weekly_make_picks":
        subject = f"Week {job.week} - Make Your Picks"
        body = f"""
        <p>Week {job.week} games are coming up.</p>
        <p>Make your picks before kickoff.</p>
        """
    elif job.reminder_type == "last_chance":
        subject = f"Week {job.week} - Last Chance to Pick"
        body = f"""
        <p>Reminder: Week {job.week} locks soon.</p>
        <p>Get your picks in before kickoff.</p>
        """
    else:
        subject = f"Week {job.week} Reminder"
        body = "<p>Reminder to check your picks.</p>"

    sent_count = 0

    for user in users:
        try:
            send_user_email(
                to_email=user.email,
                subject=subject,
                html=body,
            )
            sent_count += 1
        except Exception as e:
            current_app.logger.warning(
                f"[REMINDERS] Failed to send email to {user.email}: {e}"
            )

    current_app.logger.info(
        f"[REMINDERS] Email sent job_id={job.id} group_id={group.id} users={sent_count}"
    )


def dispatch_due_reminders(limit: int = 25):
    now = datetime.now(timezone.utc)

    jobs = (
        ReminderJob.query
        .filter(ReminderJob.status == "pending")
        .filter(ReminderJob.scheduled_for <= now)
        .order_by(ReminderJob.scheduled_for.asc())
        .limit(limit)
        .all()
    )

    if not jobs:
        current_app.logger.info("[REMINDERS] No due reminders found")
        return {"sent": 0, "skipped": 0, "failed": 0, "expired": 0}

    results = {"sent": 0, "skipped": 0, "failed": 0, "expired": 0}

    for job in jobs:
        # --- Staleness guard: never send reminders that are too far past due ---
        scheduled = job.scheduled_for
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)

        if now - scheduled > MAX_REMINDER_LATENESS:
            job.status = "expired"
            job.details = f"expired: scheduled_for {scheduled.isoformat()} exceeded max lateness {MAX_REMINDER_LATENESS}"
            results["expired"] += 1
            current_app.logger.info(
                f"[REMINDERS] Expired stale job_id={job.id} week={job.week} "
                f"type={job.reminder_type} scheduled_for={scheduled.isoformat()}"
            )
            continue
        # --- end guard ---

        try:
            if job.channel == "email":
                send_reminder_email(job)
            elif job.channel == "sms":
                current_app.logger.info(
                    f"[REMINDERS] SMS reminder skipped for job_id={job.id}; SMS not enabled yet"
                )
                job.status = "skipped"
                job.details = "SMS not enabled yet"
                results["skipped"] += 1
                continue
            else:
                job.status = "skipped"
                job.details = f"Unknown channel: {job.channel}"
                results["skipped"] += 1
                continue

            job.status = "sent"
            job.sent_at = now
            job.details = "sent successfully"
            results["sent"] += 1

        except Exception as e:
            job.status = "failed"
            job.details = str(e)[:500]
            results["failed"] += 1
            current_app.logger.exception(f"[REMINDERS] Failed job_id={job.id}")

    db.session.commit()

    current_app.logger.info(f"[REMINDERS] Dispatch complete {results}")
    return results


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

    first_kickoff = games[0].commence_time_mt

    now = datetime.now(timezone.utc)

    if first_kickoff <= now:
        current_app.logger.warning(
            f"[REMINDERS] First kickoff already passed for {season_type} {season_year} week={week}; skipping"
        )
        return

    for group in active_groups():
        # Main weekly email - 24 hours before first kickoff
        upsert_reminder(
            group_id=group.id,
            season_year=season_year,
            season_type=season_type,
            week=week,
            reminder_type="weekly_make_picks",
            channel="email",
            scheduled_for=first_kickoff - timedelta(hours=24),
        )

        # Last chance email - 3 hours before first kickoff
        upsert_reminder(
            group_id=group.id,
            season_year=season_year,
            season_type=season_type,
            week=week,
            reminder_type="last_chance",
            channel="email",
            scheduled_for=first_kickoff - timedelta(hours=3),
        )

        # SMS - when Twilio is ready
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