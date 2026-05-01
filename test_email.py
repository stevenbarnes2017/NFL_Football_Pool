
from Football_Project.services.email_helpers import send_admin_email, send_all_users_email, send_user_email, send_group_email, send_group_missing_picks_email
from Football_Project import create_app

app = create_app()

with app.app_context():
    print("=== TEST: admin ===")
    send_admin_email(
        subject="[TEST] Admin Email",
        html="<p>Admin test</p>"
    )

    print("=== TEST: user ===")
    send_user_email(
        to_email="fakeuser@example.com",
        subject="[TEST] User Email",
        html="<p>User test</p>"
    )

    print("=== TEST: all users ===")
    send_all_users_email(
        subject="[TEST] All Users Email",
        html="<p>All users test</p>"
    )

    print("=== TEST: group ===")
    send_group_email(
        group_id=1,
        subject="[TEST] Group Email",
        html="<p>Group test</p>"
    )

    print("=== TEST: missing picks ===")
    send_group_missing_picks_email(
        group_id=1,
        season_year=2026,
        season_type="PRE",
        week=1,
        subject="[TEST] Missing Picks",
        html="<p>Missing picks test</p>"
    )

    print("=== DONE ===")