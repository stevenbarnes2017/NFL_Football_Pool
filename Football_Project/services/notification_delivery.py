"""Email/push delivery queue for in-app notifications.

Web requests call enqueue_deliveries(), which only inserts rows. The
scheduler process calls process_due_deliveries() every few seconds and
does the slow provider calls (Brevo, web push) there, so a burst of
notifications can't block the website or its health checks.

Delivery is at-least-once: a row is claimed (pending -> sending) with a
conditional UPDATE so only one worker sends it, and a claim that is never
finished (process killed mid-send) is retried after CLAIM_LEASE. In that
rare case a recipient can get the same email twice.
"""

import time
from datetime import datetime, timedelta

import requests
from flask import current_app

from Football_Project.extensions import db
from Football_Project.models import (
    Notification,
    NotificationDelivery,
    NotificationSubscription,
    User,
)

MAX_ATTEMPTS = 5
# Wait before attempt 2, 3, 4, 5.
RETRY_BACKOFF = (
    timedelta(minutes=1),
    timedelta(minutes=5),
    timedelta(minutes=15),
    timedelta(hours=1),
)
# A "sending" row older than this was abandoned by a killed process.
CLAIM_LEASE = timedelta(minutes=10)
# Don't email people about something from yesterday (e.g. scheduler was down).
MAX_AGE = timedelta(hours=24)

DEFAULT_BATCH = 50
DEFAULT_TIME_BUDGET_SECONDS = 40


def enqueue_deliveries(notifications, *, email_subject, email_html_fn):
    """Queue email + push for freshly created (flushed) notifications.

    Does not commit, so the rows are saved in the same transaction as the
    notifications themselves. Preferences are checked here and again
    right before sending.
    """
    counts = {"email": 0, "push": 0}
    if not notifications:
        return counts

    user_ids = {n.user_id for n in notifications}
    users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}
    subs_by_user = {}
    for sub in NotificationSubscription.query.filter(
        NotificationSubscription.user_id.in_(user_ids),
        NotificationSubscription.active == True,  # noqa: E712
    ).all():
        subs_by_user.setdefault(sub.user_id, []).append(sub)

    for note in notifications:
        user = users.get(note.user_id)
        if not user:
            continue

        # Push: every active subscription, same policy as the reminder pushes.
        for sub in subs_by_user.get(user.id, []):
            db.session.add(NotificationDelivery(
                notification_id=note.id,
                channel="push",
                subscription_id=sub.id,
                status="pending",
            ))
            counts["push"] += 1

        # Email: respect the existing email opt-out toggle.
        if user.email and user.email_notifications_enabled:
            db.session.add(NotificationDelivery(
                notification_id=note.id,
                channel="email",
                status="pending",
                email_subject=(email_subject or "")[:300],
                email_html=email_html_fn(user, note),
            ))
            counts["email"] += 1

    return counts


def _retry_or_fail(delivery, error, now):
    delivery.last_error = error[:300]
    if delivery.attempts >= MAX_ATTEMPTS:
        delivery.status = "failed"
        return "failed"
    delivery.status = "pending"
    delivery.next_attempt_at = now + RETRY_BACKOFF[min(delivery.attempts, len(RETRY_BACKOFF)) - 1]
    return "retry"


def _send_email(delivery, note, now):
    from Football_Project.services.email_helpers import send_user_email

    user = db.session.get(User, note.user_id)
    if not user or not user.email or not user.email_notifications_enabled:
        delivery.status = "skipped"
        delivery.last_error = "email turned off"
        return "skipped"

    try:
        send_user_email(
            to_email=user.email,
            subject=delivery.email_subject,
            html=delivery.email_html,
        )
    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status is not None and 400 <= status < 500 and status != 429:
            delivery.status = "failed"
            delivery.last_error = f"rejected status={status}"
            return "failed"
        return _retry_or_fail(delivery, f"http status={status}", now)
    except Exception as e:
        # Timeouts, connection errors, missing API key, ...
        return _retry_or_fail(delivery, f"error={type(e).__name__}", now)

    delivery.status = "sent"
    delivery.sent_at = now
    note.email_sent_at = now
    return "sent"


