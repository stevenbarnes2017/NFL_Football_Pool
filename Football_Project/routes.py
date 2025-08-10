import sys
import os

# Add the parent directory of the current file to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import requests
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, Response
from dateutil import parser
from .models import db, Game, Pick, User, Settings, UserScore
from flask_login import login_required, current_user, login_user, logout_user, login_manager, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from .extensions import db
from Football_Project.get_the_odds import get_nfl_spreads, save_to_csv
from Football_Project.utils import fetch_detailed_game_stats, group_games_by_day, get_saved_games, get_unpicked_games_for_week, live_scores_cache, lock_picks_for_commenced_games, get_highest_available_confidence, save_pick_to_db, convert_to_utc, fetch_live_scores, get_picks, send_picks_email, get_nfl_playoff_picture, map_bracket_data, get_odds_data, generate_token, verify_token, get_serializer, send_password_reset_email
from Football_Project.get_the_odds import get_current_week
from sqlalchemy import func
from dateutil import parser
import time
import pytz
from threading import Thread
from flask import request, flash, redirect, url_for, render_template
from flask_login import current_user, login_required
from datetime import datetime
from pytz import timezone  # Add this
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
#from flask_mail import Message  # if you use Flask-Mail
from .utils import generate_token, verify_token



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
        return redirect(url_for('main.login'))



@main_bp.route('/my_picks', methods=['GET', 'POST'])
@login_required
def my_picks():
    # List of weeks (assuming 17 weeks in the NFL season)
    weeks = list(range(1, 18))

    # Default to current week or use the selected week from the form
    selected_week = int(request.form.get('week', 1))

    # Query for the user's picks for the selected week
    user_picks = Pick.query.filter_by(user_id=current_user.id, week=selected_week).all()

    return render_template('my_picks.html', picks=user_picks, weeks=weeks, selected_week=selected_week)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  # Capture email from the form
        password = request.form.get('password')

        # Check if the username or email already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'danger')
            return redirect(url_for('main.register'))

        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            flash('Email already exists', 'danger')
            return redirect(url_for('main.register'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)  # Include email
        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        full_name = request.form.get('full_name', '').strip()

        # Validate current password if changing password
        if new_password:
            if not check_password_hash(current_user.password, current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('main.edit_profile'))

            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        # Update other fields
        current_user.username = username
        current_user.email = email
        current_user.full_name = full_name

        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('main.edit_profile'))  # or wherever you want to send them

    return render_template('edit_profile.html', user=current_user)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            # Redirect to admin dashboard if the user is an admin
            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))  # Corrected line
            
            # Otherwise, redirect to the regular user dashboard
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return render_template('user_dashboard.html', name=current_user.username, now=datetime.now())
    

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


