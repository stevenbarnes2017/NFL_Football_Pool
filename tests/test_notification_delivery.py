import os
import unittest
from datetime import datetime, timedelta
from unittest import mock

import requests
from flask import Flask
from flask_login import LoginManager
from pywebpush import WebPushException

from Football_Project.extensions import db
from Football_Project.models import (
    Announcement,
    BoardPost,
    BoardThread,
    GroupMember,
    Notification,
    NotificationDelivery,
    NotificationSubscription,
    PoolGroup,
    User,
)
from Football_Project.services import notification_delivery as delivery_mod
from Football_Project.services.notification_delivery import (
    MAX_ATTEMPTS,
    process_due_deliveries,
)
from Football_Project.services.notification_service import (
    notify_announcement,
    notify_board_post,
)


def _push_error(status):
    response = mock.Mock(status_code=status, text="push subscription has unsubscribed or expired.")
    return WebPushException(f"Push failed: {status}", response=response)


class NotificationQueueTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask("Football_Project", template_folder="templates", static_folder="static")
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="notify-test-only",
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            WTF_CSRF_ENABLED=False,
            VAPID_PRIVATE_KEY="test-only-not-a-key",
            VAPID_CLAIM_EMAIL="mailto:test@example.invalid",
        )
        db.init_app(self.app)
        login_manager = LoginManager()
        login_manager.init_app(self.app)

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        from Football_Project.admin import admin_bp
        from Football_Project.auth import auth_bp
        from Football_Project.challenges import challenges_bp
        from Football_Project.routes import main_bp

        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(challenges_bp)

        self.context = self.app.test_request_context()
        self.context.push()
        db.create_all()

        self.group = PoolGroup(name="Main", slug="main")
        self.other_group = PoolGroup(name="Other", slug="other")
        db.session.add_all([self.group, self.other_group])
        db.session.flush()

        def user(name, **kw):
            u = User(username=name, password="x", email=f"{name}@example.invalid", **kw)
            db.session.add(u)
            db.session.flush()
            return u

        self.author = user("author")
        self.alice = user("alice")
        self.bob = user("bob")
        self.quiet = user("quiet", email_notifications_enabled=False)
        self.outsider = user("outsider")
        for u in (self.author, self.alice, self.bob, self.quiet):
            db.session.add(GroupMember(user_id=u.id, group_id=self.group.id))
        db.session.add(GroupMember(user_id=self.outsider.id, group_id=self.other_group.id))

        self.alice_phone = NotificationSubscription(user_id=self.alice.id, endpoint="https://push.example/a1", p256dh="k", auth="a")
        self.alice_laptop = NotificationSubscription(user_id=self.alice.id, endpoint="https://push.example/a2", p256dh="k", auth="a")
        self.quiet_phone = NotificationSubscription(user_id=self.quiet.id, endpoint="https://push.example/q1", p256dh="k", auth="a")
        self.bob_old = NotificationSubscription(user_id=self.bob.id, endpoint="https://push.example/b0", p256dh="k", auth="a", active=False)
        db.session.add_all([self.alice_phone, self.alice_laptop, self.quiet_phone, self.bob_old])

        self.thread = BoardThread(title="Site update", group_id=self.group.id, created_by_user_id=self.author.id)
        db.session.add(self.thread)
        db.session.commit()

        self.client = self.app.test_client()

        # Nothing in these tests may reach a real provider.
        self.http = mock.patch("Football_Project.services.email_helpers.requests.post").start()
        self.http.return_value = mock.Mock(status_code=201, raise_for_status=mock.Mock())
        self.webpush = mock.patch("Football_Project.notifications.service.webpush").start()
        os.environ["EMAIL_TEST_MODE"] = "0"
        self.addCleanup(mock.patch.stopall)
        self.addCleanup(os.environ.pop, "EMAIL_TEST_MODE", None)

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.context.pop()

    # helpers
    def login(self, user):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(user.id)
            session["_fresh"] = True
            session["active_group_id"] = self.group.id

    def reply(self, body="Nice update!"):
        return self.client.post(f"/board/thread/{self.thread.id}", data={"body": body})

    def deliveries(self, **filters):
        return NotificationDelivery.query.filter_by(**filters).all()

    def emailed_to(self):
        return sorted(c.kwargs["json"]["to"][0]["email"] for c in self.http.call_args_list)


