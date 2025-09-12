# Football_Project/services/sms_helpers.py
import os, requests

BREVO_SMS_URL = "https://api.brevo.com/v3/transactionalSMS/send"

def send_sms(to_e164: str, text: str, tag: str | None = None) -> dict:
    api_key = os.environ["BREVO_API_KEY"]
    sender = os.environ["BREVO_SMS_SENDER"]

    payload = {"sender": sender, "recipient": to_e164, "content": text}
    if tag:
        payload["tag"] = tag

    headers = {
        "api-key": api_key,
        "accept": "application/json",
        "content-type": "application/json",
    }

    resp = requests.post(BREVO_SMS_URL, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()
