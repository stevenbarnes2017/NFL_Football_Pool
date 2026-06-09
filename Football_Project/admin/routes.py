# Football_Project/admin/routes.py
from flask import render_template, request, redirect, url_for, flash, send_file, current_app, abort, Blueprint, session
from flask_login import login_required, current_user
from datetime import datetime, timezone
import os
from sqlalchemy import func, literal, or_
from . import admin_bp
from collections import defaultdict
from zoneinfo import ZoneInfo
# Data / services
from Football_Project.get_the_odds import get_nfl_spreads, save_spreads_to_db, save_to_csv
from football_scores import get_football_scores, save_scores_to_csv  # NOTE: don't import save_scores_to_db here
from Football_Project.models import db, Game, Settings, User, UserScore, Pick, JobRun, Announcement, GroupMember, PoolGroup
from Football_Project.utils import calculate_user_scores, save_game_scores_to_db  # keep the utils version
from werkzeug.security import generate_password_hash
from Football_Project.services.sms_helpers import sms_week_reminder_job
from Football_Project.services.season import get_current_season_context, get_current_week
from Football_Project.services.schedule_service import update_schedule
from Football_Project.services.group_service import get_active_group_id


#--------------------------
# Admin Announcements
#--------------------------

@admin_bp.route("/board", methods=["GET"])
@login_required
def admin_board():
    from ..services.permissions import can_manage_group
    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    return render_template("admin_board.html")


@admin_bp.route("/announcements", methods=["GET"])
@login_required
def admin_announcements():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    # optional: prefill season context defaults
    season_year, season_type = get_current_season_context()

    announcements = (
        Announcement.query
        .filter(Announcement.is_active.is_(True))
        .order_by(Announcement.pinned.desc(), Announcement.created_at.desc())
        .all()
    )

    return render_template(
        "admin_announcements.html",
        announcements=announcements,
        season_year=season_year,
        season_type=season_type,
    )


@admin_bp.route("/announcements/new", methods=["POST"])
@login_required
def admin_announcement_new():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    title = (request.form.get("title") or "").strip()
    body = (request.form.get("body") or "").strip()

    # optional context fields
    season_year = request.form.get("season_year", type=int)
    season_type = (request.form.get("season_type") or "").strip().upper() or None
    week = request.form.get("week", type=int)

    pinned = True if request.form.get("pinned") in ("1", "on", "true", "True") else False

    if not title or not body:
        flash("Title and message are required.", "danger")
        return redirect(url_for("admin.admin_announcements"))

    try:
        ann = Announcement(
            title=title,
            body=body,
            created_by_user_id=current_user.id,
            season_year=season_year,
            season_type=season_type,
            week=week,
            pinned=pinned,
            is_active=True,
        )
        db.session.add(ann)
        db.session.commit()
        flash("Announcement posted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to post announcement: {e}", "danger")

    return redirect(url_for("admin.admin_announcements"))


@admin_bp.route("/announcements/<int:ann_id>/toggle_pin", methods=["POST"])
@login_required
def admin_toggle_announcement_pin(ann_id):
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    ann = Announcement.query.get_or_404(ann_id)

    try:
        ann.pinned = not bool(ann.pinned)
        db.session.commit()
        flash(f"Announcement {'pinned' if ann.pinned else 'unpinned'}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to update: {e}", "danger")

    return redirect(url_for("admin.admin_announcements"))


@admin_bp.route("/announcements/<int:ann_id>/delete", methods=["POST"])
@login_required
def admin_delete_announcement(ann_id):
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    ann = Announcement.query.get_or_404(ann_id)

    try:
        ann.is_active = False
        db.session.commit()
        flash("Announcement removed.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to remove: {e}", "danger")

    return redirect(url_for("admin.admin_announcements"))

   



#--------------------------
# Admin Game Schedule 
#--------------------------

@admin_bp.route("/update_schedule", methods=["POST"])
@login_required
def admin_update_schedule():
    from datetime import datetime
    from Football_Project.extensions import db
    from Football_Project.models import JobRun
    from Football_Project.services.schedule_service import update_schedule
    from Football_Project.services.season import get_current_season_context
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))

    # single source of truth
    season_year, season_type_label = get_current_season_context()

    season_type_map = {"PRE": 1, "REG": 2, "POST": 3}
    season_type = season_type_map.get((season_type_label or "REG").upper(), 2)

    # optional override from form (week range)
    try:
        week_end = int(request.form.get("week_end", 18))
    except ValueError:
        week_end = 18

    try:
        result = update_schedule(
            season_year=season_year,
            season_type=season_type,
            week_start=1,
            week_end=week_end,
        )

        # ✅ record job run
        jr = JobRun(
            job_name="schedule_update",
            ran_at=datetime.utcnow(),
            ok=True,
            inserted=result.get("inserted", 0),
            updated=result.get("updated", 0),
            unchanged=result.get("unchanged", 0),
            failed_weeks=result.get("failed_weeks", 0),
            message=f"Manual schedule update from admin (Y{season_year} {season_type_label}, weeks 1-{week_end})",
        )
        db.session.add(jr)
        db.session.commit()

        flash(
            f"Schedule updated: "
            f"{result.get('inserted', 0)} added, "
            f"{result.get('updated', 0)} updated, "
            f"{result.get('unchanged', 0)} unchanged"
            + (f", {result.get('failed_weeks', 0)} week(s) failed" if result.get("failed_weeks", 0) else ""),
            "success",
        )

    except Exception as e:
        db.session.rollback()

        # ✅ record failed job run
        try:
            jr = JobRun(
                job_name="schedule_update",
                ran_at=datetime.utcnow(),
                ok=False,
                inserted=0,
                updated=0,
                unchanged=0,
                failed_weeks=0,
                message=str(e)[:500],
            )
            db.session.add(jr)
            db.session.commit()
        except Exception:
            db.session.rollback()

        flash(f"Schedule update failed: {e}", "danger")

    return redirect(url_for("admin.admin_dashboard"))


