# Football_Project/admin/routes.py
from flask import render_template, request, redirect, url_for, flash, send_file, current_app, abort, Blueprint
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
from Football_Project.models import db, Game, Settings, User, UserScore, Pick
from Football_Project.utils import calculate_user_scores, save_game_scores_to_db  # keep the utils version
from werkzeug.security import generate_password_hash
from Football_Project.services.sms_helpers import sms_week_reminder_job

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

@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    current_year = datetime.utcnow().year
    default_season_type = 2  # regular season default
    current_week = get_current_week()                      # ← define first
    last_odds_fetch = _last_odds_fetch_for_week(current_week)  # ← now safe

    weeks = list(range(1, current_week + 1))
    users = User.query.order_by(User.username).all()
    total_games = _total_games_for_week(current_week)
    counts = _missing_counts_for_week(current_week)

    # Status cards (time-based lock)
    now_mt = datetime.now(ZoneInfo("US/Mountain"))
    locked_games = (
        db.session.query(func.count(Game.id))
        .filter(Game.week == current_week, Game.commence_time_mt <= now_mt)
        .scalar() or 0
    )
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
        current_year=current_year,
        default_season_type=default_season_type,
        weeks=weeks,
        users=users,
        current_week=current_week,
        week=current_week,
        counts=counts,
        stats=stats,
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
    year = request.form.get('year')
    seasontype = request.form.get('seasontype')
    weeknum = request.form.get('weeknum')
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

    # ---- games (respect week filter)
    games_q = Game.query
    if selected_week != "all":
        games_q = games_q.filter_by(week=selected_week)
    games = games_q.order_by(Game.week.asc(), Game.id.asc()).all()

    # ---- picks (respect week + user filter)
    picks_q = db.session.query(Pick).join(User, User.id == Pick.user_id)
    if selected_week != "all":
        picks_q = picks_q.filter(Pick.week == selected_week)
    if selected_user != "all":
        picks_q = picks_q.filter(Pick.user_id == selected_user)
    picks = picks_q.all()

    # ---- totals from picks (since scoring is automated)
    user_totals = {u.username: 0 for u in all_users}
    totals_q = db.session.query(User.username, func.coalesce(func.sum(Pick.points_earned), 0)) \
                         .join(User, User.id == Pick.user_id)
    if selected_week != "all":
        totals_q = totals_q.filter(Pick.week == selected_week)
    if selected_user != "all":
        totals_q = totals_q.filter(Pick.user_id == selected_user)
    totals_q = totals_q.group_by(User.username).all()
    for uname, total in totals_q:
        user_totals[uname] = int(total or 0)

    # ---- index picks by game for fast build
    picks_by_game: dict[int, list[Pick]] = defaultdict(list)
    for p in picks:
        picks_by_game[p.game_id].append(p)

    # ---- build rows
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
                "team_picked": p.team_picked,          # ← NEW (what you asked for)
                "confidence": p.confidence,
                "points_earned": p.points_earned,
                "is_correct": is_correct,               # ← handy for coloring
            })
        game_picks.append(grp)

    # ---- week list for dropdown
    weeks = [w for (w,) in db.session.query(Game.week).distinct().order_by(Game.week).all()]

    # ---- optional: locked/total stats for this week
    locked_count = total_games = None
    if selected_week != "all":
        now_mt = datetime.now(ZoneInfo("US/Mountain"))
        locked_count = db.session.query(func.count(Game.id)) \
            .filter(Game.week == selected_week, Game.commence_time_mt <= now_mt).scalar() or 0
        total_games = db.session.query(func.count(Game.id)) \
            .filter(Game.week == selected_week).scalar() or 0

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
    )

@admin_bp.route('/admin_calculate_scores', methods=['POST'])
@login_required
def admin_calculate_scores():
    """Recalculate user totals and upsert into UserScore."""
    selected_week = request.form.get('week', 'all')

    try:
        if selected_week == 'all':
            max_week = get_current_week()
            weeks = range(1, max_week + 1)
        else:
            selected_week = int(selected_week)
            weeks = [selected_week]
    except ValueError:
        flash("Invalid week selected.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    try:
        for w in weeks:
            # calculate_user_scores should return {user_id: total_points_for_week}
            user_scores = calculate_user_scores(week=w, write_final_only=True)
            if not isinstance(user_scores, dict):
                continue

            existing = UserScore.query.filter(UserScore.week == w,
                                              UserScore.user_id.in_(list(user_scores.keys()))).all()
            existing_map = {row.user_id: row for row in existing}

            for uid, total in user_scores.items():
                row = existing_map.get(uid)
                if row:
                    row.score = total
                else:
                    db.session.add(UserScore(user_id=uid, week=w, score=total, calculated_at=datetime.utcnow()))

        db.session.commit()
        flash("Scores calculated and saved.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error calculating scores: {str(e)}", "danger")

    return redirect(url_for('admin.admin_dashboard'))

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
    """Recompute user totals and upsert into UserScore.
       Defaults to all distinct weeks except the current week.
       If form has week != 'all', only processes that week.
    """
    try:
        current_week = get_current_week()

        # Default: all distinct weeks except the current week
        weeks = [w for (w,) in db.session.query(Game.week)
                               .distinct()
                               .order_by(Game.week)
                               .all()
                 if w != current_week]

        # Optional: limit to a specific week from the form
        form_week = request.form.get('week', 'all')
        if form_week != 'all':
            try:
                form_week = int(form_week)
            except ValueError:
                flash("Invalid week selected.", "danger")
                return redirect(url_for('admin.admin_dashboard'))
            weeks = [form_week]

        # Nothing to do?
        if not weeks:
            flash("No weeks to process.", "info")
            return redirect(url_for('admin.admin_dashboard'))

        # Recalculate and upsert
        for w in weeks:
            user_scores = calculate_user_scores(week=w)  # expected {user_id: total_points}
            if not isinstance(user_scores, dict):
                continue

            existing = UserScore.query.filter(
                UserScore.week == w,
                UserScore.user_id.in_(list(user_scores.keys()))
            ).all()
            existing_map = {row.user_id: row for row in existing}

            for uid, total in user_scores.items():
                row = existing_map.get(uid)
                if row:
                    row.score = total
                    row.calculated_at = datetime.utcnow()
                else:
                    db.session.add(UserScore(
                        user_id=uid,
                        week=w,
                        score=total,
                        calculated_at=datetime.utcnow()
                    ))

        db.session.commit()

        if len(weeks) == 1:
            flash(f"Successfully processed user scores for Week {weeks[0]}.", "success")
        else:
            flash(f"Successfully processed user scores for weeks {min(weeks)}–{max(weeks)}.", "success")

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

