import unittest
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask

from Football_Project.auth.forms import RegisterForm
from Football_Project.extensions import db
from Football_Project.models import GroupMember, PoolGroup, User
from Football_Project.services.permissions import can_manage_group
from Football_Project.time_utils import ensure_dt_mt


class RegistrationGroupAndTimezoneTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-only",
            WTF_CSRF_ENABLED=False,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(self.app)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.context.pop()

    def test_registration_requires_name_and_phone(self):
        with self.app.test_request_context(method="POST", data={
            "username": "new_player",
            "email": "player@example.com",
            "password": "test-password",
            "password_confirm": "test-password",
        }):
            form = RegisterForm()
            form.group_id.choices = [(0, "Select a group")]
            self.assertFalse(form.validate())
            self.assertIn("first_name", form.errors)
            self.assertIn("last_name", form.errors)
            self.assertIn("phone", form.errors)

    def test_registration_normalizes_phone_to_e164(self):
        with self.app.test_request_context(method="POST", data={
            "first_name": "Pat",
            "last_name": "Player",
            "username": "new_player",
            "email": "player@example.com",
            "phone": "202-555-0123",
            "password": "test-password",
            "password_confirm": "test-password",
            "group_id": "0",
        }):
            form = RegisterForm()
            form.group_id.choices = [(0, "Select a group")]
            self.assertTrue(form.validate(), form.errors)
            self.assertEqual(form.phone.data, "+12025550123")

    def test_group_creator_can_manage_group_without_admin_role(self):
        creator = User(username="creator", password="test-only")
        db.session.add(creator)
        db.session.flush()
        group = PoolGroup(
            name="Creator Group",
            slug="creator-group",
            created_by_user_id=creator.id,
        )
        db.session.add(group)
        db.session.flush()
        db.session.add(GroupMember(
            user_id=creator.id,
            group_id=group.id,
            role="member",
            is_active=True,
        ))
        db.session.commit()

        self.assertTrue(can_manage_group(creator, group.id))

    def test_utc_kickoff_uses_mountain_calendar_date(self):
        sunday_night_utc = datetime(2026, 9, 14, 1, 20, tzinfo=timezone.utc)
        self.assertEqual(
            ensure_dt_mt(sunday_night_utc).date().isoformat(),
            "2026-09-13",
        )

    def test_group_selector_passes_delete_permission_to_renderer(self):
        template = (
            Path(__file__).parents[1] / "Football_Project" / "templates" / "groups.html"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "renderActions(groupId, isActiveGroup, canInvite, canDelete);",
            template,
        )


if __name__ == "__main__":
    unittest.main()
