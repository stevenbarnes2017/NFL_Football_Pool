import sys
import os

# Add the parent directory of the current file to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import requests
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, Response
from dateutil import parser
from flask_login import login_required, current_user, login_user, logout_user, login_manager, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from Football_Project.get_the_odds import get_nfl_spreads, save_to_csv
from Football_Project.utils import fetch_detailed_game_stats, group_games_by_day, get_saved_games, get_unpicked_games_for_week, live_scores_cache, lock_picks_for_commenced_games, get_highest_available_confidence, save_pick_to_db, convert_to_utc, fetch_live_scores, get_picks, send_picks_email, get_nfl_playoff_picture, map_bracket_data, get_odds_data, generate_token, verify_token, get_serializer, send_password_reset_email, resolve_selected_week
from .services.season import get_current_season_context, get_current_week
from sqlalchemy import func
from dateutil import parser
import time
import pytz
from threading import Thread
from flask import request, flash, redirect, url_for, render_template, session
from flask_login import current_user, login_required
from datetime import datetime
from pytz import timezone  # Add this
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from .extensions import db
from .models import Game, Pick, User, Settings, UserScore, Announcement, BoardThread, BoardPost, GroupMember, PoolGroup
#from flask_mail import Message  # if you use Flask-Mail
from .utils import generate_token, verify_token
from .services.leaderboard import get_season_leaderboard, get_weekly_leaderboard
from .services.auth_context import get_effective_user_id
from Football_Project.services.season import get_current_season_context
<<<<<<< HEAD
from .services.group_service import get_active_group_id
=======
from Football_Retry.Football_Project.services.group_service import get_active_group_id
from slugify import slugify

>>>>>>> 48d0bb5 (scoping users view throughout admin routes)


main_bp = Blueprint('main', __name__)


@main_bp.route('/playoff-picture')
def playoff_picture():
    standings = get_nfl_playoff_picture()
    return render_template('playoff_picture.html', standings=standings)

@main_bp.route('/')
def index():
    # If the user is authenticated, redirect them to the dashboard
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))  # Redirect to admin dashboard
        else:
            return redirect(url_for('main.dashboard'))  # Redirect to regular user dashboard
    else:
        # If the user is not authenticated, redirect to the login page
        return redirect(url_for('auth.login'))



@main_bp.route('/my_picks', methods=['GET', 'POST'])
@login_required
def my_picks():
    from Football_Project.services.group_service import get_active_group_id

    settings = Settings.query.first()
    season_year = settings.season_year
    season_type = settings.season_type
    current_week = settings.current_week

    group_id = get_active_group_id()

    weeks = [
        wk for (wk,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type,
            )
            .distinct()
            .order_by(Game.week.asc())
            .all()
        )
    ]

    if request.method == 'POST':
        selected_week = request.form.get('week', type=int) or current_week
    else:
        selected_week = request.args.get('week', type=int) or current_week

    if weeks and selected_week not in weeks:
        selected_week = weeks[0]

    user_picks = (
        Pick.query
        .join(Game, Pick.game_id == Game.id)
        .filter(
            Pick.user_id == current_user.id,
            Pick.group_id == group_id,
            Pick.week == selected_week,
            Game.season_year == season_year,
            Game.season_type == season_type,
        )
        .order_by(Pick.confidence.desc().nullslast())
        .all()
    )

    return render_template(
        'my_picks.html',
        picks=user_picks,
        weeks=weeks,
        selected_week=selected_week,
        season_year=season_year,
        season_type=season_type,
    )

@main_bp.route("/register")
def legacy_register():
    return redirect(url_for("auth.register"))

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        favorite_team = request.form.get('favorite_team', '').strip()
        new_password = request.form.get('new_password', '')
        current_password = request.form.get('current_password', '')

        # Check if username/email already exists
        if username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash('Username already taken.', 'danger')
                return redirect(url_for('main.edit_profile'))

        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already taken.', 'danger')
                return redirect(url_for('main.edit_profile'))

        try:
            # Update password if provided
            if new_password:
                if not current_password:
                    flash('Current password required to change password.', 'danger')
                    return redirect(url_for('main.edit_profile'))
                
                if not check_password_hash(current_user.password, current_password):
                    flash('Current password is incorrect.', 'danger')
                    return redirect(url_for('main.edit_profile'))
                
                current_user.password = generate_password_hash(new_password)

            # Update user fields
            current_user.username = username
            current_user.email = email
            current_user.full_name = full_name
            current_user.phone = phone
            current_user.favorite_team = favorite_team

            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('main.profile'))

        except Exception as e:
            db.session.rollback()
            flash('Error updating profile.', 'danger')
            return redirect(url_for('main.edit_profile'))

    return render_template('edit_profile.html', user=current_user)