@main_bp.route('/email_picks', methods=['GET', 'POST'])
@login_required
def email_picks():
    user_id = current_user.id
    recipient = request.form.get('recipient_email', current_user.email)  # Default to current user's email if not provided

    # Fetch the user's picks from the database for the current week
    current_week = get_current_week()
    user_picks = Pick.query.filter_by(user_id=user_id, week=current_week).all()

    # Prepare the picks for the email as a dictionary (Game -> team picked + confidence)
    user_picks_dict = {}
    for pick in user_picks:
        game = f"Game {pick.game_id}"  # You can customize this to use more readable names if needed
        user_picks_dict[game] = {
            'team_picked': pick.team_picked,
            'confidence': pick.confidence
        }

    # Send the email using the send_picks_email function
    try:
        send_picks_email(recipient, user_picks_dict)  # Send email to the specified recipient
        return jsonify({'message': 'Email sent successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/submit_picks', methods=['POST'])
@login_required
def submit_picks():
    from datetime import datetime
    import pytz

    utc = pytz.utc
    now_utc = datetime.now(utc)

    # Week
    try:
        week = int(request.form.get('week', '0'))
    except (TypeError, ValueError):
        flash("Invalid week.", "danger")
        return redirect(url_for('main.nfl_picks'))

    # Pull all games for the week (we’ll read inputs keyed by NATURAL id)
    games = Game.query.filter_by(week=week).all()

    created = updated = locked = skipped = 0

    for game in games:
        nat_id = game.game_id  # e.g. "2025-W2-IND-at-BAL"

        pick_key = f"pick_{nat_id}"
        conf_key = f"confidence_{nat_id}"

        team_picked = (request.form.get(pick_key) or "").strip()
        conf_raw = (request.form.get(conf_key) or "").strip()

        # If the user sent nothing for this game, skip it quietly
        if team_picked == "" and conf_raw == "":
            continue

        # Lock check
        if game.commence_time_mt and now_utc >= game.commence_time_mt.astimezone(utc):
            locked += 1
            continue

        # Parse confidence if present; empty string means "clear it"
        conf_val = None
        conf_set_to_null = False
        if conf_raw == "":
            conf_set_to_null = True  # explicit clear
        else:
            try:
                conf_val = int(conf_raw)
            except ValueError:
                flash(f"Confidence for {nat_id} must be a number.", "warning")
                skipped += 1
                continue

        # Upsert by (user_id, week, numeric FK)
        existing = Pick.query.filter_by(
            user_id=current_user.id,
            week=week,
            game_id=game.id  # IMPORTANT: numeric FK to Game.id
        ).first()

        if existing:
            changed = False
            if team_picked:
                existing.team_picked = team_picked
                changed = True
            if conf_set_to_null:
                existing.confidence = None
                changed = True
            elif conf_val is not None:
                existing.confidence = conf_val
                changed = True

            if changed:
                existing.pick_time = datetime.utcnow()
                updated += 1
            else:
                skipped += 1
        else:
            # New pick: require at least team OR confidence (both allowed).
            # If team missing but confidence provided, we can store a placeholder team or skip.
            # Here we require team to be chosen for a new pick.
            if not team_picked:
                skipped += 1
                continue
            # Confidence can be None (since column is now nullable).
            db.session.add(Pick(
                user_id=current_user.id,
                week=week,
                game_id=game.id,      # numeric FK
                team_picked=team_picked,
                confidence=(None if conf_set_to_null else conf_val),
            ))
            created += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving picks: {e}", "danger")
        return redirect(url_for('main.nfl_picks', week=week))

    flash(
        f"Created: {created}, Updated: {updated}, Locked: {locked}, Skipped: {skipped}",
        "success" if (created or updated) else "warning"
    )
    return redirect(url_for('main.nfl_picks', week=week))



@main_bp.route('/get_current_week')
def current_week():
    week = get_current_week()  # Call your existing function
    return jsonify({"current_week": week})

  




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
    lock_picks_for_commenced_games(current_user.id)
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
    week = get_current_week()
    # Fetch the current user's pre-calculated score for the given week
    current_user_score = UserScore.query.filter_by(user_id=current_user.id, week=week).first()
    current_user_score = current_user_score.score if current_user_score else 0

    # Fetch all pre-calculated scores for the given week
    all_scores = UserScore.query.filter_by(week=week).all()

    # Prepare the scores for display
    all_user_scores = {
        score.user_id: {
            'username': score.user.username,
            'score': score.score
        } for score in all_scores
    }

    return render_template('user_scores.html', current_user_score=current_user_score, all_scores=all_user_scores, week=week)


@main_bp.route('/see_picks', methods=['GET', 'POST'])
@login_required
def see_picks():
    # Dynamically get the current week based on the NFL season start date
    current_week = get_current_week()

    # Get the selected week from the form or default to the current week
    if request.method == 'POST':
        selected_week = int(request.form.get('week', current_week))
    else:
        selected_week = current_week

    # Get all available weeks
    all_weeks = list(range(1, current_week + 1))  # All weeks up to current week


    # Get the user's picks for the selected week
    user_picks = Pick.query.filter_by(user_id=current_user.id, week=selected_week).all()
    

    # Get unpicked games for the selected week
    unpicked_games = get_unpicked_games_for_week(user_picks, selected_week)

    return render_template(
        'see_picks.html', 
        selected_week=selected_week,   # Pass the selected week
        all_weeks=all_weeks,           # Pass the list of all available weeks
        user_picks=user_picks, 
        unpicked_games=unpicked_games
    )


from flask import jsonify, request

@main_bp.route('/user_score_summary', methods=['GET'])
@login_required
def user_score_summary():
    # Get the selected week from query params, or default to 'all'
    selected_week = request.args.get('week', 'all')  # Initialize here to ensure it always has a value

    # Check if the request is coming from the live scores page and wants the current week
    if selected_week == 'current':
        selected_week = get_current_week() - 1
        print(f"nfl start date = {datetime(2024, 9,5).date()}")
        print(f"current date = {datetime.now().date()}")


    try:
        # Convert selected_week to int if it's not 'all'
        if selected_week != 'all':
            selected_week = int(selected_week)
    except ValueError:
        flash("Invalid week selected.", "danger")
        return redirect(url_for('main.user_dashboard'))

    # Ensure current_user_id is defined
    current_user_id = current_user.id

    # Fetch total scores based on the selected week
    if selected_week == 'all':
        # Fetch scores across all weeks
        user_scores = db.session.query(
            User.id,
            User.username,
            func.coalesce(func.sum(UserScore.score), 0).label('total_score')
        ).outerjoin(UserScore, User.id == UserScore.user_id).group_by(User.id) \
         .order_by(func.coalesce(func.sum(UserScore.score), 0).desc()).all()

        # Current user's total score for all weeks
        user_total_score = db.session.query(
            func.coalesce(func.sum(UserScore.score), 0)
        ).filter_by(user_id=current_user_id).scalar() or 0
    else:
        # Fetch scores for the specific week for all users
        user_scores = db.session.query(
            User.id,
            User.username,
            func.coalesce(UserScore.score, 0).label('total_score')
        ).outerjoin(UserScore, (User.id == UserScore.user_id) & (UserScore.week == selected_week)) \
        .group_by(User.id) \
        .order_by(func.coalesce(UserScore.score, 0).desc()).all()

        # Current user's total score for the specific week
        user_total_score = db.session.query(
            func.coalesce(UserScore.score, 0)
        ).filter_by(user_id=current_user_id, week=selected_week).scalar() or 0

    # Fetch the games and user's picks for the selected week
    games = Game.query.filter_by(week=selected_week).all()
    user_picks = Pick.query.filter_by(user_id=current_user_id, week=selected_week).all()

    # Prepare game data with the user's picks
    game_picks = []
    for game in games:
        game_data = {
            'game_id': game.id,
            'home_team': game.home_team,
            'away_team': game.away_team,
            'spread': float(game.spread) if game.spread else None,
            'favorite_team': game.favorite_team,
            'home_team_score': game.home_team_score,
            'away_team_score': game.away_team_score,
            'status': game.status,
            'pick': None
        }

        # Find the user's pick for this game
        for pick in user_picks:
            if pick.game_id == game.id:
                game_data['pick'] = {
                    'team_picked': pick.team_picked,
                    'confidence': pick.confidence,
                    'points_earned': pick.points_earned
                }
                break

        game_picks.append(game_data)

    # Debug logging to verify fetched data
    import json
    import logging
    logging.debug(f"user_total_score: {user_total_score}")
    logging.debug(f"game_picks: {json.dumps(game_picks, indent=2)}")

    # Prepare weeks for the dropdown if needed
    weeks = db.session.query(Game.week).distinct().order_by(Game.week).all()
    weeks = [week[0] for week in weeks]

    # Check if the request expects JSON (from AJAX)
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        # Prepare JSON response
        response_data = {
            'user_scores': [
                {
                    'id': user.id,
                    'username': user.username,
                    'total_score': user.total_score
                }
                for user in user_scores
            ],
            'game_picks': game_picks,
            'user_total_score': user_total_score,
            'selected_week': selected_week,
            'weeks': weeks
        }

       
        return jsonify(response_data)
    else:
        # Render the HTML template as before
        return render_template(
            'user_score_summary.html',
            user_scores=user_scores,
            game_picks=game_picks,
            user_total_score=user_total_score,
            selected_week=selected_week,
            weeks=weeks
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

    # Week selection
    selected_week = request.form.get('week', type=int) or request.args.get('week', type=int)
    current_week = get_current_week()
    if not selected_week:
        selected_week = current_week

    utc = pytz.utc
    mt = pytz.timezone("America/Denver")
    now_utc = datetime.now(utc)

    # Games for the week
    games = Game.query.filter_by(week=selected_week).order_by(Game.commence_time_mt).all()
    num_of_games = len(games)

    # JOIN Pick -> Game so we can key by NATURAL ID for the template
    rows = (
        db.session.query(Pick, Game)
        .join(Game, Pick.game_id == Game.id)
        .filter(Pick.user_id == current_user.id, Pick.week == selected_week)
        .all()
    )
    # user_picks: { natural_game_id: (team_picked, confidence_or_None) }
    user_picks = {g.game_id: (p.team_picked, p.confidence) for p, g in rows}
    # only numbers for the sidebar; exclude None
    used_confidence_points = [p.confidence for p, _ in rows if p.confidence is not None]

    # Which games are locked (kickoff passed)?
    locked_ids = set()
    for g in games:
        if g.commence_time_mt and now_utc >= g.commence_time_mt.astimezone(utc):
            locked_ids.add(g.game_id)

    # Group games by Mountain weekday for display
    grouped_games = {}
    for g in games:
        dt_mt = g.commence_time_mt.astimezone(mt) if g.commence_time_mt else None
        day = dt_mt.strftime("%A") if dt_mt else "Unknown"
        grouped_games.setdefault(day, []).append(g)

    # OPTIONAL: if you auto-assign confidence for already-started, no-pick games,
    # do it here and also append to used_confidence_points so the sidebar reflects it.
    # If you don't want auto-assignment, delete this block.
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

    # (Optional) debug so you can verify values will render:
    print("user_picks ->", user_picks)
    print("used_confidence_points ->", used_confidence_points)

    all_weeks = list(range(1, current_week + 1))

    return render_template(
        'nfl_picks.html',
        grouped_games=grouped_games,
        num_of_games=num_of_games,
        now_utc=now_utc,
        selected_week=selected_week,
        all_weeks=all_weeks,
        user_picks=user_picks,                # <-- drives the input value
        used_confidence_points=used_confidence_points,
        locked_ids=locked_ids
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

        return redirect(url_for('main.login'))

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
        return redirect(url_for('main.login'))

    return render_template('reset_password.html')




    