def _send_push(delivery, note, now):
    from Football_Project.notifications.service import (
        PUSH_GONE,
        PUSH_REJECTED,
        PUSH_SENT,
        push_with_status,
    )

    sub = db.session.get(NotificationSubscription, delivery.subscription_id)
    if not sub or not sub.active:
        delivery.status = "skipped"
        delivery.last_error = "subscription inactive"
        return "skipped"

    result = push_with_status(sub, note.title, note.body or "")
    if result == PUSH_SENT:
        delivery.status = "sent"
        delivery.sent_at = now
        note.push_sent_at = now
        return "sent"
    if result == PUSH_GONE:
        delivery.status = "skipped"
        delivery.last_error = "subscription expired"
        return "expired"
    if result == PUSH_REJECTED:
        delivery.status = "failed"
        delivery.last_error = "rejected by push service"
        return "failed"
    return _retry_or_fail(delivery, "push service unavailable", now)


def _claim(delivery_id, now):
    """Atomically take one due row. False if another worker got it first."""
    claimed = (
        NotificationDelivery.query
        .filter(
            NotificationDelivery.id == delivery_id,
            NotificationDelivery.status == "pending",
        )
        .update(
            {
                "status": "sending",
                "claimed_at": now,
                "attempts": NotificationDelivery.attempts + 1,
            },
            synchronize_session=False,
        )
    )
    db.session.commit()
    return claimed == 1


def _release_abandoned(now):
    """Put rows whose sender died mid-send back in the queue."""
    return (
        NotificationDelivery.query
        .filter(
            NotificationDelivery.status == "sending",
            NotificationDelivery.claimed_at < now - CLAIM_LEASE,
        )
        .update(
            {"status": "pending", "next_attempt_at": now, "last_error": "released after interrupted send"},
            synchronize_session=False,
        )
    )


def _expire_stale(now):
    return (
        NotificationDelivery.query
        .filter(
            NotificationDelivery.status == "pending",
            NotificationDelivery.created_at < now - MAX_AGE,
        )
        .update(
            {"status": "failed", "last_error": "expired before it could be sent"},
            synchronize_session=False,
        )
    )


def process_due_deliveries(
    limit=DEFAULT_BATCH,
    time_budget_seconds=DEFAULT_TIME_BUDGET_SECONDS,
    *,
    now_fn=datetime.utcnow,
):
    """Send due deliveries. Commits after every row so a crash loses at most one."""
    started = time.monotonic()
    now = now_fn()
    results = {"sent": 0, "retry": 0, "failed": 0, "skipped": 0, "expired": 0}

    results["released"] = _release_abandoned(now)
    results["stale"] = _expire_stale(now)
    db.session.commit()

    due_ids = [
        row.id for row in (
            NotificationDelivery.query
            .with_entities(NotificationDelivery.id)
            .filter(
                NotificationDelivery.status == "pending",
                NotificationDelivery.next_attempt_at <= now,
            )
            .order_by(NotificationDelivery.id)
            .limit(limit)
            .all()
        )
    ]

    for delivery_id in due_ids:
        if time.monotonic() - started > time_budget_seconds:
            break
        if not _claim(delivery_id, now_fn()):
            continue

        delivery = db.session.get(NotificationDelivery, delivery_id)
        note = db.session.get(Notification, delivery.notification_id)
        send_started = time.monotonic()
        attempt_at = now_fn()

        try:
            if delivery.channel == "email":
                outcome = _send_email(delivery, note, attempt_at)
            elif delivery.channel == "push":
                outcome = _send_push(delivery, note, attempt_at)
            else:
                delivery.status = "skipped"
                delivery.last_error = f"unknown channel {delivery.channel}"[:300]
                outcome = "skipped"
        except Exception as e:
            db.session.rollback()
            delivery = db.session.get(NotificationDelivery, delivery_id)
            outcome = _retry_or_fail(delivery, f"error={type(e).__name__}", attempt_at)
            current_app.logger.exception(f"[NOTIFY] unexpected delivery error delivery_id={delivery_id}")

        delivery.claimed_at = None
        db.session.commit()
        results[outcome] += 1

        current_app.logger.info(
            f"[NOTIFY] delivery delivery_id={delivery.id} notification_id={delivery.notification_id} "
            f"type={note.type if note else '?'} related_id={note.related_id if note else '?'} "
            f"channel={delivery.channel} outcome={outcome} attempt={delivery.attempts} "
            f"duration_ms={int((time.monotonic() - send_started) * 1000)}"
        )

    results["duration_ms"] = int((time.monotonic() - started) * 1000)
    if due_ids or results["released"] or results["stale"]:
        current_app.logger.info(
            "[NOTIFY] dispatch " + " ".join(f"{k}={v}" for k, v in results.items())
        )
    return results