@main_bp.route("/profile/sms", methods=["POST"])
@login_required
def update_sms_settings():
    from . import db
    from flask import current_app
    import re

    raw_phone = (request.form.get("phone") or "").strip()
    wants_sms = bool(request.form.get("sms_opt_in"))

    current_app.logger.info(f"[SMS] POST /profile/sms raw_phone={raw_phone!r} wants_sms={wants_sms}")

    # Keep current phone unless user changed it
    phone = current_user.phone

    # Normalize/validate to E.164. Accept 10-digit US or +E.164
    if raw_phone != "":
        try:
            import phonenumbers
            digits = re.sub(r"\D", "", raw_phone)
            if len(digits) == 10:
                num = phonenumbers.parse(digits, "US")
            else:
                num = phonenumbers.parse(raw_phone, None)

            if not phonenumbers.is_valid_number(num):
                raise ValueError("invalid")

            phone = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            current_app.logger.warning(f"[SMS] phone validation failed: {e}")
            flash("Please enter a valid mobile number (e.g., 720-555-1234 or +17205551234).", "danger")
            return redirect(url_for("main.profile"))
    else:
        # Explicitly cleared the field
        phone = None

    current_user.phone = phone

    # Only enable if BOTH: checkbox ticked AND phone present
    new_opt_in = bool(phone) and wants_sms
    current_app.logger.info(f"[SMS] normalized_phone={phone!r} new_opt_in={new_opt_in}")

    # If column doesn't exist, this would raise—so wrap/flash
    try:
        # Optional timestamp if you added the column:
        try:
            if new_opt_in and not current_user.sms_opt_in:
                from datetime import datetime
                current_user.sms_opt_in_at = datetime.utcnow()
        except Exception as e:
            current_app.logger.info(f"[SMS] sms_opt_in_at not present (ok): {e}")

        current_user.sms_opt_in = new_opt_in
        db.session.commit()
        current_app.logger.info("[SMS] settings saved OK")
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"[SMS] DB commit failed: {e}")
        flash("Could not save your SMS settings. Please try again.", "danger")
        return redirect(url_for("main.profile"))

    flash("SMS reminders " + ("enabled." if current_user.sms_opt_in else "disabled."),
          "success" if current_user.sms_opt_in else "info")
    return redirect(url_for("main.profile"))




@main_bp.route("/login")
def legacy_login():
    return redirect(url_for("auth.login"))

@main_bp.route("/logout")
def legacy_logout():
    return redirect(url_for("auth.logout"))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # If admin is NOT viewing as a user, go to admin dashboard
    if current_user.is_admin and not session.get("admin_view_as_user_id"):
        return redirect(url_for('admin.admin_dashboard'))

    # Otherwise, render user dashboard (normal user OR admin view-as)
    return render_template(
        'user_dashboard.html',
        name=current_user.username,
        now=datetime.now()
    )
    

@main_bp.route('/download')
def download_spreads():
    games_list, _ = get_nfl_spreads()
    if games_list:
        filename = 'nfl_spreads.csv'
        save_to_csv(games_list, filename)

        return send_file(
            filename,
            mimetype='csv',
            download_name=filename,
            as_attachment=True
        )
    else:
        return "No data available for download.", 404


