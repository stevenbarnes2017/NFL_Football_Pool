# Football_Project/admin/routes.py
from flask import render_template, request, redirect, url_for, flash, send_file, current_app, abort, Blueprint
from flask_login import login_required, current_user
from datetime import datetime
import os
from sqlalchemy import func, literal
from . import admin_bp
# Data / services
from Football_Project.get_the_odds import get_nfl_spreads, save_spreads_to_db, get_current_week, save_to_csv
from football_scores import get_football_scores, save_scores_to_csv  # NOTE: don't import save_scores_to_db here
from Football_Project.models import db, Game, Settings, User, UserScore, Pick
from Football_Project.utils import calculate_user_scores, save_game_scores_to_db  # keep the utils version
from werkzeug.security import generate_password_hash

# -------------------------
# Guards
# -------------------------

@admin_bp.before_request
def admin_guard():
    # This runs for every admin blueprint request.
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
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

@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    current_year = datetime.utcnow().year
    default_season_type = 2  # regular season default
    current_week = get_current_week()
    weeks = list(range(1, current_week + 1))
    users = User.query.order_by(User.username).all()

    # Missing picks counts for banner/cards
    total_games = _total_games_for_week(current_week)
    counts = _missing_counts_for_week(current_week, total_games)

    return render_template(
        'admin_dashboard.html',
        current_year=current_year,
        default_season_type=default_season_type,
        weeks=weeks,
        users=users,
        current_week=current_week,  # needed for template links
        week=current_week,          # also pass as 'week' for consistency
        counts=counts               # needed for missing picks display
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
    selected_week = request.args.get('week', 'all')
    selected_user = request.args.get('user', 'all')

    # sanitize inputs
    try:
        if selected_week != 'all':
            selected_week = int(selected_week)
    except ValueError:
        flash("Invalid week selected.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    try:
        if selected_user != 'all':
            selected_user = int(selected_user)
    except ValueError:
        flash("Invalid user selected.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    all_users = User.query.order_by(User.username).all()
    user_totals = {user.username: 0 for user in all_users}

    if selected_week == 'all':
        totals = db.session.query(UserScore.user_id, db.func.sum(UserScore.score).label('total_score')) \
                           .group_by(UserScore.user_id).all()
        for user_id, total in totals:
            uname = User.query.get(user_id).username
            user_totals[uname] = total or 0
        games = Game.query.order_by(Game.week).all()
    else:
        scores = UserScore.query.filter_by(week=selected_week).all()
        for row in scores:
            uname = User.query.get(row.user_id).username
            user_totals[uname] = row.score
        games = Game.query.filter_by(week=selected_week).all()

    if selected_week == 'all' and selected_user == 'all':
        picks = Pick.query.all()
    elif selected_week == 'all':
        picks = Pick.query.filter_by(user_id=selected_user).all()
    elif selected_user == 'all':
        picks = Pick.query.filter_by(week=selected_week).all()
    else:
        picks = Pick.query.filter_by(week=selected_week, user_id=selected_user).all()

    game_picks = []
    for game in games:
        g = {
            'game_id': game.id,
            'home_team': game.home_team,
            'away_team': game.away_team,
            'spread': game.spread,
            'favorite_team': game.favorite_team,
            'home_team_score': game.home_team_score,
            'away_team_score': game.away_team_score,
            'status': game.status,
            'picks': []
        }
        for pick in picks:
            if pick.game_id == game.id:
                g['picks'].append({
                    'username': pick.user.username,
                    'confidence': pick.confidence,
                    'points_earned': pick.points_earned,
                    'user_id': pick.user_id
                })
        game_picks.append(g)

    weeks = [w[0] for w in db.session.query(Game.week).distinct().order_by(Game.week).all()]

    return render_template(
        'admin_scores.html',
        game_picks=game_picks,
        user_totals=user_totals,
        selected_week=selected_week,
        weeks=weeks,
        selected_user=selected_user,
        users=all_users
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
            user_scores = calculate_user_scores(week=w)
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





@admin_bp.route('/missing_picks', methods=['GET'])
@login_required
def missing_picks():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('main.index'))

    # inputs
    week = request.args.get('week', type=int) or get_current_week()
    filter_mode = request.args.get('filter', default='any')  # none | any | complete | all

    total_games = _total_games_for_week(week)
    pick_agg = _user_pick_aggregate_for_week(week)

    # Build expressions once
    picks_made = func.coalesce(pick_agg.c.picks_made, 0)
    remaining_expr = (literal(total_games) - picks_made)

    # Outer-join users to the pick aggregates so every user shows
    base_q = (
        db.session.query(
            User.id.label("user_id"),
            User.username.label("username"),
            picks_made.label("picks_made"),
            remaining_expr.label("remaining"),
            pick_agg.c.last_pick_time.label("last_pick_time"),
        )
        .outerjoin(pick_agg, pick_agg.c.user_id == User.id)
    )

    # Apply filter mode using WHERE (SQLite doesn't allow HAVING here)
    if filter_mode == 'none':
        # users with 0 picks
        base_q = base_q.filter(picks_made == 0)
    elif filter_mode == 'any':
        # users who still have remaining picks (partial or zero)
        base_q = base_q.filter(remaining_expr > 0)
    elif filter_mode == 'complete':
        # users fully done
        base_q = base_q.filter(remaining_expr == 0)
    # 'all' = no extra filter

    # Correct ordering: remaining desc, then username
    base_q = base_q.order_by(remaining_expr.desc(), User.username.asc())

    rows = base_q.all()

    # Precompute counts for quick links and dashboard summary
    counts = _missing_counts_for_week(week, total_games)

    return render_template(
        "missing_picks.html",
        week=week,
        total_games=total_games,
        rows=rows,
        filter_mode=filter_mode,
        counts=counts,
    )


def _missing_counts_for_week(week: int, total_games: int):
    pick_agg = _user_pick_aggregate_for_week(week)

    # all users with 0 picks
    none_count = (
        db.session.query(func.count(User.id))
        .outerjoin(pick_agg, pick_agg.c.user_id == User.id)
        .filter(func.coalesce(pick_agg.c.picks_made, 0) == 0)
        .scalar()
        or 0
    )

    # users with some but not all picks (partial)
    partial_count = (
        db.session.query(func.count(User.id))
        .outerjoin(pick_agg, pick_agg.c.user_id == User.id)
        .filter(func.coalesce(pick_agg.c.picks_made, 0) > 0)
        .filter(func.coalesce(pick_agg.c.picks_made, 0) < total_games)
        .scalar()
        or 0
    )

    # users complete
    complete_count = (
        db.session.query(func.count(User.id))
        .outerjoin(pick_agg, pick_agg.c.user_id == User.id)
        .filter(func.coalesce(pick_agg.c.picks_made, 0) == total_games)
        .scalar()
        or 0
    )

    return {
        "none": none_count,
        "partial": partial_count,
        "complete": complete_count,
        "any": none_count + partial_count,
        "total_users": none_count + partial_count + complete_count,
    }

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

