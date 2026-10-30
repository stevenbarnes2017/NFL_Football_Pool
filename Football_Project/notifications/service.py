import json

from flask import current_app
from pywebpush import webpush, WebPushException
from datetime import datetime

# Seconds to wait for the browser's push service before giving up.
PUSH_TIMEOUT_SECONDS = 10

# The push service says this subscription will never work again.
GONE_STATUS_CODES = (404, 410)

# Push results returned by push_with_status()
PUSH_SENT = "sent"
PUSH_GONE = "gone"            # subscription deactivated; don't retry
PUSH_REJECTED = "rejected"    # permanent 4xx (bad payload/keys); don't retry
PUSH_RETRY = "retry"          # timeout, network error, 429 or 5xx


def push_with_status(
    subscription,
    title,
    message,
    *,
    ttl=None,
    urgency=None,
):
    """Send one web push and return one of the PUSH_* results.

    Expired subscriptions (404/410) are marked inactive here; the caller
    commits. Never raises for delivery failures.
    """
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
            timeout=PUSH_TIMEOUT_SECONDS,
            **delivery_options,
        )

        subscription.last_used = datetime.utcnow()
        return PUSH_SENT

    except WebPushException as e:
        status = getattr(e.response, "status_code", None)

        if status in GONE_STATUS_CODES:
            subscription.active = False
            current_app.logger.info(
                f"[PUSH] subscription expired status={status} "
                f"subscription_id={subscription.id} user_id={subscription.user_id} deactivated=1"
            )
            return PUSH_GONE

        current_app.logger.warning(
            f"[PUSH] failed status={status} subscription_id={subscription.id} "
            f"user_id={subscription.user_id}"
        )
        if status is not None and 400 <= status < 500 and status != 429:
            return PUSH_REJECTED
        return PUSH_RETRY

    except Exception as e:
        # Timeouts, connection errors, bad keys: keep the caller's loop going.
        current_app.logger.warning(
            f"[PUSH] failed error={type(e).__name__} subscription_id={subscription.id} "
            f"user_id={subscription.user_id}"
        )
        return PUSH_RETRY


def send_push_notification(
    subscription,
    title,
    message,
    *,
    ttl=None,
    urgency=None,
):
    """Send one web push; True if the push service accepted it."""
    return push_with_status(
        subscription, title, message, ttl=ttl, urgency=urgency,
    ) == PUSH_SENT
