import os
import base64
import logging
import requests

from flask import current_app

from Football_Project.models import User, GroupMember, Pick, Game

logger = logging.getLogger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def _split_emails(value: str | None) -> list[str]:
    if not value:
        return []
    return [email.strip() for email in value.split(",") if email.strip()]


def _test_mode_recipients(recipients: list[str]) -> list[str]:
    test_mode = os.getenv("EMAIL_TEST_MODE", "1") == "1"

    if not test_mode:
        return recipients

    test_email = os.getenv("TEST_EMAIL", "stevenbarnes50@gmail.com")
    return [test_email]


def send_email(
    recipients: list[str],
    subject: str,
    html: str,
    attachment_bytes: bytes | None = None,
    filename: str | None = None,
):
    recipients = [email for email in recipients if email]

    if not recipients:
        logger.warning(f"[EMAIL] No recipients for subject='{subject}'")
        return {"sent": 0, "skipped": True}

    final_recipients = _test_mode_recipients(recipients)

    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": os.getenv("FROM_NAME", "Sunday Pickems"),
            "email": os.getenv("FROM_EMAIL", "noreply@sundaypickems.com"),
        },
        "to": [{"email": email} for email in final_recipients],
        "subject": subject,
        "htmlContent": html,
    }

    if attachment_bytes:
        payload["attachment"] = [{
            "content": base64.b64encode(attachment_bytes).decode("utf-8"),
            "name": filename or "attachment.csv",
        }]

    try:
        logger.info(
            f"[EMAIL] Sending subject='{subject}' "
            f"recipients={len(final_recipients)} "
            f"test_mode={os.getenv('EMAIL_TEST_MODE', '1')}"
        )

        r = requests.post(BREVO_URL, json=payload, headers=headers)
        r.raise_for_status()

        logger.info(f"[EMAIL] SUCCESS subject='{subject}' status_code={r.status_code}")

        return {"sent": len(final_recipients), "status_code": r.status_code}

    except Exception as e:
        logger.error(f"[EMAIL] FAILED subject='{subject}' error={str(e)}")
        raise


def send_admin_email(
    subject: str,
    html: str,
    attachment_bytes: bytes | None = None,
    filename: str | None = None,
):
    admin_emails = _split_emails(
        os.getenv("ADMIN_EMAILS", "stevenbarnes50@gmail.com")
    )

    return send_email(
        recipients=admin_emails,
        subject=subject,
        html=html,
        attachment_bytes=attachment_bytes,
        filename=filename,
    )


def send_user_email(
    to_email: str,
    subject: str,
    html: str,
    attachment_bytes: bytes | None = None,
    filename: str | None = None,
):
    return send_email(
        recipients=[to_email],
        subject=subject,
        html=html,
        attachment_bytes=attachment_bytes,
        filename=filename,
    )


def send_all_users_email(
    subject: str,
    html: str,
    attachment_bytes: bytes | None = None,
    filename: str | None = None,
):
    users = User.query.filter(User.email.isnot(None)).all()
    recipients = [u.email for u in users if u.email]

    return send_email(
        recipients=recipients,
        subject=subject,
        html=html,
        attachment_bytes=attachment_bytes,
        filename=filename,
    )


def send_group_email(
    group_id: int,
    subject: str,
    html: str,
    attachment_bytes: bytes | None = None,
    filename: str | None = None,
):
    members = GroupMember.query.filter_by(
        group_id=group_id,
        is_active=True,
    ).all()

    user_ids = [m.user_id for m in members]

    users = (
        User.query
        .filter(User.id.in_(user_ids))
        .filter(User.email.isnot(None))
        .all()
    )

    recipients = [u.email for u in users if u.email]

    return send_email(
        recipients=recipients,
        subject=subject,
        html=html,
        attachment_bytes=attachment_bytes,
        filename=filename,
    )


def send_group_missing_picks_email(
    group_id: int,
    season_year: int,
    season_type: str,
    week: int,
    subject: str,
    html: str,
):
    members = GroupMember.query.filter_by(
        group_id=group_id,
        is_active=True,
    ).all()

    games = Game.query.filter_by(
        season_year=season_year,
        season_type=season_type,
        week=week,
    ).all()

    game_ids = [g.id for g in games]

    recipients = []

    for member in members:
        user = User.query.get(member.user_id)

        if not user or not user.email:
            continue

        pick_count = (
            Pick.query
            .filter_by(
                user_id=user.id,
                group_id=group_id,
                week=week,
            )
            .filter(Pick.game_id.in_(game_ids))
            .count()
        )

        if pick_count < len(game_ids):
            recipients.append(user.email)

    return send_email(
        recipients=recipients,
        subject=subject,
        html=html,
    )