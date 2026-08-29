import unittest
from pathlib import Path

from flask import Flask
from flask_login import LoginManager

from Football_Project.admin import admin_bp
from Football_Project.auth import auth_bp
from Football_Project.extensions import db
from Football_Project.models import User
from Football_Project.routes import HELP_ARTICLES, main_bp


class HelpCenterTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(
            "Football_Project",
            template_folder="templates",
            static_folder="static",
        )
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="help-test-only",
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(self.app)
        login_manager = LoginManager()
        login_manager.init_app(self.app)

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(main_bp)

        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.user = User(username="help-reader", password="test-only")
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.context.pop()

    def _login(self):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(self.user.id)
            session["_fresh"] = True

    def test_help_center_requires_authentication(self):
        self.assertEqual(self.client.get("/help").status_code, 401)
        self.assertEqual(self.client.get("/help/getting-started").status_code, 401)

    def test_help_center_lists_every_configured_article(self):
        self._login()
        response = self.client.get("/help")
        self.assertEqual(response.status_code, 200)
        for slug, article in HELP_ARTICLES.items():
            self.assertIn(article["title"].encode(), response.data)
            self.assertIn(f'/help/{slug}'.encode(), response.data)

    def test_every_configured_help_article_renders(self):
        self._login()
        for slug in HELP_ARTICLES:
            with self.subTest(slug=slug):
                response = self.client.get(f"/help/{slug}")
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'class="help-article"', response.data)

    def test_markdown_headings_lists_and_emphasis_render_as_html(self):
        self._login()
        response = self.client.get("/help/getting-started")
        self.assertIn(b"<h1>Getting Started with SundayPickems</h1>", response.data)
        self.assertIn(b"<h2>1. Sign In</h2>", response.data)
        self.assertIn(b"<strong>Select Picks</strong>", response.data)
        picks_response = self.client.get("/help/making-picks")
        self.assertIn(b"<ul>", picks_response.data)

    def test_unknown_slug_returns_404(self):
        self._login()
        self.assertEqual(self.client.get("/help/not-configured").status_code, 404)

    def test_allowlist_filenames_are_plain_markdown_files(self):
        help_dir = Path(self.app.root_path) / "help"
        for article in HELP_ARTICLES.values():
            filename = article["filename"]
            self.assertEqual(Path(filename).name, filename)
            self.assertEqual(Path(filename).suffix, ".md")
            self.assertTrue((help_dir / filename).is_file())

    def test_help_navigation_order_includes_desktop_and_mobile(self):
        template = (
            Path(self.app.root_path) / "templates" / "base.html"
        ).read_text(encoding="utf-8")
        segments = template.split("main.edit_profile")
        self.assertGreaterEqual(len(segments), 3)
        for following in segments[1:3]:
            self.assertLess(
                following.index("main.help_center"),
                following.index("Contact Support"),
            )


if __name__ == "__main__":
    unittest.main()