@main_bp.route('/email_picks', methods=['POST'])
@login_required
def email_picks():
    from flask import current_app, request

    user_id = current_user.id
    recipient = request.form.get('recipient_email', current_user.email)

    # ← this reads week from the form (week/selected_week/week_number)
    selected_week = resolve_selected_week(get_current_week)

    # Query picks for THAT week
    user_picks = (Pick.query
                  .filter(Pick.user_id == user_id, Pick.week == int(selected_week))
                  .order_by(Pick.confidence.desc())
                  .all())

    # Helpful log to verify what's coming in
    current_app.logger.info(
        "email_picks: user=%s week_param=%s resolved_week=%s picks=%d form=%s",
        current_user.username,
        request.form.get('week'),
        selected_week,
        len(user_picks),
        dict(request.form)
    )

    if not user_picks:
        flash(f"No picks found for Week {selected_week}.", "warning")
        return redirect(url_for('main.see_picks'))

    # Build the dict your email helper expects
    user_picks_dict = {}
    for pick in user_picks:
        label = f"Game {pick.game_id}"
        user_picks_dict[label] = {
            'team_picked': pick.team_picked,
            'confidence': pick.confidence
        }

    try:
        send_picks_email(recipient, user_picks_dict)  # keeps your signature
        flash(f"Emailed picks for Week {selected_week} to {recipient}.", "success")
        return redirect(url_for('main.user_dashboard'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/submit_picks', methods=['POST'])
@login_required
def submit_picks():
    from datetime import datetime
    import pytz
    from flask import session
    from Football_Project.services.group_service import get_active_group_id

    utc = pytz.utc
    now_utc = datetime.now(utc)

    settings = Settings.query.first()
    season_year = settings.season_year
    season_type = settings.season_type

    # Active group should come from the same source as nfl_picks
    group_id = get_active_group_id()
    if not group_id:
        flash("No active group selected.", "danger")
        return redirect(url_for("main.nfl_picks"))

    # Optional fallback if you still want to compare against posted value
    posted_group_id = request.form.get("group_id", type=int)
    if posted_group_id and posted_group_id != group_id:
        flash("Group mismatch detected.", "danger")
        return redirect(url_for("main.nfl_picks"))

    # View-as support
    view_as_id = session.get("view_as_user_id") or session.get("admin_view_as_user_id")
    effective_user_id = current_user.id
    if view_as_id and getattr(current_user, "is_admin", False):
        try:
            effective_user_id = int(view_as_id)
        except (TypeError, ValueError):
            effective_user_id = current_user.id

    try:
        week = int(request.form.get("week", "0"))
    except (TypeError, ValueError):
        flash("Invalid week.", "danger")
        return redirect(url_for("main.nfl_picks"))

    membership = GroupMember.query.filter_by(
        user_id=effective_user_id,
        group_id=group_id,
        is_active=True,
    ).first()

    if not membership:
        flash("You are not a member of that group.", "danger")
        return redirect(url_for("main.nfl_picks", week=week))

    games = (
        Game.query
        .filter(
            Game.week == week,
            Game.season_year == season_year,
            Game.season_type == season_type,
        )
        .all()
    )

    created = updated = locked = skipped = 0

    for game in games:
        nat_id = game.game_id

        pick_key = f"pick_{nat_id}"
        conf_key = f"confidence_{nat_id}"

        team_picked = (request.form.get(pick_key) or "").strip()
        conf_raw = (request.form.get(conf_key) or "").strip()

        if team_picked == "" and conf_raw == "":
            continue

        if game.commence_time_mt and now_utc >= game.commence_time_mt.astimezone(utc):
            locked += 1
            continue

        if team_picked and team_picked not in {game.home_team, game.away_team}:
            flash(f"Invalid team selection for game {nat_id}.", "warning")
            skipped += 1
            continue

        conf_val = None
        conf_set_to_null = False

        if conf_raw == "":
            conf_set_to_null = True
        else:
            try:
                conf_val = int(conf_raw)
            except ValueError:
                flash(f"Confidence for {nat_id} must be a number.", "warning")
                skipped += 1
                continue

        existing = Pick.query.filter_by(
            user_id=effective_user_id,
            game_id=game.id,
            group_id=group_id,
        ).first()

        if existing:
            changed = False

            if team_picked and existing.team_picked != team_picked:
                existing.team_picked = team_picked
                changed = True

            if conf_set_to_null and existing.confidence is not None:
                existing.confidence = None
                changed = True
            elif conf_val is not None and existing.confidence != conf_val:
                existing.confidence = conf_val
                changed = True

            if changed:
                existing.week = game.week
                existing.pick_time = datetime.utcnow()
                updated += 1
            else:
                skipped += 1

        else:
            if not team_picked:
                skipped += 1
                continue

            db.session.add(Pick(
                user_id=effective_user_id,
                week=game.week,
                game_id=game.id,
                group_id=group_id,
                team_picked=team_picked,
                confidence=(None if conf_set_to_null else conf_val),
                pick_time=datetime.utcnow(),
            ))
            created += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving picks: {e}", "danger")
        return redirect(url_for("main.nfl_picks", week=week))

    flash(
        f"Saved for user {effective_user_id} — Created: {created}, Updated: {updated}, Locked: {locked}, Skipped: {skipped}",
        "success" if (created or updated) else "warning"
    )
    return redirect(url_for("main.nfl_picks", week=week))



@main_bp.route('/get_current_week')
def current_week():
    settings = Settings.query.first()

    if not settings:
        return jsonify({"error": "Settings not configured"}), 500

    week = get_current_week(
        season_year=settings.season_year,
        season_type=settings.season_type
    )

    return jsonify({
        "current_week": week,
        "season_year": settings.season_year,
        "season_type": settings.season_type
    })
  




@main_bp.route('/admin_set_week', methods=['GET', 'POST'])
@login_required
def admin_set_week():
    if not current_user.is_admin:
        flash('You must be an administrator to access this page.', 'danger')
        return redirect(url_for('index'))

    return render_template('admin_set_week.html', now=datetime.now())


@main_bp.route('/user_dashboard')
@login_required
def user_dashboard():
    group_id = get_active_group_id()
    lock_picks_for_commenced_games(current_user.id, group_id)
    settings = Settings.query.first()
    current_week = settings.current_week if settings else 1
    all_weeks = list(range(1, current_week ))  # List of all weeks up to the current week

    return render_template('user_dashboard.html', name=current_user.username, current_week=current_week, all_weeks=all_weeks, now=datetime.now())


@main_bp.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get the selected week from the form
        selected_week = request.form.get('week')
        if selected_week:
            try:
                selected_week = int(selected_week)
            except ValueError:
                flash("Invalid week selected.", "danger")
                return redirect(url_for('results'))
            # Query games for the selected week
            games = Game.query.filter_by(week=selected_week).order_by(Game.id).all()
        else:
            # If no week is selected, show all games
            games = Game.query.order_by(Game.week, Game.id).all()
    else:
        # For GET requests, display all games or set a default week
        games = Game.query.order_by(Game.week, Game.id).all()
    
    # Get a list of distinct weeks for the dropdown
    weeks = db.session.query(Game.week).distinct().order_by(Game.week).all()
    weeks = [week[0] for week in weeks]  # Extract week numbers from tuples
    
    return render_template('results.html', games=games, weeks=weeks)

@main_bp.route('/user_scores/<int:week>', methods=['GET'])
@login_required
def user_scores(week):
    from .models import Settings  # adjust import path if needed

    settings = Settings.query.first()
    if not settings:
        # If settings missing, just use the week from the URL
        pass

    # ✅ week comes from the URL; no get_current_week() call
    current_user_score_row = UserScore.query.filter_by(
        user_id=current_user.id,
        week=week
    ).first()
    current_user_score = current_user_score_row.score if current_user_score_row else 0

    all_scores = UserScore.query.filter_by(week=week).all()

    all_user_scores = {
        score.user_id: {
            "username": score.user.username,
            "score": score.score
        }
        for score in all_scores
    }

    return render_template(
        "user_scores.html",
        current_user_score=current_user_score,
        all_scores=all_user_scores,
        week=week
    )



@main_bp.route('/see_picks', methods=['GET', 'POST'])
@login_required
def see_picks():
    from flask import session

    # ✅ DB-driven season context (source of truth)
    settings = Settings.query.first()
    season_year = settings.season_year
    season_type = settings.season_type
    current_week = settings.current_week

    group_id = get_active_group_id()

    # ✅ View-as support: use effective_user_id for loading picks
    view_as_id = session.get("view_as_user_id") or session.get("admin_view_as_user_id")
    effective_user_id = current_user.id
    if view_as_id and getattr(current_user, "is_admin", False):
        try:
            effective_user_id = int(view_as_id)
        except (TypeError, ValueError):
            effective_user_id = current_user.id

    # ✅ Weeks available for THIS season/year/type (prevents Week 18 leakage)
    all_weeks = [
        wk for (wk,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type
            )
            .distinct()
            .order_by(Game.week.asc())
            .all()
        )
    ]

    # Week selection (POST from dropdown or default)
    if request.method == 'POST':
        selected_week = request.form.get('week', type=int) or current_week
    else:
        selected_week = request.args.get('week', type=int) or current_week

    # Safety: force selected_week to valid list
    if all_weeks and selected_week not in all_weeks:
        selected_week = all_weeks[0]

    # ✅ User picks for ONLY games in this season/week/type/group (view-as aware)
    user_picks = (
        Pick.query
        .join(Game, Pick.game_id == Game.id)
        .filter(
            Pick.user_id == effective_user_id,
            Pick.group_id == group_id,
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week == selected_week
        )
        .order_by(Pick.confidence.desc().nullslast())
        .all()
    )

    # ✅ Unpicked games should also be season filtered and group-aware
    unpicked_games = get_unpicked_games_for_week(
        user_picks=user_picks,
        week=selected_week,
        season_year=season_year,
        season_type=season_type,        
        
    )

    return render_template(
        'see_picks.html',
        selected_week=selected_week,
        all_weeks=all_weeks,
        user_picks=user_picks,
        unpicked_games=unpicked_games,
        season_year=season_year,
        season_type=season_type,
        effective_user_id=effective_user_id
    )


from flask import jsonify, request

@main_bp.route('/user_score_summary', methods=['GET'])
@login_required
def user_score_summary():
    from collections import defaultdict

    # Season context
    season_year, season_type = get_current_season_context()

    # View mode persistence (snapshot/details)
    view = request.args.get("view", "snapshot")

    # Week parsing
    selected_week = request.args.get('week', 'all')

    if selected_week == 'current':
        selected_week = (get_current_week(season_year, season_type) or 1) - 1

    try:
        if selected_week != 'all':
            selected_week = int(selected_week)
    except ValueError:
        flash("Invalid week selected.", "danger")
        return redirect(url_for('main.dashboard'))

    # Effective user (admin view-as aware)
    user_id = get_effective_user_id()

    # ==========================================================
    # Standings + totals (FIX: derive from Pick+Game, season-safe)
    # ==========================================================
    if selected_week == 'all':
        user_scores = (
            db.session.query(
                User.id,
                User.username,
                func.coalesce(func.sum(Pick.points_earned), 0).label('total_score')
            )
            .outerjoin(Pick, User.id == Pick.user_id)
            .outerjoin(Game, Game.id == Pick.game_id)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type
            )
            .group_by(User.id)
            .order_by(func.coalesce(func.sum(Pick.points_earned), 0).desc())
            .all()
        )

        user_total_score = (
            db.session.query(func.coalesce(func.sum(Pick.points_earned), 0))
            .join(Game, Game.id == Pick.game_id)
            .filter(
                Pick.user_id == user_id,
                Game.season_year == season_year,
                Game.season_type == season_type
            )
            .scalar() or 0
        )
    else:
        user_scores = (
            db.session.query(
                User.id,
                User.username,
                func.coalesce(func.sum(Pick.points_earned), 0).label('total_score')
            )
            .outerjoin(Pick, (User.id == Pick.user_id) & (Pick.week == selected_week))
            .outerjoin(Game, Game.id == Pick.game_id)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type,
                Game.week == selected_week
            )
            .group_by(User.id)
            .order_by(func.coalesce(func.sum(Pick.points_earned), 0).desc())
            .all()
        )

        user_total_score = (
            db.session.query(func.coalesce(func.sum(Pick.points_earned), 0))
            .join(Game, Game.id == Pick.game_id)
            .filter(
                Pick.user_id == user_id,
                Game.season_year == season_year,
                Game.season_type == season_type,
                Game.week == selected_week
            )
            .scalar() or 0
        )

    # ==========================================================
    # Games + Picks table (season-safe)
    # ==========================================================
    games = []
    user_picks = []
    game_picks = []

    if selected_week != 'all':
        games = (
            Game.query
            .filter(
                Game.week == selected_week,
                Game.season_year == season_year,
                Game.season_type == season_type
            )
            .all()
        )

        # Don't assume Pick has season fields; enforce via Game join
        user_picks = (
            db.session.query(Pick)
            .join(Game, Game.id == Pick.game_id)
            .filter(
                Pick.user_id == user_id,
                Pick.week == selected_week,
                Game.season_year == season_year,
                Game.season_type == season_type
            )
            .all()
        )

        pick_by_game = {p.game_id: p for p in user_picks}
        for g in games:
            p = pick_by_game.get(g.id)
            game_picks.append({
                'game_id': g.id,
                'home_team': g.home_team,
                'away_team': g.away_team,
                'spread': float(g.spread) if g.spread is not None else None,
                'favorite_team': g.favorite_team,
                'home_team_score': g.home_team_score,
                'away_team_score': g.away_team_score,
                'status': g.status,
                'pick': {
                    'team_picked': p.team_picked,
                    'confidence': p.confidence,
                    'points_earned': p.points_earned
                } if p else None
            })

    # ==========================================================
    # Weeks dropdown (season-safe)
    # ==========================================================
    weeks = [
        w[0] for w in (
            db.session.query(Game.week)
            .filter(Game.season_year == season_year, Game.season_type == season_type)
            .distinct()
            .order_by(Game.week)
            .all()
        )
    ]

    # ==========================================================
    # Season-wide stats (FIX: weekly totals from Pick+Game)
    # ==========================================================
    weekly_rows = (
        db.session.query(Game.week, func.coalesce(func.sum(Pick.points_earned), 0))
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Pick.user_id == user_id,
            Game.season_year == season_year,
            Game.season_type == season_type
        )
        .group_by(Game.week)
        .order_by(Game.week)
        .all()
    )
    weekly_points = [{'week': int(w), 'points': int(s or 0)} for (w, s) in weekly_rows]

    season_total = sum(r['points'] for r in weekly_points)
    week_count = len(weekly_points) if weekly_points else 0
    avg_points = round(season_total / week_count, 2) if week_count else 0.0
    best_week = max(weekly_points, key=lambda r: r['points']) if weekly_points else None
    worst_week = min(weekly_points, key=lambda r: r['points']) if weekly_points else None

    # Pick-level performance — FINAL only, season-safe
    final_picks = (
        db.session.query(Pick, Game)
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Pick.user_id == user_id,
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.status == 'STATUS_FINAL'
        )
        .all()
    )
    total_final = len(final_picks)
    wins = sum(1 for (p, g) in final_picks if (p.points_earned or 0) > 0)
    losses = sum(1 for (p, g) in final_picks if (p.points_earned or 0) == 0)
    win_rate = round((wins / total_final) * 100, 1) if total_final else 0.0

    def streak_at_or_above_avg(weekly_points_list, avg):
        if not weekly_points_list:
            return 0
        streak = 0
        for row in reversed(weekly_points_list):
            if row['points'] >= avg:
                streak += 1
            else:
                break
        return streak

    streak_weeks = streak_at_or_above_avg(weekly_points, avg_points)

    season_stats = {
        'season_total': int(season_total),
        'avg_points': avg_points,
        'best_week': {'week': best_week['week'], 'points': best_week['points']} if best_week else None,
        'worst_week': {'week': worst_week['week'], 'points': worst_week['points']} if worst_week else None,
        'win_rate': win_rate,
        'streak_at_or_above_avg': streak_weeks
    }

    # Confidence trends (FINAL only + season filtered)
    conf_wins = defaultdict(int)
    conf_attempts = defaultdict(int)

    final_conf_rows = (
        db.session.query(Pick.confidence, Pick.points_earned)
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Pick.user_id == user_id,
            Pick.confidence.isnot(None),
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.status == 'STATUS_FINAL'
        )
        .all()
    )

    for conf, pts in final_conf_rows:
        c = int(conf)
        conf_attempts[c] += 1
        if (pts or 0) > 0:
            conf_wins[c] += 1

    max_conf = max(conf_attempts.keys(), default=16)
    wins_by_confidence = [conf_wins.get(c, 0) for c in range(1, max_conf + 1)]
    attempts_by_confidence = [conf_attempts.get(c, 0) for c in range(1, max_conf + 1)]
    win_rate_by_confidence = [
        round((conf_wins.get(c, 0) / conf_attempts.get(c, 1)) * 100, 1) if conf_attempts.get(c) else 0
        for c in range(1, max_conf + 1)
    ]

    trend_data = {
        'wins_by_confidence': wins_by_confidence,
        'attempts_by_confidence': attempts_by_confidence,
        'win_rate_by_confidence': win_rate_by_confidence,
        'weekly_points': weekly_points
    }

    # Team bias (season filtered by joining Game)
    team_stats = defaultdict(lambda: {'picked_count': 0, 'wins': 0, 'losses': 0})
    team_rows = (
        db.session.query(Pick.team_picked, Pick.points_earned, Game.status)
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Pick.user_id == user_id,
            Game.season_year == season_year,
            Game.season_type == season_type
        )
        .all()
    )
    for team, pts, status in team_rows:
        if not team:
            continue
        st = team_stats[team]
        st['picked_count'] += 1
        if status == 'STATUS_FINAL':
            if (pts or 0) > 0:
                st['wins'] += 1
            elif (pts or 0) == 0:
                st['losses'] += 1

    team_bias_rows = []
    for team, st in team_stats.items():
        total = st['wins'] + st['losses']
        win_pct = round((st['wins'] / total) * 100, 1) if total > 0 else 0.0
        team_bias_rows.append({
            'team': team,
            'picked_count': st['picked_count'],
            'wins': st['wins'],
            'losses': st['losses'],
            'win_pct': win_pct
        })

    favorites_sorted = sorted(team_bias_rows, key=lambda r: r['picked_count'], reverse=True)[:5]
    best_teams_sorted = sorted(
        [r for r in team_bias_rows if r['picked_count'] >= 3],
        key=lambda r: r['win_pct'],
        reverse=True
    )[:5]

    team_bias = {
        'by_team': team_bias_rows,
        'favorites': favorites_sorted,
        'best_teams': best_teams_sorted
    }

    tips = []
    if favorites_sorted:
        f0 = favorites_sorted[0]
        tips.append(f"Most picked: {f0['team']} ({f0['picked_count']} picks, {f0['win_pct']}% win rate).")
    hi_conf = sum(wins_by_confidence[10:16])  # 11–16
    lo_conf = sum(wins_by_confidence[0:5])    # 1–5
    if hi_conf < lo_conf:
        tips.append("High confidence picks (11–16) have underperformed compared to your low confidence picks.")
    if len(weekly_points) >= 3:
        last3 = [wp['points'] for wp in weekly_points[-3:]]
        tips.append(f"Last 3 weeks: {last3[0]}, {last3[1]}, {last3[2]} points.")
    if win_rate >= 60:
        tips.append("Strong overall win rate — keep riding your strategy.")
    elif win_rate <= 40 and week_count >= 4:
        tips.append("Consider dialing back confidence on toss-up games — recent results suggest volatility.")

    coach_tips = tips[:3]

    # JSON response
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        return jsonify({
            'user_scores': [{'id': u.id, 'username': u.username, 'total_score': int(u.total_score or 0)} for u in user_scores],
            'game_picks': game_picks,
            'user_total_score': int(user_total_score or 0),
            'selected_week': selected_week,
            'weeks': weeks,
            'season_stats': season_stats,
            'trend_data': trend_data,
            'team_bias': team_bias,
            'coach_tips': coach_tips,
            'view': view,
            'effective_user_id': user_id,
        })

    # HTML render
    return render_template(
        'user_score_summary.html',
        user_scores=user_scores,
        game_picks=game_picks,
        user_total_score=user_total_score,
        selected_week=selected_week,
        weeks=weeks,
        season_stats=season_stats,
        trend_data=trend_data,
        team_bias=team_bias,
        coach_tips=coach_tips,
        view=view,
        season_year=season_year,
        season_type=season_type,
        effective_user_id=user_id,
    )