class ReplyQueueTests(NotificationQueueTestCase):
    def test_reply_queues_instead_of_sending(self):
        self.login(self.author)
        response = self.reply()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(BoardPost.query.count(), 1)
        self.http.assert_not_called()
        self.webpush.assert_not_called()

        notes = Notification.query.order_by(Notification.user_id).all()
        self.assertEqual([n.user_id for n in notes], [self.alice.id, self.bob.id, self.quiet.id])
        # email: alice + bob (quiet opted out); push: alice x2 + quiet x1 (bob's is inactive)
        self.assertEqual(len(self.deliveries(channel="email")), 2)
        self.assertEqual(len(self.deliveries(channel="push")), 3)
        self.assertTrue(all(d.status == "pending" for d in self.deliveries()))

    def test_processing_delivers_to_every_recipient_once(self):
        self.login(self.author)
        self.reply()
        results = process_due_deliveries()

        self.assertEqual(results["sent"], 5)
        self.assertEqual(self.emailed_to(), ["alice@example.invalid", "bob@example.invalid"])
        self.assertEqual(self.webpush.call_count, 3)
        self.assertEqual(self.http.call_args.kwargs["timeout"], delivery_mod_timeout())
        for note in Notification.query.all():
            if note.user_id in (self.alice.id, self.bob.id):
                self.assertIsNotNone(note.email_sent_at)

        # A second run sends nothing more.
        self.assertEqual(process_due_deliveries()["sent"], 0)
        self.assertEqual(self.http.call_count, 2)

    def test_outsiders_and_author_are_not_notified(self):
        self.login(self.author)
        self.reply()
        notified = {n.user_id for n in Notification.query.all()}
        self.assertNotIn(self.author.id, notified)
        self.assertNotIn(self.outsider.id, notified)

    def test_repeat_submit_posts_and_notifies_once(self):
        self.login(self.author)
        for _ in range(6):
            self.assertEqual(self.reply("Even better hope next week is as exciting").status_code, 302)
        self.assertEqual(BoardPost.query.count(), 1)
        self.assertEqual(Notification.query.count(), 3)

        # A different message, or the same one later, is a real new post.
        self.reply("Second thought")
        self.assertEqual(BoardPost.query.count(), 2)
        old = BoardPost.query.filter_by(body="Second thought").one()
        old.created_at -= timedelta(minutes=2)
        db.session.commit()
        self.reply("Second thought")
        self.assertEqual(BoardPost.query.count(), 3)

    def test_repeat_new_thread_is_ignored(self):
        self.login(self.author)
        for _ in range(3):
            self.client.post("/board/new", data={"title": "Week 9", "body": "Picks?"})
        self.assertEqual(BoardThread.query.filter_by(title="Week 9").count(), 1)
        thread = BoardThread.query.filter_by(title="Week 9").one()
        self.assertEqual(Notification.query.filter_by(related_id=thread.id).count(), 3)

    def test_repeat_announcement_is_ignored(self):
        self.author.is_admin = True
        db.session.commit()
        self.login(self.author)
        for _ in range(3):
            response = self.client.post("/admin/announcements/new", data={"title": "Playoffs", "body": "Soon"})
            self.assertEqual(response.status_code, 302)
        self.assertEqual(Announcement.query.count(), 1)
        self.assertEqual(Notification.query.filter_by(type="announcement").count(), 4)

    def test_duplicate_recipient_ids_get_one_notification(self):
        post = BoardPost(thread_id=self.thread.id, author_user_id=self.author.id, body="hi")
        db.session.add(post)
        db.session.commit()
        notify_board_post(self.thread, post, recipient_user_ids=[self.alice.id, self.alice.id, None],
                          is_new_thread=False)
        self.assertEqual(Notification.query.count(), 1)
        self.assertEqual(len(self.deliveries(channel="email")), 1)
        self.assertEqual(len(self.deliveries(channel="push")), 2)

    def test_reply_is_saved_even_if_queueing_fails(self):
        self.login(self.author)
        with mock.patch("Football_Project.services.notification_service.enqueue_deliveries",
                        side_effect=RuntimeError("db hiccup")):
            response = self.reply()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BoardPost.query.count(), 1)
        self.assertEqual(NotificationDelivery.query.count(), 0)

    def test_announcement_queues_for_everyone_but_author(self):
        ann = Announcement(title="Playoffs", body="**Soon**", created_by_user_id=self.author.id, is_active=True)
        db.session.add(ann)
        db.session.commit()
        ids = [u.id for u in User.query.filter_by(is_active=True)]
        notify_announcement(ann, ids)

        self.assertEqual({n.user_id for n in Notification.query}, {self.alice.id, self.bob.id, self.quiet.id, self.outsider.id})
        process_due_deliveries()
        self.assertEqual(self.emailed_to(), ["alice@example.invalid", "bob@example.invalid", "outsider@example.invalid"])
        html = self.http.call_args.kwargs["json"]["htmlContent"]
        self.assertIn("<strong>Soon</strong>", html)


