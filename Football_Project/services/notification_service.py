"""Central service for in-app notifications (+ push/email fan-out).

Covers three event types today:
  - "announcement"      -> new admin announcement posted
  - "board_post"        -> new message board thread/reply
  - "challenge_invite"  -> user added as a challenge participant

Each event creates one Notification row per recipient (powers the nav
badge counts + login banner), then best-effort fans out to push
(reusing the existing web-push subscriptions) and email (reusing
services/email_helpers.send_user_email).
"""

from datetime import datetime

from flask import current_app, url_for
from markupsafe import escape
from sqlalchemy import func

from Football_Project.extensions import db
from Football_Project.models import Notification, User, NotificationSubscription
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


def _dispatch_push_and_email(notifications, *, email_subject, email_html_fn):
    """Best-effort push + email fan-out for freshly created notifications.

    Never raises: a failed push/email should not break the request that
    triggered the notification (announcement post, board reply, etc).
    """
    if not notifications:
        return

    app = current_app._get_current_object()

    from Football_Project.notifications.service import send_push_notification

    for note in notifications:
        user = db.session.get(User, note.user_id)
        if not user:
            continue

        # --- push: send to every active subscription, same policy as
        # the existing weekly-reminder push job (opt-in == having an
        # active subscription; no extra toggle to check). ---
        try:
            subs = NotificationSubscription.query.filter_by(
                user_id=user.id, active=True
            ).all()
            pushed_any = False
            for sub in subs:
                if send_push_notification(sub, note.title, note.body or ""):
                    pushed_any = True
            if pushed_any:
                note.push_sent_at = datetime.utcnow()
        except Exception as e:
            app.logger.warning(f"[NOTIFY] push failed user={user.id}: {e}")

        # --- email: respect the existing email opt-out toggle. ---
        if user.email and user.email_notifications_enabled:
            try:
                from Football_Project.services.email_helpers import send_user_email

                send_user_email(
                    to_email=user.email,
                    subject=email_subject,
                    html=email_html_fn(user, note),
                )
                note.email_sent_at = datetime.utcnow()
            except Exception as e:
                app.logger.warning(f"[NOTIFY] email failed user={user.id}: {e}")

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("[NOTIFY] failed committing push/email dispatch state")


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
    db.session.commit()

    def email_html(user, note):
        link = _absolute_url("main.announcements")
        return (
            f"<p><strong>{escape(announcement.title)}</strong></p>"
            f"{render_post(announcement.body, images=False)}"
            f"<p><a href='{link}'>View announcement</a></p>"
        )

    _dispatch_push_and_email(
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
    db.session.commit()

    def email_html(user, note):
        link = _absolute_url("main.view_thread", thread_id=thread.id)
        return (
            f"<p><strong>{escape(title)}</strong></p>"
            f"{render_post(post.body, images=False)}"
            f"<p><a href='{link}'>View on the message board</a></p>"
        )

    _dispatch_push_and_email(
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
    db.session.commit()

    def email_html(user, note):
        link = _absolute_url("challenges.challenge_detail", challenge_id=challenge.id)
        return (
            f"<p><strong>You've been added to a new challenge: {challenge.name}</strong></p>"
            f"<p>{challenge.description or ''}</p>"
            f"<p><a href='{link}'>View the challenge</a></p>"
        )

    _dispatch_push_and_email(
        notifications,
        email_subject=f"New challenge: {challenge.name}",
        email_html_fn=email_html,
    )
    return notifications


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