@main_bp.route('/game_details/<game_id>')
def game_details(game_id):
    # Fetch detailed stats for the specific game using its game ID
    detailed_data = fetch_detailed_game_stats(game_id)

    if not detailed_data:
        # Handle case where detailed data couldn't be fetched
        flash("Could not load game details. Please try again.", "warning")
        return redirect(url_for('main.live_scores_page'))

    # Render the template for detailed game stats
    return render_template('game_details.html', data=detailed_data)

mountain_tz = pytz.timezone('America/Denver')

def convert_utc_to_mountain(utc_time):
    """Convert UTC time (datetime or ISO string) to Mountain Time, or return None."""
    if utc_time is None:
        return None

    # If stored as string, parse it first
    if isinstance(utc_time, str):
        # Handle Zulu suffix by replacing 'Z' with UTC offset
        s = utc_time.strip().replace("Z", "+00:00")
        utc_time = datetime.fromisoformat(s)

    # If naive datetime, assume it's UTC
    if utc_time.tzinfo is None:
        from datetime import timezone
        utc_time = utc_time.replace(tzinfo=timezone.utc)

    return utc_time.astimezone(mountain_tz)


@main_bp.route('/nfl_picks', methods=['GET', 'POST'])
@login_required
def nfl_picks():
    from datetime import datetime
    import pytz
    from flask import request, render_template, session
    from flask_login import current_user
    from Football_Project.services.group_service import get_active_group_id

    utc = pytz.utc
    mt = pytz.timezone("America/Denver")
    now_utc = datetime.now(utc)

    # ✅ DB is source of truth
    settings = Settings.query.first()
    season_year = settings.season_year
    season_type = settings.season_type
    current_week = settings.current_week

    group_id = get_active_group_id()

    # ✅ View-as support
    view_as_id = session.get("view_as_user_id")
    effective_user_id = current_user.id
    if view_as_id and getattr(current_user, "is_admin", False):
        try:
            effective_user_id = int(view_as_id)
        except (TypeError, ValueError):
            effective_user_id = current_user.id

    # ✅ Only weeks that exist for THIS season_year + season_type
    all_weeks = [
        wk for (wk,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type
            )
            .distinct()
            .order_by(Game.week.asc())
            .all()
        )
    ]

    # Week selection (GET param or POST dropdown)
    selected_week = request.form.get('week', type=int) or request.args.get('week', type=int)
    if not selected_week:
        selected_week = current_week

    # Safety: prevent selecting a week that isn't in this season_type
    if all_weeks and selected_week not in all_weeks:
        selected_week = all_weeks[0]

    # ✅ Games for the week — filtered to season/year/type
    games = (
        Game.query
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week == selected_week
        )
        .order_by(Game.commence_time_mt)
        .all()
    )
    num_of_games = len(games)

    # ✅ Group games by Mountain weekday for display
    grouped_games = {}
    for g in games:
        dt_mt = g.commence_time_mt.astimezone(mt) if g.commence_time_mt else None
        day = dt_mt.strftime("%A") if dt_mt else "Unknown"
        grouped_games.setdefault(day, []).append(g)

    # DB PK ids for the week's games
    game_db_ids = [g.id for g in games]

    # ✅ Picks for ONLY these games, ONLY this week, ONLY this group, and the effective user
    rows = (
        db.session.query(Pick, Game)
        .join(Game, Pick.game_id == Game.id)
        .filter(
            Pick.user_id == effective_user_id,
            Pick.group_id == group_id,
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week == selected_week,
        )
        .all()
    )

    # ✅ Match the template: key by NATURAL game_id
    user_picks = {g.game_id: (p.team_picked, p.confidence) for p, g in rows}
    used_confidence_points = [p.confidence for p, _ in rows if p.confidence is not None]

    # ✅ locked_ids must also use NATURAL game_id for template compatibility
    locked_ids = set()
    for g in games:
        if g.commence_time_mt and now_utc >= g.commence_time_mt.astimezone(utc):
            locked_ids.add(g.game_id)

    # OPTIONAL auto-assign confidence for locked/no-pick (uses natural ids)
    total_conf_points = list(range(1, num_of_games + 1))

    def highest_available(all_pts, used_pts):
        avail = sorted(set(all_pts) - set(used_pts), reverse=True)
        return avail[0] if avail else None

    for g in games:
        if g.game_id in locked_ids and g.game_id not in user_picks:
            hi = highest_available(total_conf_points, used_confidence_points)
            if hi:
                user_picks[g.game_id] = ('No pick made', hi)
                used_confidence_points.append(hi)

    print("VIEW_AS:", session.get("view_as_user_id"), "CURRENT:", current_user.id, "EFFECTIVE:", effective_user_id, "USED:", used_confidence_points)

    return render_template(
        'nfl_picks.html',
        grouped_games=grouped_games,
        num_of_games=num_of_games,
        now_utc=now_utc,
        selected_week=selected_week,
        all_weeks=all_weeks,
        user_picks=user_picks,
        used_confidence_points=used_confidence_points,
        locked_ids=locked_ids,
        season_year=season_year,
        season_type=season_type,
        effective_user_id=effective_user_id,
        group_id=group_id
    )

