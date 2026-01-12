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
from Football_Project.get_the_odds import get_nfl_spreads, save_spreads_to_db, get_current_week, save_to_csv
from football_scores import get_football_scores, save_scores_to_csv  # NOTE: don't import save_scores_to_db here
from Football_Project.models import db, Game, Settings, User, UserScore, Pick, JobRun, Announcement
from Football_Project.utils import calculate_user_scores, save_game_scores_to_db  # keep the utils version
from werkzeug.security import generate_password_hash
from Football_Project.services.sms_helpers import sms_week_reminder_job
from Football_Project.services.season import get_current_season_context, get_current_week
from Football_Project.services.schedule_service import update_schedule



#--------------------------
# Admin Announcements
#--------------------------

@admin_bp.route("/board", methods=["GET"])
@login_required
def admin_board():
    # placeholder for later moderation UI
    return render_template("admin_board.html")


@admin_bp.route("/announcements", methods=["GET"])
@login_required
def admin_announcements():
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
    if not current_user.is_admin:
        flash("Not authorized.", "danger")
        return redirect(url_for("admin.manage_users"))

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
    if not current_user.is_admin:
        flash("Not authorized.", "danger")
        return redirect(url_for("admin.manage_users"))

    session.pop("view_as_user_id", None)
    session.modified = True

    flash("View-as user disabled.", "info")
    return redirect(url_for("admin.manage_users"))

@admin_bp.route("/force_exit_view_as", methods=["GET"])
@login_required
def force_exit_view_as():
    if not current_user.is_admin:
        return "Not authorized", 403

    session.pop("view_as_user_id", None)
    session.pop("admin_view_as_user_id", None)
    session.modified = True
    return "OK: view-as cleared"

@admin_bp.route("/debug_session", methods=["GET"])
@login_required
def debug_session():
    if not current_user.is_admin:
        return "Not authorized", 403
    return f"session={dict(session)}"



@admin_bp.route("/test_sms/<int:week>")
def test_sms_week(week):
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
    # This runs for every admin blueprint request.
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if not current_user.is_admin:
        flash("Admins only.", "danger")
        return redirect(url_for('main.index'))