#--------------------------
# Admin User Views
#--------------------------
@admin_bp.route("/view_as_user", methods=["POST"])
@login_required
def view_as_user():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    
    user_id = request.form.get("user_id", type=int)
    if not user_id:
        flash("Please select a user.", "warning")
        return redirect(url_for("admin.manage_users"))

    # ✅ USE THE SAME KEY nfl_picks READS
    session["view_as_user_id"] = user_id
    session.modified = True

    flash(f"Now viewing as user {user_id}.", "success")
    return redirect(url_for("main.user_dashboard"))

@admin_bp.route("/exit_view_as_user", methods=["POST"])
@login_required
def exit_view_as_user():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    
    session.pop("view_as_user_id", None)
    session.modified = True

    flash("View-as user disabled.", "info")
    return redirect(url_for("admin.manage_users"))

@admin_bp.route("/force_exit_view_as", methods=["GET"])
@login_required
def force_exit_view_as():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    

    session.pop("view_as_user_id", None)
    session.pop("admin_view_as_user_id", None)
    session.modified = True
    return "OK: view-as cleared"

@admin_bp.route("/debug_session", methods=["GET"])
@login_required
def debug_session():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    
    return f"session={dict(session)}"



@admin_bp.route("/test_sms/<int:week>")
@login_required
def test_sms_week(week):
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    """Manually trigger the SMS reminder job for a given week."""
    try:
        sms_week_reminder_job(current_app, week)
        flash(f"Test SMS job executed for Week {week}", "success")
    except Exception as e:
        current_app.logger.exception(e)
        flash(f"SMS job failed: {e}", "danger")
    return redirect(url_for("main.dashboard"))

# -------------------------
# Guards
# -------------------------

@admin_bp.before_request
def admin_guard():
    from ..services.permissions import can_manage_group

    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    active_group_id = session.get("active_group_id")
    if not active_group_id:
        flash("No active group selected.", "warning")
        return redirect(url_for("main.groups"))

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))