import json
@main_bp.route('/stream-live-scores')
def stream_live_scores():
    print("Returning live scores:", live_scores_cache)  # Debugging line
    if not live_scores_cache.get('live_games') and not live_scores_cache.get('last_week_games'):
        # Fallback if no cached data
        fallback_data = fetch_live_scores()
        return jsonify(fallback_data)
    
    return jsonify(live_scores_cache)

# Route to render the live scoreboard page
@main_bp.route('/live-scores')
def live_scores_page():
    return render_template('live_scores.html')

from flask_login import current_user
from io import BytesIO
import pandas as pd
from flask import send_file, request

@main_bp.route('/download_picks')
def download_picks():
    # Retrieve the selected week (e.g., from query parameter or default)
    week = request.args.get('week', get_current_week())  # Default to week 9 or dynamically get this value
    
    # Call get_picks with current_user.id and selected week
    picks_data = get_picks(current_user.id, week)
    
    # Convert picks to a DataFrame
    df = pd.DataFrame(picks_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Picks')
    output.seek(0)
    
    # Send the file as an Excel download
    return send_file(
        output, 
        as_attachment=True, 
        download_name='picks.xlsx', 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@main_bp.route('/playoff_bracket')
def playoff_bracket():
    standings = get_nfl_playoff_picture()  # Fetch the playoff data
    afc_bracket, nfc_bracket, super_bowl = map_bracket_data(standings)
    return render_template(
        'bracket.html',
        afc_bracket=afc_bracket,
        nfc_bracket=nfc_bracket,
        super_bowl=super_bowl
    )

@main_bp.route('/odds')
def odds():
    """Route for displaying live odds."""
    odds_data = get_odds_data()  # Centralized odds data logic
    return render_template('odds.html', odds_data=odds_data)


@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = get_serializer().dumps(user.email, salt='password-reset-salt')
            reset_url = url_for('main.reset_password', token=token, _external=True)

            # 👇 Send the email using Brevo
            send_password_reset_email(user.email, reset_url)

            flash('If that email exists, a reset link has been sent.', 'info')
        else:
            flash('If that email exists, a reset link has been sent.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')



@main_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = get_serializer().loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('The reset link has expired.', 'danger')
        return redirect(url_for('main.forgot_password'))
    except BadSignature:
        flash('Invalid reset token.', 'danger')
        return redirect(url_for('main.forgot_password'))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or new_password != confirm_password:
            flash('Passwords do not match or are empty.', 'danger')
            return redirect(request.url)

        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')

@main_bp.route("/leaderboard", methods=["GET"])
@login_required
def leaderboard():
    tab = request.args.get("tab", "season")  # 'season' | 'weekly'

    active_group_id = session.get("active_group_id")
    if not active_group_id:
        flash("No active group selected.", "warning")
        return redirect(url_for("main.groups"))

    settings = Settings.query.first()
    season_year = settings.season_year
    season_type = settings.season_type
    current_week = settings.current_week

    # Weeks available for THIS season/type
    all_weeks = [
        wk for (wk,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type
            )
            .distinct()
            .order_by(Game.week.asc())
            .all()
        )
    ]

    if tab == "weekly":
        week = request.args.get("week", type=int) or current_week
        if all_weeks and week not in all_weeks:
            week = all_weeks[0]

        w_header, w_rows = get_weekly_leaderboard(
            week=week,
            season_year=season_year,
            season_type=season_type,
            group_id=active_group_id,
        )

        return render_template(
            "leaderboard.html",
            tab="weekly",
            current_week=current_week,
            selected_week=week,
            all_weeks=all_weeks,
            weekly_header=w_header,
            weekly_rows=w_rows,
            season_year=season_year,
            season_type=season_type,
        )

    s_header, s_rows = get_season_leaderboard(
        current_week=current_week,
        season_year=season_year,
        season_type=season_type,
        group_id=active_group_id,
    )

    return render_template(
        "leaderboard.html",
        tab="season",
        current_week=current_week,
        all_weeks=all_weeks,
        season_header=s_header,
        season_rows=s_rows,
        season_year=season_year,
        season_type=season_type,
    )

@main_bp.route("/board")
@login_required
def board_threads():
    page = request.args.get("page", 1, type=int)

    threads = (
        BoardThread.query
        .filter(BoardThread.is_active.is_(True))
        .order_by(
            BoardThread.pinned.desc(),
            BoardThread.last_activity_at.desc(),
            BoardThread.created_at.desc(),
        )
        .paginate(page=page, per_page=25, error_out=False)
    )

    return render_template("board_threads.html", threads=threads)
@main_bp.route("/board/thread/<int:thread_id>", methods=["GET", "POST"])
@login_required
def view_thread(thread_id):
    thread = BoardThread.query.get_or_404(thread_id)

    if request.method == "POST":
        if thread.locked:
            flash("Thread is locked.", "warning")
            return redirect(url_for("main.view_thread", thread_id=thread.id))

        body = request.form.get("body")

        if not body:
            flash("Post cannot be empty.", "danger")
        else:
            post = BoardPost(
                thread_id=thread.id,
                author_user_id=current_user.id,
                body=body
            )
            db.session.add(post)

            thread.last_activity_at = datetime.utcnow()

            db.session.commit()

            return redirect(url_for("main.view_thread", thread_id=thread.id))

    posts = (
        BoardPost.query
        .filter_by(thread_id=thread.id, is_active=True)
        .order_by(BoardPost.created_at.asc())
        .all()
    )

    return render_template("thread.html", thread=thread, posts=posts)

@main_bp.route("/board/new", methods=["GET", "POST"])
@login_required
def new_thread():
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")

        if not title or not body:
            flash("Title and body required.", "danger")
        else:
            thread = BoardThread(
                title=title,
                created_by_user_id=current_user.id
            )
            db.session.add(thread)
            db.session.flush()  # get thread.id

            first_post = BoardPost(
                thread_id=thread.id,
                author_user_id=current_user.id,
                body=body
            )
            db.session.add(first_post)

            db.session.commit()

            return redirect(url_for("main.view_thread", thread_id=thread.id))

    return render_template("new_thread.html")

@main_bp.route("/groups/create", methods=["GET", "POST"])
@login_required
def create_group():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        slug = slugify(name)

        if not name:
            flash("Group name is required.", "danger")
            return redirect(url_for("main.create_group"))

        existing = PoolGroup.query.filter_by(slug=slug).first()
        if existing:
            flash("A group with that name already exists.", "warning")
            return redirect(url_for("main.create_group"))

        group = PoolGroup(
            name=name,
            slug=slug,
            is_active=True,
            created_by_user_id=current_user.id,
        )
        db.session.add(group)
        db.session.flush()

        membership = GroupMember(
            user_id=current_user.id,
            group_id=group.id,
            role="commissioner",
            is_active=True,
        )
        db.session.add(membership)
        db.session.commit()

        session["active_group_id"] = group.id
        flash("Group created successfully.", "success")
        return redirect(url_for("main.nfl_picks"))

    return render_template("create_group.html")

@main_bp.route("/groups/switch/<int:group_id>", methods=["POST"])
@login_required
def switch_group(group_id):
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id,
        is_active=True,
    ).first()

    if not membership:
        flash("You do not have access to that group.", "danger")
        return redirect(url_for("main.groups"))

    session["active_group_id"] = group_id
    flash("Active group updated.", "success")
    return redirect(url_for("main.nfl_picks"))
    