def delivery_mod_timeout():
    from Football_Project.services.email_helpers import BREVO_TIMEOUT
    return BREVO_TIMEOUT


class PreferenceTests(NotificationQueueTestCase):
    def test_email_turned_off_after_queueing_is_skipped(self):
        self.login(self.author)
        self.reply()
        self.bob.email_notifications_enabled = False
        db.session.commit()
        process_due_deliveries()
        self.assertEqual(self.emailed_to(), ["alice@example.invalid"])
        bob_email = NotificationDelivery.query.join(Notification).filter(
            Notification.user_id == self.bob.id, NotificationDelivery.channel == "email").one()
        self.assertEqual(bob_email.status, "skipped")

    def test_unsubscribed_device_after_queueing_is_skipped(self):
        self.login(self.author)
        self.reply()
        self.alice_laptop.active = False
        db.session.commit()
        process_due_deliveries()
        self.assertEqual(self.webpush.call_count, 2)


class ExpiredPushTests(NotificationQueueTestCase):
    def _run_with_push_status(self, status):
        def fake_webpush(subscription_info, **kw):
            if subscription_info["endpoint"] == self.alice_phone.endpoint:
                raise _push_error(status)
        self.webpush.side_effect = fake_webpush
        self.login(self.author)
        self.reply()
        with self.assertLogs(self.app.logger, "INFO") as logs:
            results = process_due_deliveries()
        return results, "\n".join(logs.output)

    def test_410_deactivates_subscription_and_is_not_retried(self):
        results, logs = self._run_with_push_status(410)
        self.assertEqual(results["expired"], 1)
        self.assertFalse(db.session.get(NotificationSubscription, self.alice_phone.id).active)
        self.assertTrue(db.session.get(NotificationSubscription, self.alice_laptop.id).active)
        self.assertTrue(db.session.get(NotificationSubscription, self.quiet_phone.id).active)
        self.assertNotIn("push.example", logs)  # endpoints stay out of logs

        # Next event: the expired device isn't even queued.
        calls = self.webpush.call_count
        self.reply("another one")
        process_due_deliveries()
        endpoints = [c.kwargs["subscription_info"]["endpoint"] for c in self.webpush.call_args_list[calls:]]
        self.assertNotIn(self.alice_phone.endpoint, endpoints)
        self.assertEqual(len(endpoints), 2)

    def test_404_deactivates_subscription(self):
        results, _ = self._run_with_push_status(404)
        self.assertEqual(results["expired"], 1)
        self.assertFalse(db.session.get(NotificationSubscription, self.alice_phone.id).active)

    def test_push_server_error_is_retried_and_subscription_kept(self):
        results, _ = self._run_with_push_status(503)
        self.assertEqual(results["retry"], 1)
        self.assertTrue(db.session.get(NotificationSubscription, self.alice_phone.id).active)
        pending = NotificationDelivery.query.filter_by(subscription_id=self.alice_phone.id).one()
        self.assertEqual(pending.status, "pending")
        self.assertGreater(pending.next_attempt_at, datetime.utcnow())

    def test_reminder_style_push_deactivates_too(self):
        from Football_Project.notifications.service import send_push_notification
        self.webpush.side_effect = _push_error(410)
        self.assertFalse(send_push_notification(self.alice_phone, "t", "b"))
        self.assertFalse(self.alice_phone.active)
        self.assertEqual(self.webpush.call_args.kwargs["timeout"], 10)


