from flask import request, jsonify
from flask_login import current_user, login_required
from .. import db
from ..models import NotificationSubscription
from . import notifications_bp
from datetime import datetime
from .. import csrf

@notifications_bp.route("/subscribe", methods=["POST"])
@login_required
@csrf.exempt
def subscribe():
    data = request.get_json()

    endpoint = data.get("endpoint")
    keys = data.get("keys", {})

    if not endpoint or not keys.get("p256dh") or not keys.get("auth"):
        return jsonify({
            "success": False,
            "error": "Invalid subscription data"
        }), 400

    existing = NotificationSubscription.query.filter_by(
        user_id=current_user.id,
        endpoint=endpoint
    ).first()

    if existing:
        existing.active = True
        existing.p256dh = keys["p256dh"]
        existing.auth = keys["auth"]
        existing.last_used = datetime.utcnow()
    else:
        subscription = NotificationSubscription(
            user_id=current_user.id,
            endpoint=endpoint,
            p256dh=keys["p256dh"],
            auth=keys["auth"],
            browser=request.user_agent.string[:50]
        )

        db.session.add(subscription)

    db.session.commit()

    return jsonify({
        "success": True
    })


@notifications_bp.route("/test")
@login_required
def test():
    return jsonify({
        "message": "Notifications blueprint works",
        "user": current_user.username
    })

from .service import send_push_notification
@notifications_bp.route("/test-push")
@login_required
def test_push():

    subscriptions = NotificationSubscription.query.filter_by(
        user_id=current_user.id,
        active=True
    ).all()

    results = []

    for subscription in subscriptions:
        results.append(
            send_push_notification(
                subscription,
                "Sunday Pickems",
                "Your push notifications are working!"
            )
        )

    return jsonify({
        "sent": results
    })