# -------------------------
# User management
# -------------------------

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not active_group_id:
        flash("No active group selected.", "warning")
        return redirect(url_for("main.user_dashboard"))

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))

    active_group = PoolGroup.query.get(active_group_id)

    memberships = (
        GroupMember.query
        .filter_by(group_id=active_group_id, is_active=True)
        .all()
    )

    user_ids = [m.user_id for m in memberships]

    users = (
        User.query
        .filter(User.id.in_(user_ids))
        .order_by(User.username)
        .all()
    ) if user_ids else []

    membership_by_user_id = {m.user_id: m for m in memberships}

    user_rows = []
    for user in users:
        membership = membership_by_user_id.get(user.id)

        user_rows.append({
            "user": user,
            "membership": membership,
            "is_group_admin": bool(
                membership
                and (membership.role or "").strip().lower() == "group_admin"
            ),
        })

    return render_template(
        'manage_users.html',
        user_rows=user_rows,
        active_group=active_group,
    )

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash("Only global admins can edit user accounts.", "danger")
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.full_name = request.form.get('full_name', user.full_name)
        user.email = request.form.get('email', user.email)
        user.phone = request.form.get('phone', user.phone)
        user.favorite_team = request.form.get('favorite_team', user.favorite_team)
        user.is_admin = request.form.get('is_admin') in ('1', 'on', 'true', 'True')

        new_password = request.form.get('new_password')
        if new_password:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        flash('User updated!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('edit_user.html', user=user)

@admin_bp.route('/update_admin_status/<int:user_id>', methods=['POST'])
@login_required
def update_admin_status(user_id):
    if not current_user.is_admin:
        flash("Only global admins can change global admin status.", "danger")
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)

    vals = [v.strip().lower() for v in request.form.getlist('is_admin')]
    new_is_admin = any(v in ('1', 'true', 'on', 'yes') for v in vals)

    if user.id == current_user.id and not new_is_admin:
        flash("You can’t remove your own admin rights.", "warning")
        return redirect(url_for('admin.manage_users'))

    if not new_is_admin and User.query.filter_by(is_admin=True).count() <= 1:
        flash("At least one global admin is required.", "warning")
        return redirect(url_for('admin.manage_users'))

    user.is_admin = new_is_admin
    db.session.commit()
    flash("Global admin status updated.", "success")
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Only global admins can deactivate user accounts.", "danger")
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You can’t deactivate your own account.", "warning")
        return redirect(url_for('admin.manage_users'))

    if user.is_admin and User.query.filter_by(is_admin=True, is_active=True).count() <= 1:
        flash("You can’t deactivate the last global admin.", "warning")
        return redirect(url_for('admin.manage_users'))

    user.is_active = False

    GroupMember.query.filter_by(user_id=user.id, is_active=True).update(
        {"is_active": False},
        synchronize_session=False
    )

    db.session.commit()
    flash('User deactivated successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash("Only global admins can add users.", "danger")
        return redirect(url_for('admin.manage_users'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        is_admin = request.form.get('is_admin') in ('1', 'on', 'true', 'True')

        if not username or not email or not password:
            flash("All fields (username, email, password) are required.", "danger")
            return redirect(url_for('admin.add_user'))

        if User.query.filter_by(email=email).first():
            flash(f"User with email {email} already exists.", "danger")
            return redirect(url_for('admin.add_user'))

        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed, is_admin=is_admin)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")

        return redirect(url_for('admin.admin_dashboard'))

    return render_template('add_user.html')

def _last_odds_fetch_for_week(week: int):
    
    ts = db.session.query(func.max(Game.saved_at)).filter(Game.week == week).scalar()
    if not ts:
        return None
    # saved_at is naive UTC; mark as UTC then render in MT
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(ZoneInfo("US/Mountain")).strftime("%Y-%m-%d %I:%M %p %Z")

def _settings_to_espn_seasontype(settings) -> int:
    
    if not settings or not settings.season_type:
        return 2

    st = settings.season_type.upper()
    if st in ("PRE", "PRESEASON"):
        return 1
    if st in ("REG", "REGULAR"):
        return 2
    if st in ("POST", "POSTSEASON", "PLAYOFFS"):
        return 3

    return 2

def in_view_as_mode():
    
    return bool(session.get("view_as_user_id") or session.get("admin_view_as_user_id"))

@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    session.pop("view_as_user_id", None)
    session.pop("admin_view_as_user_id", None)
    session.modified = True
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    print("ADMIN_DASH session keys:", dict(session))  # TEMP DEBUG

    if in_view_as_mode():
        flash("View-as mode is active.", "warning")
        return redirect(url_for("main.user_dashboard"))

    settings = Settings.query.first()

    season_year = settings.season_year if settings else datetime.utcnow().year
    season_type = (settings.season_type if settings else "REG")
    current_week = settings.current_week

    last_odds_fetch = _last_odds_fetch_for_week(current_week)

    last_schedule_sync = (
        JobRun.query
        .filter_by(job_name="schedule_update")
        .order_by(JobRun.ran_at.desc())
        .first()
    )

    weeks = list(range(1, current_week + 1))

    # get active group id
    active_group_id = session.get("active_group_id")
    if not active_group_id:
        flash("No active group selected.", "warning")
        return redirect(url_for("main.user_dashboard"))

    # only users in active group
    users = (
        User.query
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == active_group_id)
        .order_by(User.username)
        .all()
    )

    total_games = (
        db.session.query(func.count(Game.id))
        .filter(
            Game.week == current_week,
            Game.season_year == season_year,
            Game.season_type == season_type,
        )
        .scalar() or 0
    )

    active_group_id = session.get("active_group_id")
    if not active_group_id:
        flash("No active group selected.", "warning")
        return redirect(url_for("main.user_dashboard"))

    counts = _missing_counts_for_week(
        week=current_week,
        group_id=active_group_id,
        season_year=season_year,
        season_type=season_type,
    )

    now_mt = datetime.now(ZoneInfo("America/Denver"))

    locked_games = (
        db.session.query(func.count(Game.id))
        .filter(
            Game.week == current_week,
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.commence_time_mt <= now_mt,
        )
        .scalar() or 0
    )

    remaining = max(0, (total_games or 0) - locked_games)

    last_grading = db.session.query(func.max(UserScore.calculated_at)).scalar()

    stats = {
        "current_week": current_week,
        "total_games": total_games or 0,
        "locked_games": locked_games,
        "remaining_games": remaining,
        "last_grading": last_grading,
        "last_odds_fetch": last_odds_fetch,
    }

    return render_template(
        'admin_dashboard.html',
        settings=settings,
        current_year=season_year,
        season_type=season_type,
        weeks=weeks,
        users=users,
        current_week=current_week,
        week=current_week,
        counts=counts,
        stats=stats,
        last_schedule_sync=last_schedule_sync,
    )

@admin_bp.route('/fetch_odds', methods=['POST'])
@login_required
def fetch_odds():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    try:
        settings = Settings.query.first()
        if not settings:
            flash("Settings not found. Please initialize Settings first.", "danger")
            return redirect(url_for('admin.admin_dashboard'))

        week_option = request.form.get('week_option')

        # ✅ Use Settings.current_week unless admin overrides
        if week_option == 'override':
            week = int(request.form.get('week_number'))
        else:
            week = settings.current_week

        games_list, num_of_games = get_nfl_spreads()

        if not games_list:
            flash("No odds data available for the selected week.", "warning")
            return redirect(url_for('admin.admin_dashboard'))

        action = request.form.get('action')

        if action == "csv":
            filename = f'nfl_spreads_week_{week}.csv'
            save_path = os.path.join(current_app.root_path, 'static', 'downloads', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            save_to_csv(games_list, save_path)
            return send_file(save_path, as_attachment=True)

        if action == "db":
            save_spreads_to_db(games_list, week)
            flash(f"Odds for week {week} have been successfully saved to the database.", "success")
            return redirect(url_for('admin.admin_dashboard'))

        return render_template('display_odds.html', games_list=games_list, week=week)

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"An error occurred while fetching the odds: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/save_odds', methods=['POST'])
@login_required
def save_odds():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    try:
        settings = Settings.query.first()
        if not settings:
            flash("Settings not found. Please initialize Settings first.", "danger")
            return redirect(url_for('admin.admin_dashboard'))

        action = request.form.get('action')
        form_week = request.form.get('week')

        # ✅ Use posted week if present, else Settings.current_week
        week = int(form_week) if form_week else settings.current_week

        games_list, _ = get_nfl_spreads()

        if not games_list:
            flash("No odds data available.", "warning")
            return redirect(url_for('admin.admin_dashboard'))

        if action == "db":
            save_spreads_to_db(games_list, week)
            flash(f"Odds for week {week} have been saved to the database.", "success")

        elif action == "csv":
            filename = f'nfl_spreads_week_{week}.csv'
            save_dir = os.path.join(current_app.root_path, 'static', 'downloads')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            save_to_csv(games_list, save_path)
            return send_file(save_path, as_attachment=True)

        else:
            flash("Invalid action.", "danger")

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/display_odds')
@login_required
def display_odds():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    settings = Settings.query.first()
    current_week = settings.current_week
    games = Game.query.filter_by(week=current_week).all()
    return render_template('display_odds.html', games_list=games, week=current_week)

# -------------------------
# Scores (fetch / admin)
# -------------------------

@admin_bp.route('/fetch_scores', methods=['POST'])
@login_required
def fetch_scores():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    # year, season type, week from form
    settings = Settings.query.first()
    year = int(request.form.get("year") or settings.season_year)
    seasontype = int(request.form.get("seasontype") or _settings_to_espn_seasontype(settings))
    weeknum = int(request.form.get("weeknum") or settings.current_week)
    action = request.form.get('action')

    try:
        scores = get_football_scores(year, seasontype, weeknum)

        if action == 'save_to_db':
            # Save raw game scores to DB (your util handles mapping)
            save_game_scores_to_db(scores, weeknum)
            flash(f"Successfully saved game scores for week {weeknum}.", "success")

        elif action == 'download_csv':
            filename = f"football_scores_week{weeknum}.csv"
            save_dir = os.path.join(current_app.root_path, 'static', 'downloads')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            save_scores_to_csv(scores, save_path)
            return send_file(save_path, as_attachment=True)

    except Exception as e:
        current_app.logger.exception("Error fetching/saving scores")
        flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin_scores', methods=['GET'])
@login_required
def admin_scores():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    selected_week = request.args.get("week", "all")
    selected_user = request.args.get("user", "all")

    active_group_id = session.get("active_group_id")
    if not active_group_id:
        flash("No active group selected.", "warning")
        return redirect(url_for("main.user_dashboard"))

    # ✅ season context
    season_year, season_type_label = get_current_season_context()

    # sanitize inputs
    try:
        if selected_week != "all":
            selected_week = int(selected_week)
    except ValueError:
        flash("Invalid week selected.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    try:
        if selected_user != "all":
            selected_user = int(selected_user)
    except ValueError:
        flash("Invalid user selected.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    memberships = GroupMember.query.filter_by(group_id=active_group_id).all()
    user_ids = [m.user_id for m in memberships]

    all_users = (
        User.query
        .filter(User.id.in_(user_ids))
        .order_by(User.username)
        .all()
    ) if user_ids else []

    # -------------------------------------------------------
    # ✅ Games: always filter to current season + optional week
    # Games are global, so no group filter here
    # -------------------------------------------------------
    games_q = Game.query.filter(
        Game.season_year == season_year,
        Game.season_type == season_type_label
    )

    if selected_week != "all":
        games_q = games_q.filter(Game.week == selected_week)

    games = games_q.order_by(Game.week.asc(), Game.id.asc()).all()

    # -------------------------------------------------------
    # ✅ Picks: join Game so season filter is guaranteed
    # ✅ Group-scoped via Pick.group_id
    # -------------------------------------------------------
    picks_q = (
        db.session.query(Pick)
        .join(Game, Game.id == Pick.game_id)
        .join(User, User.id == Pick.user_id)
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type_label,
            Pick.group_id == active_group_id
        )
    )

    if selected_week != "all":
        picks_q = picks_q.filter(Pick.week == selected_week)

    if selected_user != "all":
        # optional extra safety so a user from another group can't be forced in by URL
        if selected_user not in user_ids:
            flash("Invalid user selected for this group.", "danger")
            return redirect(url_for("admin.admin_scores", week=selected_week))
        picks_q = picks_q.filter(Pick.user_id == selected_user)

    picks = picks_q.all()

    # -------------------------------------------------------
    # ✅ Totals: computed from picks, season-filtered via Game
    # ✅ Group-scoped via Pick.group_id
    # -------------------------------------------------------
    user_totals = {u.username: 0 for u in all_users}

    totals_q = (
        db.session.query(User.username, func.coalesce(func.sum(Pick.points_earned), 0))
        .join(Pick, Pick.user_id == User.id)
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type_label,
            Pick.group_id == active_group_id
        )
    )

    if selected_week != "all":
        totals_q = totals_q.filter(Pick.week == selected_week)

    if selected_user != "all":
        totals_q = totals_q.filter(Pick.user_id == selected_user)

    totals_q = totals_q.group_by(User.username).all()

    for uname, total in totals_q:
        user_totals[uname] = int(total or 0)

    # -------------------------------------------------------
    # Index picks by game for fast build
    # -------------------------------------------------------
    picks_by_game: dict[int, list[Pick]] = defaultdict(list)
    for p in picks:
        picks_by_game[p.game_id].append(p)

    def winner_for(g: Game):
        
        if g.home_team_score is None or g.away_team_score is None:
            return None
        if g.home_team_score > g.away_team_score:
            return g.home_team
        if g.away_team_score > g.home_team_score:
            return g.away_team
        return "TIE"

    game_picks = []
    for g in games:
        win = winner_for(g)
        grp = {
            "game_id": g.id,
            "home_team": g.home_team,
            "away_team": g.away_team,
            "spread": g.spread,
            "favorite_team": g.favorite_team,
            "home_team_score": g.home_team_score,
            "away_team_score": g.away_team_score,
            "status": g.status,
            "winner": win,
            "picks": []
        }

        for p in picks_by_game.get(g.id, []):
            is_correct = (win is not None and p.team_picked == win)
            grp["picks"].append({
                "username": p.user.username,
                "user_id": p.user_id,
                "team_picked": p.team_picked,
                "confidence": p.confidence,
                "points_earned": p.points_earned,
                "is_correct": is_correct,
            })

        game_picks.append(grp)

    # -------------------------------------------------------
    # ✅ Weeks dropdown: season-filtered
    # Games are global, so no group filter here
    # -------------------------------------------------------
    weeks = [
        w for (w,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type_label
            )
            .distinct()
            .order_by(Game.week)
            .all()
        )
        if w is not None
    ]

    # -------------------------------------------------------
    # ✅ locked/total stats: season-filtered
    # Games are global, so no group filter here
    # -------------------------------------------------------
    locked_count = total_games = None
    if selected_week != "all":
        now_mt = datetime.now(ZoneInfo("US/Mountain"))

        locked_count = (
            db.session.query(func.count(Game.id))
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type_label,
                Game.week == selected_week,
                Game.commence_time_mt <= now_mt
            )
            .scalar() or 0
        )

        total_games = (
            db.session.query(func.count(Game.id))
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type_label,
                Game.week == selected_week
            )
            .scalar() or 0
        )

    return render_template(
        "admin_scores.html",
        game_picks=game_picks,
        user_totals=user_totals,
        selected_week=selected_week,
        weeks=weeks,
        selected_user=selected_user,
        users=all_users,
        locked_count=locked_count,
        total_games=total_games,
        season_year=season_year,
        season_type=season_type_label,
    )