# -------------------------
# User management
# -------------------------

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    users = User.query.order_by(User.username).all()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
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
    user = User.query.get_or_404(user_id)

    # handle multiple values from hidden + checkbox
    vals = [v.strip().lower() for v in request.form.getlist('is_admin')]
    new_is_admin = any(v in ('1', 'true', 'on', 'yes') for v in vals)

    # prevent demoting self and ensure at least one admin
    if user.id == current_user.id and not new_is_admin:
        flash("You can’t remove your own admin rights.", "warning")
        return redirect(url_for('admin.manage_users'))
    if not new_is_admin and User.query.filter_by(is_admin=True).count() <= 1:
        flash("At least one admin is required.", "warning")
        return redirect(url_for('admin.manage_users'))

    user.is_admin = new_is_admin
    db.session.commit()
    flash("Admin status updated.", "success")
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You can’t delete your own account.", "warning")
        return redirect(url_for('admin.manage_users'))
    if user.is_admin and User.query.filter_by(is_admin=True).count() <= 1:
        flash("You can’t delete the last admin.", "warning")
        return redirect(url_for('admin.manage_users'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
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
    print("ADMIN_DASH session keys:", dict(session))  # TEMP DEBUG

    if in_view_as_mode():
        return redirect(url_for("main.user_dashboard"))

    settings = Settings.query.first()

    # Fallbacks if settings row somehow missing (shouldn't happen now)
    season_year = settings.season_year if settings else datetime.utcnow().year
    default_season_type = _settings_to_espn_seasontype(settings)

    # Your settings season_type appears to be 'REG'/'POST'/'PRE' (string)
    season_type = (settings.season_type if settings else "REG")

    # Use settings.current_week if present; else your existing logic
    current_week = settings.current_week if settings else get_current_week()

    last_odds_fetch = _last_odds_fetch_for_week(current_week)

    last_schedule_sync = (
        JobRun.query
        .filter_by(job_name="schedule_update")
        .order_by(JobRun.ran_at.desc())
        .first()
    )

    weeks = list(range(1, current_week + 1))
    users = User.query.order_by(User.username).all()

    # ⚠️ NOTE: these two helpers probably need season filters too.
    # We'll fix them next if they are also pulling old seasons.
    total_games = (
        db.session.query(func.count(Game.id))
        .filter(
            Game.week == current_week,
            Game.season_year == season_year,
            Game.season_type == season_type,
        )
        .scalar() or 0
    )
    counts = _missing_counts_for_week(current_week)

    # ✅ Status cards (time-based lock) — FIXED: filter by season_year + season_type
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

    # ✅ Remaining should be based on total_games for THIS season/week too
    remaining = max(0, (total_games or 0) - locked_games)

    # Optional: last grading timestamp
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
    try:
        week_option = request.form.get('week_option')
        week = int(request.form.get('week_number')) if week_option == 'override' else get_current_week()

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

        # default: render odds preview
        return render_template('display_odds.html', games_list=games_list, week=week)

    except Exception as e:
        flash(f"An error occurred while fetching the odds: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/save_odds', methods=['POST'])
@login_required
def save_odds():
    try:
        action = request.form.get('action')
        form_week = request.form.get('week')
        week = int(form_week) if form_week else get_current_week()
        games_list, _ = get_nfl_spreads()

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
        flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/display_odds')
@login_required
def display_odds():
    settings = Settings.query.first()
    current_week = settings.current_week if settings else get_current_week()
    games = Game.query.filter_by(week=current_week).all()
    return render_template('display_odds.html', games_list=games, week=current_week)

# -------------------------
# Scores (fetch / admin)
# -------------------------

@admin_bp.route('/fetch_scores', methods=['POST'])
@login_required
def fetch_scores():
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
    selected_week = request.args.get("week", "all")
    selected_user = request.args.get("user", "all")

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

    all_users = User.query.order_by(User.username).all()

    # -------------------------------------------------------
    # ✅ Games: always filter to current season + optional week
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
    # -------------------------------------------------------
    picks_q = (
        db.session.query(Pick)
        .join(Game, Game.id == Pick.game_id)
        .join(User, User.id == Pick.user_id)
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type_label
        )
    )

    if selected_week != "all":
        picks_q = picks_q.filter(Pick.week == selected_week)

    if selected_user != "all":
        picks_q = picks_q.filter(Pick.user_id == selected_user)

    picks = picks_q.all()

    # -------------------------------------------------------
    # ✅ Totals: computed from picks, season-filtered via Game
    # -------------------------------------------------------
    user_totals = {u.username: 0 for u in all_users}

    totals_q = (
        db.session.query(User.username, func.coalesce(func.sum(Pick.points_earned), 0))
        .join(Pick, Pick.user_id == User.id)
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type_label
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
    # -------------------------------------------------------
    weeks = [
        w for (w,) in (
            db.session.query(Game.week)
            .filter(Game.season_year == season_year, Game.season_type == season_type_label)
            .distinct()
            .order_by(Game.week)
            .all()
        )
        if w is not None
    ]

    # -------------------------------------------------------
    # ✅ locked/total stats: season-filtered
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
        season_year=season_year,               # optional (for header)
        season_type=season_type_label,         # optional (for header)
    )

@admin_bp.route("/admin_calculate_scores", methods=["POST"])
@login_required
def admin_calculate_scores():
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
    user_id = request.form.get('user_id', type=int)
    week = request.form.get('week', type=int)
    game_id = request.form.get('game_id', type=int)
    new_score = request.form.get('new_score')

    try:
        new_score = float(new_score)
    except (TypeError, ValueError):
        flash("Invalid score value.", "danger")
        return redirect(url_for('admin.admin_scores', week=week))

    pick = Pick.query.filter_by(user_id=user_id, game_id=game_id, week=week).first()
    if not pick:
        flash("Pick not found.", "danger")
        return redirect(url_for('admin.admin_scores', week=week))

    pick.points_earned = new_score
    pick.is_overridden = True
    db.session.add(pick)
    db.session.commit()

    # Recompute totals for that week
    user_scores = calculate_user_scores(week=week)
    row = UserScore.query.filter_by(user_id=user_id, week=week).first()
    if row:
        row.score = user_scores.get(user_id, row.score)
    else:
        db.session.add(UserScore(user_id=user_id, week=week, score=user_scores.get(user_id, 0),
                                 calculated_at=datetime.utcnow()))
    db.session.commit()

    flash("Score successfully overridden and totals updated.", "success")
    return redirect(url_for('admin.admin_scores', week=week))

@admin_bp.route('/process_user_scores', methods=['POST'])
@login_required
def process_user_scores():
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





def _missing_counts_for_week(week: int) -> dict:
    """
    Missing picks = for UNLOCKED games (kickoff in future or unknown),
    count per user how many valid picks are missing (no row OR confidence is NULL).
    Returns a dict with 'rows' for UI use.
    """
    now_mt = datetime.now(ZoneInfo("US/Mountain"))

    total_games = (
        db.session.query(func.count(Game.id))
        .filter(Game.week == week)
        .scalar()
        or 0
    )

    # Unlocked = kickoff in the future (or unknown)
    unlocked_ids = [
        gid
        for (gid,) in db.session.query(Game.id)
        .filter(
            Game.week == week,
            or_(Game.commence_time_mt.is_(None), Game.commence_time_mt > now_mt),
        )
        .all()
    ]
    unlocked_count = len(unlocked_ids)

    # All users
    users = db.session.query(User.id, User.username).order_by(User.username).all()

    # Valid picks among unlocked games = confidence is not NULL
    valid_by_user = {}
    if unlocked_count:
        valid_rows = (
            db.session.query(Pick.user_id, func.count(Pick.id))
            .filter(
                Pick.week == week,
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
        # include both 'made' and 'picks_made' for template compatibility
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

    # Sort: most missing first, then username
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
    # Inputs (defaults)
    week = request.args.get('week', type=int) or get_current_week()
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
        # summary tiles
        zero_count=zero_count,
        any_count=any_count,
        complete_count=complete_count,
    )



@admin_bp.route('/user_picks/<int:user_id>', methods=['GET'], endpoint='view_user_picks')
@login_required
def view_user_picks(user_id: int):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('main.index'))

    week = request.args.get('week', type=int) or get_current_week()
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
                .filter(Pick.user_id == user_id, Pick.week == week)
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
                .filter(Pick.user_id == user_id, Pick.week == week)
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
                .filter(Pick.user_id == user_id, Pick.week == week)
                .order_by(Game.commence_time_mt.asc())
                .all()
            )
            joined = True
    except Exception:
        joined = False

    if joined:
        def norm(p, g):
            pick_team = getattr(p, 'team_picked', None)
            # Confidence field fallback chain
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
        # Fallback: show picks even if we can't match a Game row
        picks = (
            Pick.query.filter_by(user_id=user_id, week=week)
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

