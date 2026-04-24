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

    recipients = [{"email": "stevenbarnes50@gmail.com"}]

    payload = {
        "sender": {"name": "Sunday Pickems", "email": "noreply@sundaypickems.com"},
        "to": recipients,
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
