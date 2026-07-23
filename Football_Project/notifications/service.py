import json

from flask import current_app
from pywebpush import webpush, WebPushException
from datetime import datetime


def send_push_notification(subscription, title, message):

    payload = {
        "title": title,
        "body": message,
        "icon": "/static/images/logo.png"
    }

    subscription_info = {
        "endpoint": subscription.endpoint,
        "keys": {
            "p256dh": subscription.p256dh,
            "auth": subscription.auth,
        },
    }

    vapid_claims = {
        "sub": current_app.config["VAPID_CLAIM_EMAIL"]
    }

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=current_app.config["VAPID_PRIVATE_KEY"],
            vapid_claims=vapid_claims,
        )

        subscription.last_used = datetime.utcnow()

        return True

    except WebPushException as e:

        current_app.logger.error(
            f"Push notification failed: {e}"
        )

        return False