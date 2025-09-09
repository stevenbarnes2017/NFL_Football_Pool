# services/email_helpers.py
import os, base64, requests
from Football_Project.models import User


def send_admin_email(subject: str, html: str, attachment_bytes: bytes | None = None, filename: str = "odds.csv"):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    # 👇 get all users (not just admins)
    users = User.query.all()
    to_list = [{"email": u.email} for u in users if u.email]

    payload = {
        "sender": {"name": "NFL Football Pool", "email": "lines31@hotmail.com"},
        "to": to_list,
        "subject": subject,
        "htmlContent": html
    }

    if attachment_bytes:
        payload["attachment"] = [{
            "content": base64.b64encode(attachment_bytes).decode("utf-8"),
            "name": filename
        }]

    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
