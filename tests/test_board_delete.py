from Football_Project.extensions import db
from Football_Project.models import (
    BoardPost,
    BoardThread,
    GroupMember,
    Notification,
    NotificationDelivery,
)

from test_notification_delivery import NotificationQueueTestCase


class BoardDeleteTests(NotificationQueueTestCase):
    def setUp(self):
        super().setUp()
        self.opening = BoardPost(thread_id=self.thread.id, author_user_id=self.author.id, body="Welcome")
        db.session.add(self.opening)
        db.session.commit()

    def reply_as(self, user, body):
        self.login(user)
        self.reply(body)
        return BoardPost.query.filter_by(body=body).one()

    def delete(self, post):
        return self.client.post(f"/board/post/{post.id}/delete")

    def test_author_deletes_own_reply(self):
        mine = self.reply_as(self.alice, "oops, wrong thread")
        other = self.reply_as(self.bob, "Nice update")

        self.login(self.alice)
        response = self.delete(mine)

        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/board/thread/{self.thread.id}", response.headers["Location"])
        self.assertFalse(db.session.get(BoardPost, mine.id).is_active)
        self.assertTrue(db.session.get(BoardPost, other.id).is_active)
        self.assertTrue(db.session.get(BoardThread, self.thread.id).is_active)

        page = self.client.get(f"/board/thread/{self.thread.id}").get_data(as_text=True)
        self.assertNotIn("oops, wrong thread", page)
        self.assertIn("Nice update", page)

    def test_deleted_reply_withdraws_only_its_notifications(self):
        mine = self.reply_as(self.alice, "oops")
        self.reply_as(self.bob, "Nice update")
        self.login(self.alice)
        self.delete(mine)

        oops = Notification.query.filter_by(body="oops").all()
        self.assertTrue(oops and all(n.read_at for n in oops))
        oops_ids = [n.id for n in oops]
        statuses = {d.status for d in NotificationDelivery.query.filter(NotificationDelivery.notification_id.in_(oops_ids))}
        self.assertEqual(statuses, {"skipped"})

        nice = Notification.query.filter_by(body="Nice update").all()
        self.assertTrue(nice and all(n.read_at is None for n in nice))
        nice_ids = [n.id for n in nice]
        statuses = {d.status for d in NotificationDelivery.query.filter(NotificationDelivery.notification_id.in_(nice_ids))}
        self.assertEqual(statuses, {"pending"})

    def test_members_cannot_delete_other_peoples_posts(self):
        theirs = self.reply_as(self.bob, "keep me")
        self.login(self.alice)
        self.delete(theirs)
        self.delete(self.opening)
        self.assertTrue(db.session.get(BoardPost, theirs.id).is_active)
        self.assertTrue(db.session.get(BoardPost, self.opening.id).is_active)
        self.assertTrue(db.session.get(BoardThread, self.thread.id).is_active)

    def test_group_admin_and_site_admin_can_delete_any_post(self):
        a = self.reply_as(self.bob, "first spam")
        b = self.reply_as(self.bob, "second spam")

        GroupMember.query.filter_by(user_id=self.alice.id, group_id=self.group.id).one().role = "group_admin"
        db.session.commit()
        self.login(self.alice)
        self.delete(a)
        self.assertFalse(db.session.get(BoardPost, a.id).is_active)

        self.outsider.is_admin = True
        db.session.commit()
        self.login(self.outsider)
        self.delete(b)
        self.assertFalse(db.session.get(BoardPost, b.id).is_active)

    def test_deleting_the_opening_post_deletes_the_thread(self):
        self.reply_as(self.bob, "a reply")
        self.login(self.author)
        response = self.delete(self.opening)

        self.assertTrue(response.headers["Location"].endswith("/board"))
        self.assertFalse(db.session.get(BoardThread, self.thread.id).is_active)
        self.assertTrue(all(n.read_at for n in Notification.query.filter_by(related_id=self.thread.id)))
        self.assertEqual(NotificationDelivery.query.filter_by(status="pending").count(), 0)

        # Old links and replies to it no longer work.
        response = self.client.get(f"/board/thread/{self.thread.id}")
        self.assertTrue(response.headers["Location"].endswith("/board"))
        self.reply("late reply")
        self.assertEqual(BoardPost.query.filter_by(body="late reply").count(), 0)

    def test_cannot_delete_from_another_group(self):
        mine = self.reply_as(self.alice, "mine")
        self.login(self.alice)
        with self.client.session_transaction() as session:
            session["active_group_id"] = self.other_group.id
        self.delete(mine)
        self.assertTrue(db.session.get(BoardPost, mine.id).is_active)

    def test_delete_button_only_shown_where_allowed(self):
        self.reply_as(self.bob, "bob says hi")
        self.login(self.alice)
        page = self.client.get(f"/board/thread/{self.thread.id}").get_data(as_text=True)
        self.assertNotIn("/delete", page)

        self.reply("alice says hi")
        page = self.client.get(f"/board/thread/{self.thread.id}").get_data(as_text=True)
        self.assertEqual(page.count("/delete"), 1)
        self.assertIn("Delete this post?", page)

        self.login(self.author)
        page = self.client.get(f"/board/thread/{self.thread.id}").get_data(as_text=True)
        self.assertEqual(page.count("/delete"), 1)
        self.assertIn("Delete this whole thread, including all replies?", page)
