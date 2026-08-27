import json

from flask import current_app
from pywebpush import webpush, WebPushException
from datetime import datetime


def send_push_notification(
    subscription,
    title,
    message,
    *,
    ttl=None,
    urgency=None,
):
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

    delivery_options = {}

    if ttl is not None:
        delivery_options["ttl"] = ttl

    if urgency is not None:
        delivery_options["headers"] = {
            "Urgency": urgency
        }

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=current_app.config["VAPID_PRIVATE_KEY"],
            vapid_claims=vapid_claims,
            **delivery_options,
        )

        subscription.last_used = datetime.utcnow()
        return True

    except WebPushException as e:
        current_app.logger.error(
            f"Web Push failed for subscription {subscription.id}: {e}"
        )
        return False