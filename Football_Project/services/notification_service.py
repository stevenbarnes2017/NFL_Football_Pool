"""Central service for in-app notifications (+ push/email fan-out).

Covers three event types today:
  - "announcement"      -> new admin announcement posted
  - "board_post"        -> new message board thread/reply
  - "challenge_invite"  -> user added as a challenge participant

Each event creates one Notification row per recipient (powers the nav
badge counts + login banner) and queues push (existing web-push
subscriptions) and email (services/email_helpers.send_user_email)
deliveries, which the scheduler sends; see services/notification_delivery.
"""

from datetime import datetime, timedelta

from flask import current_app, url_for
from markupsafe import escape
from sqlalchemy import func

from Football_Project.extensions import db
from Football_Project.models import Notification
from Football_Project.services.notification_delivery import enqueue_deliveries
from Football_Project.services.text_format import plain_text, render_post

NOTIFICATION_TYPES = ("announcement", "board_post", "challenge_invite")


def _create_notifications(
    user_ids,
    *,
    type_,
    title,
    body,
    url,
    group_id=None,
    related_id=None,
    exclude_user_id=None,
):
    """Insert one Notification per unique recipient. Does not commit."""
    created = []
    seen = set()

    for uid in user_ids:
        if uid is None or uid == exclude_user_id or uid in seen:
            continue
        seen.add(uid)

        created.append(
            Notification(
                user_id=uid,
                type=type_,
                title=title[:200],
                body=(body or "")[:500],
                url=url,
                group_id=group_id,
                related_id=related_id,
            )
        )

    if created:
        db.session.add_all(created)

    return created


def _queue_push_and_email(notifications, *, email_subject, email_html_fn):
    """Save the notifications and queue their push + email in one commit.

    Sending happens later in the scheduler process
    (services/notification_delivery.py), so this returns quickly no matter
    how many recipients there are or how slow Brevo/push services are.
    """
    try:
        db.session.flush()
        counts = enqueue_deliveries(
            notifications,
            email_subject=email_subject,
            email_html_fn=email_html_fn,
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    if notifications:
        first = notifications[0]
        current_app.logger.info(
            f"[NOTIFY] queued type={first.type} related_id={first.related_id} "
            f"recipients={len(notifications)} email={counts['email']} push={counts['push']}"
        )


def _absolute_url(endpoint, **values):
    try:
        return url_for(endpoint, _external=True, **values)
    except Exception:
        return url_for(endpoint, **values)


def notify_announcement(announcement, recipient_user_ids):
    """Notify recipients about a newly posted Announcement."""
    path_url = url_for("main.announcements")

    notifications = _create_notifications(
        recipient_user_ids,
        type_="announcement",
        title=f"New announcement: {announcement.title}",
        body=plain_text(announcement.body),
        url=path_url,
        related_id=announcement.id,
        exclude_user_id=announcement.created_by_user_id,
    )

    def email_html(user, note):
        link = _absolute_url("main.announcements")
        return (
            f"<p><strong>{escape(announcement.title)}</strong></p>"
            f"{render_post(announcement.body, images=False)}"
            f"<p><a href='{link}'>View announcement</a></p>"
        )

    _queue_push_and_email(
        notifications,
        email_subject=f"New announcement: {announcement.title}",
        email_html_fn=email_html,
    )
    return notifications


def notify_board_post(thread, post, *, recipient_user_ids, is_new_thread):
    """Notify recipients about a new board thread or a new reply."""
    path_url = url_for("main.view_thread", thread_id=thread.id)

    if is_new_thread:
        title = f"New board post: {thread.title}"
    else:
        title = f"New reply in: {thread.title}"

    notifications = _create_notifications(
        recipient_user_ids,
        type_="board_post",
        title=title,
        body=plain_text(post.body),
        url=path_url,
        group_id=thread.group_id,
        related_id=thread.id,
        exclude_user_id=post.author_user_id,
    )

    def email_html(user, note):
        link = _absolute_url("main.view_thread", thread_id=thread.id)
        return (
            f"<p><strong>{escape(title)}</strong></p>"
            f"{render_post(post.body, images=False)}"
            f"<p><a href='{link}'>View on the message board</a></p>"
        )

    _queue_push_and_email(
        notifications,
        email_subject=title,
        email_html_fn=email_html,
    )
    return notifications


def notify_challenge_invite(challenge, recipient_user_ids, *, exclude_user_id=None):
    """Notify newly added participants that they were added to a challenge."""
    path_url = url_for("challenges.challenge_detail", challenge_id=challenge.id)

    notifications = _create_notifications(
        recipient_user_ids,
        type_="challenge_invite",
        title=f"You're in a new challenge: {challenge.name}",
        body=challenge.description or f"You've been added to \"{challenge.name}\".",
        url=path_url,
        group_id=challenge.group_id,
        related_id=challenge.id,
        exclude_user_id=exclude_user_id,
    )

    def email_html(user, note):
        link = _absolute_url("challenges.challenge_detail", challenge_id=challenge.id)
        return (
            f"<p><strong>You've been added to a new challenge: {challenge.name}</strong></p>"
            f"<p>{challenge.description or ''}</p>"
            f"<p><a href='{link}'>View the challenge</a></p>"
        )

    _queue_push_and_email(
        notifications,
        email_subject=f"New challenge: {challenge.name}",
        email_html_fn=email_html,
    )
    return notifications


def withdraw_board_notifications(thread_id, *, post=None):
    """Clear notifications about deleted board content. Does not commit.

    Unread ones are marked read (so badges don't point at a deleted post)
    and emails/pushes not sent yet are cancelled. Without a time window,
    covers the whole thread; with a post, only that reply's notifications
    (same text, created right after the post was saved).
    """
    from Football_Project.models import NotificationDelivery

    query = Notification.query.filter(
        Notification.type == "board_post",
        Notification.related_id == thread_id,
    )
    if post is not None:
        query = query.filter(
            Notification.created_at >= post.created_at,
            Notification.created_at <= post.created_at + timedelta(seconds=30),
            Notification.body == (plain_text(post.body) or "")[:500],
        )
    note_ids = [n.id for n in query.with_entities(Notification.id)]
    if not note_ids:
        return 0

    Notification.query.filter(
        Notification.id.in_(note_ids), Notification.read_at.is_(None)
    ).update({"read_at": datetime.utcnow()}, synchronize_session=False)
    return (
        NotificationDelivery.query
        .filter(
            NotificationDelivery.notification_id.in_(note_ids),
            NotificationDelivery.status == "pending",
        )
        .update({"status": "skipped", "last_error": "post deleted"}, synchronize_session=False)
    )


def unread_counts(user_id):
    """Return unread notification counts by type, plus a 'total' key."""
    counts = {t: 0 for t in NOTIFICATION_TYPES}

    rows = (
        db.session.query(Notification.type, func.count(Notification.id))
        .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
        .group_by(Notification.type)
        .all()
    )

    for note_type, count in rows:
        if note_type in counts:
            counts[note_type] = count

    counts["total"] = sum(counts.values())
    return counts


def mark_read(user_id, type_, related_id=None):
    """Mark a user's unread notifications of a given type as read.

    When related_id is given, only notifications tied to that specific
    object (e.g. one thread) are marked -- notifications of the same
    type with no related_id (shouldn't normally happen) are left alone.
    """
    query = Notification.query.filter_by(
        user_id=user_id,
        type=type_,
        read_at=None,
    )
    if related_id is not None:
        query = query.filter(Notification.related_id == related_id)

    updated = query.update({"read_at": datetime.utcnow()}, synchronize_session=False)
    db.session.commit()
    return updated