@admin_bp.route("/admin_calculate_scores", methods=["POST"])
@login_required
def admin_calculate_scores():

    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    if not getattr(current_user, "is_admin", False):
        flash("Not authorized.", "danger")
        return redirect(url_for("main.user_dashboard"))

    settings = Settings.query.first()
    if not settings:
        flash("Settings row missing. Cannot calculate scores.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    season_year = settings.season_year
    season_type = settings.season_type
    current_week = settings.current_week

    # Form options:
    # week = "all" OR "all_except_current" OR a number like "3"
    form_week = request.form.get("week", "all_except_current")

    # Build weeks list for THIS season/year/type only
    season_weeks = [
        w for (w,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type,
                Game.week.isnot(None),
            )
            .distinct()
            .order_by(Game.week.asc())
            .all()
        )
    ]

    if not season_weeks:
        flash("No games found for this season context. Load schedule first.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    if form_week == "all":
        weeks_to_process = [w for w in season_weeks if w <= current_week]
    elif form_week == "all_except_current":
        weeks_to_process = [w for w in season_weeks if w <= current_week and w != current_week]
    else:
        try:
            w = int(form_week)
        except ValueError:
            flash("Invalid week selected.", "danger")
            return redirect(url_for("admin.admin_dashboard"))

        if w not in season_weeks:
            flash(f"Week {w} not found for {season_year} {season_type}.", "warning")
            return redirect(url_for("admin.admin_dashboard"))

        weeks_to_process = [w]

    if not weeks_to_process:
        flash("No weeks to process.", "info")
        return redirect(url_for("admin.admin_dashboard"))

    try:
        processed = 0
        for w in weeks_to_process:
            # IMPORTANT: use season context
            calculate_user_scores(
                week=w,
                season_year=season_year,
                season_type=season_type,
                write_final_only=True,   # only FINAL games contribute to UserScore
            )
            processed += 1

        db.session.commit()
        if processed == 1:
            flash(f"Scores recalculated for Week {weeks_to_process[0]} ({season_year} {season_type}).", "success")
        else:
            flash(
                f"Scores recalculated for {season_year} {season_type} weeks "
                f"{min(weeks_to_process)}–{max(weeks_to_process)}.",
                "success",
            )

    except Exception as e:
        db.session.rollback()
        flash(f"Error while calculating scores: {e}", "danger")

    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route('/admin_override_score', methods=['POST'])
@login_required
def admin_override_score():
    from Football_Project.services.group_service import get_active_group_id
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    user_id = request.form.get('user_id', type=int)
    week = request.form.get('week', type=int)
    game_id = request.form.get('game_id', type=int)
    new_score = request.form.get('new_score')

    group_id = get_active_group_id()

    try:
        new_score = float(new_score)
    except (TypeError, ValueError):
        flash("Invalid score value.", "danger")
        return redirect(url_for('admin.admin_scores', week=week))

    pick = Pick.query.filter_by(
        user_id=user_id,
        game_id=game_id,
        week=week,
        group_id=group_id,
    ).first()

    if not pick:
        flash("Pick not found.", "danger")
        return redirect(url_for('admin.admin_scores', week=week))

    pick.points_earned = new_score
    pick.is_overridden = True
    db.session.add(pick)
    db.session.commit()

    # Recompute totals for that week/group
    user_scores = calculate_user_scores(week=week, group_id=group_id)

    row = UserScore.query.filter_by(user_id=user_id, week=week).first()
    if row:
        row.score = user_scores.get(user_id, row.score)
    else:
        db.session.add(
            UserScore(
                user_id=user_id,
                week=week,
                score=user_scores.get(user_id, 0),
                calculated_at=datetime.utcnow(),
            )
        )
    db.session.commit()

    flash("Score successfully overridden and totals updated.", "success")
    return redirect(url_for('admin.admin_scores', week=week))

@admin_bp.route('/process_user_scores', methods=['POST'])
@login_required
def process_user_scores():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    try:
        settings = Settings.query.first()
        season_year = settings.season_year
        season_type = settings.season_type
        current_week = settings.current_week

        # Weeks available for THIS season/type
        season_weeks = [
            w for (w,) in (
                db.session.query(Game.week)
                .filter(Game.season_year==season_year, Game.season_type==season_type)
                .distinct()
                .order_by(Game.week)
                .all()
            )
        ]

        form_week = request.form.get('week', 'all')
        if form_week != 'all':
            week = int(form_week)
            weeks = [week]
        else:
            # ✅ don’t exclude week 1; instead exclude weeks that aren’t final yet (optional)
            weeks = season_weeks

        for w in weeks:
            calculate_user_scores(
                week=w,
                season_year=season_year,
                season_type=season_type,
                write_final_only=True
            )

        db.session.commit()
        flash(f"Successfully processed scores for {season_type} {season_year} week(s): {weeks}", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while processing user scores: {str(e)}", "danger")

    return redirect(url_for('admin.admin_dashboard'))


# assumes you already have these:
# from Football_Project import db
# from Football_Project.models import User, Pick, Game
# from Football_Project.utils import get_current_week  # or wherever you defined it

def _total_games_for_week(week: int) -> int:
    return db.session.query(func.count(Game.id)).filter(Game.week == week).scalar() or 0

def _user_pick_aggregate_for_week(week: int):
    
    """
    Returns a query with per-user aggregates for the given week:
      - picks_made (count)
      - last_pick_time (max created_at)
    Then outer-joins to all users so admins see every user row, even with 0 picks.
    """
    # subquery: per-user pick counts and latest timestamp for the target week
    pick_agg = (
        db.session.query(
            Pick.user_id.label("user_id"),
            func.count(Pick.id).label("picks_made"),
            func.max(Pick.pick_time).label("last_pick_time"),
        )
        .filter(Pick.week == week)
        .group_by(Pick.user_id)
        .subquery()
    )

    return pick_agg





def _missing_counts_for_week(
    week: int,
    group_id: int,
    season_year: int,
    season_type: str,
) -> dict:
    """
    Missing picks = for UNLOCKED games in the selected season/week,
    count per user in the active group how many valid picks are missing
    (no row OR confidence is NULL).
    Returns a dict with 'rows' for UI use.
    """
    now_mt = datetime.now(ZoneInfo("US/Mountain"))

    total_games = (
        db.session.query(func.count(Game.id))
        .filter(
            Game.week == week,
            Game.season_year == season_year,
            Game.season_type == season_type,
        )
        .scalar()
        or 0
    )

    # Unlocked games only for this season/week
    unlocked_ids = [
        gid
        for (gid,) in db.session.query(Game.id)
        .filter(
            Game.week == week,
            Game.season_year == season_year,
            Game.season_type == season_type,
            or_(Game.commence_time_mt.is_(None), Game.commence_time_mt > now_mt),
        )
        .all()
    ]
    unlocked_count = len(unlocked_ids)

    # Only users in this group
    users = (
        db.session.query(User.id, User.username)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .order_by(User.username)
        .all()
    )

    # Valid picks among unlocked games for this group only
    valid_by_user = {}
    if unlocked_count:
        valid_rows = (
            db.session.query(Pick.user_id, func.count(Pick.id))
            .filter(
                Pick.week == week,
                Pick.group_id == group_id,
                Pick.confidence.isnot(None),
                Pick.game_id.in_(unlocked_ids),
            )
            .group_by(Pick.user_id)
            .all()
        )
        valid_by_user = {uid: int(c or 0) for uid, c in valid_rows}

    rows = []
    by_user = {}
    missing_total = 0

    for uid, uname in users:
        made = valid_by_user.get(uid, 0)
        miss = max(0, unlocked_count - made)

        row = {
            "user_id": uid,
            "username": uname,
            "missing": miss,
            "remaining": miss,
            "made": made,
            "picks_made": made,
        }
        rows.append(row)
        by_user[uname] = miss
        missing_total += miss

    rows.sort(key=lambda r: (-r["missing"], r["username"].lower()))

    return {
        "week": week,
        "total_games": total_games,
        "unlocked_games": unlocked_count,
        "by_user": by_user,
        "missing_total": missing_total,
        "rows": rows,
    }

@admin_bp.route('/missing_picks', methods=['GET'])
@login_required
def missing_picks():
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    settings = Settings.query.first()
    if not settings:
        flash("Settings not found. Please initialize Settings first.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    # Inputs (defaults)
    week = request.args.get('week', type=int) or settings.current_week
    filter_opt = request.args.get('filter', 'any')  # any | zero | complete | all

    # Core counts (unlocked-aware)
    counts = _missing_counts_for_week(week)
    total_games = counts.get('total_games', 0)

    # Summary tiles
    zero_count = sum(1 for r in counts['rows'] if r['made'] == 0)
    any_count = sum(1 for r in counts['rows'] if r['missing'] > 0)
    complete_count = sum(1 for r in counts['rows'] if r['missing'] == 0)

    # Last-pick time (optional) and include exact keys the template needs
    pick_agg = _user_pick_aggregate_for_week(week)
    last_map = dict(
        db.session.query(pick_agg.c.user_id, pick_agg.c.last_pick_time).all()
    )

    display_rows = []
    for r in counts['rows']:
        uid = r['user_id']
        picks_made = r['made']            # valid picks (confidence set) among UNLOCKED games
        remaining = r['missing']          # unlocked - valid
        progress_pct = int((picks_made * 100) // total_games) if total_games else 0

        display_rows.append({
            "user_id": uid,
            "username": r['username'],
            "picks_made": picks_made,
            "remaining": remaining,
            "progress_pct": progress_pct,
            "last_pick_time": last_map.get(uid),
        })

    # Table filter
    if filter_opt == 'zero':
        display_rows = [r for r in display_rows if r['picks_made'] == 0]
    elif filter_opt == 'any':
        display_rows = [r for r in display_rows if r['remaining'] > 0]
    elif filter_opt == 'complete':
        display_rows = [r for r in display_rows if r['remaining'] == 0]
    # 'all' → no filter

    # Sort: most missing first, then username
    display_rows.sort(key=lambda r: (-r["remaining"], r["username"].lower()))

    return render_template(
        "missing_picks.html",
        week=week,
        filter=filter_opt,
        total_games=total_games,
        rows=display_rows,
        zero_count=zero_count,
        any_count=any_count,
        complete_count=complete_count,
    )




@admin_bp.route('/user_picks/<int:user_id>', methods=['GET'], endpoint='view_user_picks')
@login_required
def view_user_picks(user_id: int):
    from ..services.permissions import can_manage_group

    active_group_id = session.get("active_group_id")

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.user_dashboard"))
    

    settings = Settings.query.first()
    if not settings:
        flash("Settings not found. Please initialize Settings first.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    group_id = get_active_group_id()

    week = request.args.get('week', type=int) or settings.current_week

    user = User.query.get_or_404(user_id)
    total_games = _total_games_for_week(week)

    joined_rows = []
    joined = False

    # Try best-available join path in order of specificity
    try:
        if hasattr(Pick, 'game_id'):
            # 1) Direct game_id join
            joined_rows = (
                db.session.query(Pick, Game)
                .join(Game, Game.id == Pick.game_id)
                .filter(
                    Pick.user_id == user_id,
                    Pick.week == week,
                    Pick.group_id == group_id,
                )
                .order_by(Game.commence_time_mt.asc())
                .all()
            )
            joined = True

        elif hasattr(Pick, 'home_team') and hasattr(Pick, 'away_team'):
            # 2) Join by explicit teams + week
            joined_rows = (
                db.session.query(Pick, Game)
                .join(
                    Game,
                    (Game.week == Pick.week)
                    & (Game.home_team == Pick.home_team)
                    & (Game.away_team == Pick.away_team)
                )
                .filter(
                    Pick.user_id == user_id,
                    Pick.week == week,
                    Pick.group_id == group_id,
                )
                .order_by(Game.commence_time_mt.asc())
                .all()
            )
            joined = True

        elif hasattr(Pick, 'team_picked'):
            # 3) Join by week + the team picked belonging to the game
            joined_rows = (
                db.session.query(Pick, Game)
                .join(
                    Game,
                    (Game.week == Pick.week)
                    & or_(Game.home_team == Pick.team_picked,
                          Game.away_team == Pick.team_picked)
                )
                .filter(
                    Pick.user_id == user_id,
                    Pick.week == week,
                    Pick.group_id == group_id,
                )
                .order_by(Game.commence_time_mt.asc())
                .all()
            )
            joined = True
    except Exception:
        joined = False

    if joined:
        def norm(p, g):
            pick_team = getattr(p, 'team_picked', None)
            confidence = (
                getattr(p, 'confidence', None)
                or getattr(p, 'confidence_points', None)
                or getattr(p, 'confidence_number', None)
            )
            kickoff = getattr(g, 'commence_time_mt', None) or getattr(g, 'commence_time', None)
            matchup = f"{getattr(g,'away_team','?')} @ {getattr(g,'home_team','?')}"
            return dict(matchup=matchup, kickoff=kickoff, pick_team=pick_team, confidence=confidence)

        view_rows = [norm(p, g) for (p, g) in joined_rows]
        picks_made = len(view_rows)

    else:
        picks = (
            Pick.query.filter_by(
                user_id=user_id,
                week=week,
                group_id=group_id,
            )
            .order_by(getattr(Pick, 'pick_time', getattr(Pick, 'created_at', Pick.id)).desc())
            .all()
        )

        def norm_p(p):
            pick_team = getattr(p, 'team_picked', None)
            confidence = (
                getattr(p, 'confidence', None)
                or getattr(p, 'confidence_points', None)
                or getattr(p, 'confidence_number', None)
            )
            matchup = getattr(p, "matchup", None) or f"Game #{getattr(p, 'game_id', '—')}"
            kickoff = None
            return dict(matchup=matchup, kickoff=kickoff, pick_team=pick_team, confidence=confidence)

        view_rows = [norm_p(p) for p in picks]
        picks_made = len(view_rows)

    return render_template(
        "admin_view_user_picks.html",
        user=user,
        week=week,
        total_games=total_games,
        picks_made=picks_made,
        rows=view_rows,
    )

@admin_bp.route('/update_group_admin_status/<int:user_id>', methods=['POST'])
@login_required
def update_group_admin_status(user_id):
    from ..services.permissions import can_manage_group, is_global_admin

    active_group_id = session.get("active_group_id")
    if not active_group_id:
        flash("No active group selected.", "warning")
        return redirect(url_for("main.user_dashboard"))

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to manage this group.", "danger")
        return redirect(url_for("main.user_dashboard"))

    membership = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=active_group_id,
        is_active=True,
    ).first()

    if not membership:
        flash("Group membership not found.", "danger")
        return redirect(url_for("admin.manage_users"))

    vals = [v.strip().lower() for v in request.form.getlist('is_group_admin')]
    new_is_group_admin = any(v in ('1', 'true', 'on', 'yes') for v in vals)

    current_role = (membership.role or "").strip().lower()
    new_role = "group_admin" if new_is_group_admin else "member"

    # Prevent removing the last group admin
    if current_role == "group_admin" and new_role != "group_admin":
        active_admin_count = GroupMember.query.filter_by(
            group_id=active_group_id,
            is_active=True,
            role="group_admin",
        ).count()

        if active_admin_count <= 1:
            flash("Each group must have at least one group admin.", "warning")
            return redirect(url_for("admin.manage_users"))

    # Prevent group admin from removing their own group-admin access
    # unless they are also a global admin
    if (
        membership.user_id == current_user.id
        and current_role == "group_admin"
        and new_role != "group_admin"
        and not is_global_admin(current_user)
    ):
        flash("You cannot remove your own group admin access.", "warning")
        return redirect(url_for("admin.manage_users"))

    membership.role = new_role
    db.session.commit()

    flash("Group admin status updated.", "success")
    return redirect(url_for("admin.manage_users"))

@admin_bp.route('/remove_user_from_group/<int:user_id>', methods=['POST'])
@login_required
def remove_user_from_group(user_id):
    from ..services.permissions import can_manage_group, is_global_admin

    active_group_id = session.get("active_group_id")
    if not active_group_id:
        flash("No active group selected.", "warning")
        return redirect(url_for("main.user_dashboard"))

    if not can_manage_group(current_user, active_group_id):
        flash("You do not have permission to manage this group.", "danger")
        return redirect(url_for("main.user_dashboard"))

    membership = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=active_group_id,
        is_active=True,
    ).first()

    if not membership:
        flash("User is not an active member of this group.", "danger")
        return redirect(url_for("admin.manage_users"))

    role = (membership.role or "").strip().lower()

    # Prevent removing the last group admin
    if role == "group_admin":
        active_admin_count = GroupMember.query.filter_by(
            group_id=active_group_id,
            is_active=True,
            role="group_admin",
        ).count()

        if active_admin_count <= 1:
            flash("You cannot remove the last group admin from the group.", "warning")
            return redirect(url_for("admin.manage_users"))

    # Prevent group admin from removing themselves unless global admin
    if membership.user_id == current_user.id and not is_global_admin(current_user):
        flash("You cannot remove yourself from the active group.", "warning")
        return redirect(url_for("admin.manage_users"))

    membership.is_active = False
    db.session.commit()

    flash("User removed from the active group.", "success")
    return redirect(url_for("admin.manage_users"))

@admin_bp.route('/set_tiebreaker', methods=['GET', 'POST'])
@login_required
def set_tiebreaker():
    """Let admin mark a single game as the season tiebreaker."""
    from Football_Project.services.permissions import is_global_admin
    if not is_global_admin(current_user):
        flash("Access denied.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    settings = Settings.query.first()
    if not settings:
        flash("Settings not configured.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == 'POST':
        game_id = request.form.get('game_id', type=int)

        # Clear any existing tiebreaker for this season
        Game.query.filter_by(
            season_year=settings.season_year,
            season_type=settings.season_type,
            is_tiebreaker=True,
        ).update({"is_tiebreaker": False})

        if game_id:
            game = Game.query.get(game_id)
            if game:
                game.is_tiebreaker = True
                db.session.commit()
                flash(f"Tiebreaker set to {game.away_team} @ {game.home_team} (Week {game.week}).", "success")
            else:
                flash("Game not found.", "danger")
        else:
            db.session.commit()
            flash("Tiebreaker cleared.", "success")

        return redirect(url_for("admin.set_tiebreaker"))

    # GET - show all games for current season, grouped by week
    games = (
        Game.query
        .filter_by(
            season_year=settings.season_year,
            season_type=settings.season_type,
        )
        .order_by(Game.week.desc(), Game.commence_time_mt.desc())
        .all()
    )

    current_tiebreaker = next((g for g in games if g.is_tiebreaker), None)

    return render_template(
        'set_tiebreaker.html',
        games=games,
        current_tiebreaker=current_tiebreaker,
        settings=settings,
    )