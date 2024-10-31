from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, Response
from dateutil import parser
from .models import db, Game, Pick, User, Settings, UserScore
from flask_login import login_required, current_user, login_user, logout_user, login_manager, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from .extensions import db
from Football_Project.get_the_odds import get_nfl_spreads, save_to_csv
from Football_Project.utils import fetch_detailed_game_stats, group_games_by_day, get_saved_games, get_unpicked_games_for_week, fetch_live_scores, lock_picks_for_commenced_games, get_highest_available_confidence, save_pick_to_db, convert_to_utc
from get_the_odds import get_current_week
from sqlalchemy import func
from dateutil import parser
import time
import pytz
from threading import Thread
from flask import request, flash, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime
from pytz import timezone  # Add this
from dateutil import parser  # This helps to handle parsing strings to datetime






main_bp = Blueprint('main', __name__)

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
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        # Check current password if changing password
        if new_password and not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('edit_profile'))

        # Update fields
        current_user.username = username
        current_user.email = email

        if new_password:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('profile'))

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




@main_bp.route('/submit_picks', methods=['POST'])
@login_required
def submit_picks():
    selected_week = request.form.get('week')
    num_of_games = int(request.form.get('num_of_games'))
    user_id = current_user.id

    # Ensure we're not using any part of dateutil
    print(">>> Using pytz for timezone handling, dateutil should not be involved.")
    
    mountain_tz = pytz.timezone("America/Denver")
    utc = pytz.utc

    now_utc = datetime.now(pytz.utc)

    for key in request.form.keys():
        if key.startswith('game_id_'):
            game_id = request.form.get(key)
            if not game_id:
                print(f"Skipping game as no game ID was found for key {key}.")
                continue

            game = Game.query.get(game_id)
            if not game:
                print(f"Game {game_id} does not exist.")
                continue

            commence_time_str = game.commence_time_mt
            print(f"Commence time (string) for game {game_id}: {commence_time_str}")

            try:
                dt_str, tz_abbr = commence_time_str.rsplit(' ', 1)
                naive_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

                if tz_abbr == 'MDT':
                    print(">>> Localizing with Mountain Time (MDT)")
                    commence_time = mountain_tz.localize(naive_time)
                elif tz_abbr == 'MST':
                    print(">>> Localizing with Mountain Time (MST)")
                    commence_time = mountain_tz.localize(naive_time)
                else:
                    raise ValueError(f"Unknown timezone abbreviation: {tz_abbr}")

                commence_time = commence_time.astimezone(pytz.utc)
            except (ValueError, TypeError) as e:
                print(f"Error parsing commence time for game {game_id}: {e}")
                flash(f"Error with commence time for game {game_id}.")
                continue

            print(f"Commence time (datetime) for game {game_id}: {commence_time}")

            if now_utc >= commence_time:
                print(f"Game {game_id} has already started, pick cannot be made.")
                continue

            team_picked = request.form.get(f'pick_{game_id}')
            confidence_score = request.form.get(f'confidence_{game_id}')

            print(f"Processing pick for game {game_id}: {team_picked}, confidence: {confidence_score}")

            if not team_picked or not confidence_score:
                flash(f'Missing pick or confidence score for game {game_id}')
                print(f"Skipping game {game_id} due to missing pick or confidence.")
                continue

            save_pick_to_db(user_id, int(selected_week), game_id, team_picked, int(confidence_score))
            print(f"Pick saved for game {game_id}")

    flash('Picks submitted successfully!')
    return redirect(url_for('main.nfl_picks', week=selected_week))




  




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
    all_weeks = list(range(1, current_week + 1))  # List of all weeks up to the current week

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
    selected_week = request.args.get('week', 'all')

    # Check if the request is coming from the live scores page and wants the current week
    if selected_week == 'current':
        selected_week = get_current_week()

    try:
        if selected_week != 'all':
            selected_week = int(selected_week)
    except ValueError:
        flash("Invalid week selected.", "danger")
        return redirect(url_for('main.user_dashboard'))

    current_user_id = current_user.id

    # Fetch total scores based on the selected week
    if selected_week == 'all':
        # Placeholder logic for fetching scores across all weeks
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

mountain_tz = timezone('America/Denver')

def convert_utc_to_mountain(utc_time):
    """Convert UTC time back to Mountain Time."""
    return utc_time.astimezone(mountain_tz)


@main_bp.route('/nfl_picks', methods=['GET', 'POST'])
@login_required
def nfl_picks():
    selected_week = request.form.get('week', type=int) or request.args.get('week', default=None, type=int)
    current_week = get_current_week()
    
    if not selected_week:
        selected_week = current_week

    user_id = current_user.id
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)  # Current time in UTC
    print(f"Current UTC time: {now_utc}")  # Debug current time

    # Retrieve user's picks for the selected week
    user_picks_db = Pick.query.filter_by(user_id=user_id, week=selected_week).all()
    user_picks = {pick.game_id: (pick.team_picked, pick.confidence) for pick in user_picks_db}

    # Retrieve saved games for the selected week
    saved_games = get_saved_games(week=selected_week)
    if saved_games:
        num_of_games = len(saved_games)

        for game in saved_games:
            commence_time_str = game['commence_time_mt']
            print(f"Original commence time string for game {game['id']}: {commence_time_str}")

            # Convert commence_time_mt to UTC using the conversion function
            try:
                game['commence_time_mt'] = convert_to_utc(commence_time_str)
                print(f"Game {game['id']} converted commence time (UTC): {game['commence_time_mt']}")
            except Exception as e:
                print(f"Error converting commence time for game {game['id']}: {e}")
                continue  # Skip this game if there's a conversion error

        # Now convert the UTC time back to Mountain Time for display and grouping
        for game in saved_games:
            game['commence_time_mt_display'] = convert_utc_to_mountain(game['commence_time_mt'])
            print(f"Game {game['id']} converted commence time (Mountain Time for display): {game['commence_time_mt_display']}")

        # Group games by Mountain Time day
        grouped_games = group_games_by_day(saved_games)
        total_confidence_points = list(range(1, num_of_games + 1))
        used_confidence_points = [pick.confidence for pick in user_picks_db]

        for game in saved_games:
            game_id = game['id']
            if now_utc >= game['commence_time_mt'] and game_id not in user_picks:
                highest_available_confidence = get_highest_available_confidence(total_confidence_points, used_confidence_points)
                if highest_available_confidence:
                    user_picks[game_id] = ('No pick made', highest_available_confidence)
                    used_confidence_points.append(highest_available_confidence)

    else:
        grouped_games = {"Thursday": [], "Friday": [], "Sunday": [], "Monday": []}
        num_of_games = 0
        used_confidence_points = []

    all_weeks = list(range(1, current_week + 1))

    return render_template(
        'nfl_picks.html',
        grouped_games=group_games_by_day(saved_games),
        num_of_games=num_of_games,
        now_utc=now_utc,
        selected_week=selected_week,
        all_weeks=all_weeks,
        user_picks=user_picks,
        used_confidence_points=used_confidence_points  # Pass the used confidence points
    )



import json
@main_bp.route('/stream-live-scores')
def stream_live_scores():
    def event_stream():
        while True:
            # Fetch the live scores (or last week's scores) every 30 seconds
            scores_data = fetch_live_scores()
            yield f"data: {json.dumps(scores_data)}\n\n"  # Convert to JSON string
            time.sleep(30)  # Update every 30 seconds

    return Response(event_stream(), content_type='text/event-stream')


# Route to render the live scoreboard page
@main_bp.route('/live-scores')
def live_scores_page():
    return render_template('live_scores.html')





    