class RetryTests(NotificationQueueTestCase):
    def test_email_timeout_retries_with_backoff_then_fails(self):
        self.http.side_effect = requests.Timeout("read timed out")
        self.login(self.author)
        self.reply()

        clock = [datetime.utcnow()]
        now = lambda: clock[0]
        for attempt in range(1, MAX_ATTEMPTS + 1):
            process_due_deliveries(now_fn=now)
            emails = self.deliveries(channel="email")
            self.assertTrue(all(d.attempts == attempt for d in emails), [d.attempts for d in emails])
            if attempt < MAX_ATTEMPTS:
                self.assertTrue(all(d.status == "pending" for d in emails))
                # Not due again until the backoff passes.
                self.assertEqual(process_due_deliveries(now_fn=now)["sent"] + process_due_deliveries(now_fn=now)["retry"], 0)
                clock[0] = max(d.next_attempt_at for d in emails) + timedelta(seconds=1)
        self.assertTrue(all(d.status == "failed" for d in self.deliveries(channel="email")))
        self.assertEqual(self.http.call_count, 2 * MAX_ATTEMPTS)
        # Pushes were unaffected by the email outage.
        self.assertTrue(all(d.status == "sent" for d in self.deliveries(channel="push")))

    def test_email_recovers_on_retry(self):
        self.http.side_effect = [requests.ConnectionError("down"), requests.ConnectionError("down"),
                                 mock.Mock(status_code=201, raise_for_status=mock.Mock()),
                                 mock.Mock(status_code=201, raise_for_status=mock.Mock())]
        self.login(self.author)
        self.reply()
        later = datetime.utcnow() + timedelta(minutes=2)
        process_due_deliveries()
        process_due_deliveries(now_fn=lambda: later)
        self.assertTrue(all(d.status == "sent" for d in self.deliveries(channel="email")))

    def test_rejected_email_is_not_retried(self):
        error = requests.HTTPError("400 bad request", response=mock.Mock(status_code=400))
        self.http.return_value = mock.Mock(status_code=400, raise_for_status=mock.Mock(side_effect=error))
        self.login(self.author)
        self.reply()
        results = process_due_deliveries()
        self.assertEqual(results["failed"], 2)
        self.assertTrue(all(d.attempts == 1 for d in self.deliveries(channel="email")))

    def test_unexpected_error_does_not_stop_the_batch(self):
        self.webpush.side_effect = ValueError("bad vapid key")
        self.login(self.author)
        self.reply()
        results = process_due_deliveries()
        self.assertEqual(results["sent"], 2)  # both emails still went out
        self.assertEqual(results["retry"], 3)

    def test_time_budget_stops_early_and_leaves_rest_pending(self):
        self.login(self.author)
        self.reply()
        results = process_due_deliveries(time_budget_seconds=-1)
        self.assertEqual(results["sent"], 0)
        self.assertEqual(len(self.deliveries(status="pending")), 5)

    def test_stale_deliveries_expire_instead_of_sending(self):
        self.login(self.author)
        self.reply()
        tomorrow = datetime.utcnow() + timedelta(hours=25)
        results = process_due_deliveries(now_fn=lambda: tomorrow)
        self.assertEqual(results["stale"], 5)
        self.http.assert_not_called()


class QueueRecoveryTests(NotificationQueueTestCase):
    def test_queue_survives_until_processed(self):
        self.login(self.author)
        self.reply()
        # New session (like a restarted process) still sees the queued work.
        db.session.remove()
        self.assertEqual(NotificationDelivery.query.filter_by(status="pending").count(), 5)
        self.assertEqual(process_due_deliveries()["sent"], 5)

    def test_claim_is_exclusive(self):
        self.login(self.author)
        self.reply()
        first = self.deliveries()[0]
        now = datetime.utcnow()
        self.assertTrue(delivery_mod._claim(first.id, now))
        self.assertFalse(delivery_mod._claim(first.id, now))  # a second worker gets nothing
        results = process_due_deliveries()
        self.assertEqual(results["sent"], 4)  # the claimed row is left to its owner

    def test_interrupted_send_is_retried_after_lease(self):
        self.login(self.author)
        self.reply()
        stuck = self.deliveries(channel="email")[0]
        delivery_mod._claim(stuck.id, datetime.utcnow())  # process "dies" here

        process_due_deliveries()
        self.assertEqual(db.session.get(NotificationDelivery, stuck.id).status, "sending")

        later = datetime.utcnow() + delivery_mod.CLAIM_LEASE + timedelta(minutes=1)
        results = process_due_deliveries(now_fn=lambda: later)
        self.assertEqual(results["released"], 1)
        row = db.session.get(NotificationDelivery, stuck.id)
        self.assertEqual(row.status, "sent")
        self.assertEqual(row.attempts, 2)


class HealthEndpointTests(unittest.TestCase):
    def test_health_needs_no_database_or_login(self):
        with mock.patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:", "RUN_SCHEDULER": "0"}):
            from Football_Project import create_app
            app = create_app()
        client = app.test_client()
        with mock.patch("Football_Project.extensions.db.session.execute", side_effect=AssertionError("db used")):
            response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