@main_bp.route("/groups/join", methods=["GET", "POST"])
@login_required
def join_group():
    if request.method == "POST":
        slug = (request.form.get("slug") or "").strip().lower()

        if not slug:
            flash("Group slug is required.", "danger")
            return redirect(url_for("main.join_group"))

        group = PoolGroup.query.filter_by(slug=slug, is_active=True).first()

        if not group:
            flash("Group not found.", "danger")
            return redirect(url_for("main.join_group"))

        existing_membership = GroupMember.query.filter_by(
            user_id=current_user.id,
            group_id=group.id,
        ).first()

        if existing_membership:
            if not existing_membership.is_active:
                existing_membership.is_active = True
                db.session.commit()

            session["active_group_id"] = group.id
            flash("You are already a member of that group.", "info")
            return redirect(url_for("main.groups"))

        membership = GroupMember(
            user_id=current_user.id,
            group_id=group.id,
            role="member",
            is_active=True,
        )
        db.session.add(membership)
        db.session.commit()

        session["active_group_id"] = group.id
        flash(f"You joined {group.name}.", "success")
        return redirect(url_for("main.nfl_picks"))

    return render_template("join_group.html")

@main_bp.route("/groups", methods=["GET"])
@login_required
def groups():
    from Football_Project.services.group_service import get_active_group_id

    active_group_id = get_active_group_id()

    memberships = (
        db.session.query(GroupMember, PoolGroup)
        .join(PoolGroup, GroupMember.group_id == PoolGroup.id)
        .filter(
            GroupMember.user_id == current_user.id,
            GroupMember.is_active == True,
            PoolGroup.is_active == True,
        )
        .order_by(PoolGroup.name.asc())
        .all()
    )

    return render_template(
        "groups.html",
        memberships=memberships,
        active_group_id=active_group_id,
    )


@main_bp.app_context_processor
def inject_active_group():
    from Football_Project.services.group_service import get_active_group_id

    group_id = get_active_group_id()
    active_group = None
    active_membership = None

    print(f"[CTX] current_user_authenticated={getattr(current_user, 'is_authenticated', False)}")
    print(f"[CTX] group_id={group_id}")

    if group_id and getattr(current_user, "is_authenticated", False):
        active_group = PoolGroup.query.filter_by(id=group_id, is_active=True).first()
        print(f"[CTX] active_group={active_group}")

        if active_group:
            active_membership = GroupMember.query.filter_by(
                user_id=current_user.id,
                group_id=group_id,
                is_active=True,
            ).first()
            print(f"[CTX] active_membership={active_membership}")

    return dict(
        active_group=active_group,
        active_membership=active_membership,
    )