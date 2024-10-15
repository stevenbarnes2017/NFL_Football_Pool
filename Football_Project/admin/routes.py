# admin/routes.py
from flask import render_template, request, redirect, url_for, flash, send_file, Blueprint
from flask_login import login_required, current_user
from get_the_odds import get_nfl_spreads, save_spreads_to_db, get_current_week, save_to_csv
from datetime import datetime, timedelta
from football_scores import get_football_scores, save_scores_to_csv, save_scores_to_db
from Football_Project.models import db, Game, Settings, User, UserScore, Pick
from Football_Project.utils import calculate_user_scores, save_game_scores_to_db
from . import admin_bp



print("Setting up before_request for admin_bp")



@admin_bp.before_request
def before_request():
    # Check if the user is logged in and is an admin
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))  # Redirect to login if not authenticated
    
    # Assuming you have an `is_admin` property on your User model
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect to home page if not an admin
# Define other routes...

@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('main.index'))
    
    current_year = datetime.utcnow().year    
    default_season_type = 2  # Default to Regular season
    current_week = get_current_week()
    all_weeks = list(range(1, current_week +1))
    users = User.query.order_by(User.username).all()    
    return render_template(
        'admin_dashboard.html',
        current_year=current_year,        
        default_season_type=default_season_type,
        weeks=all_weeks,
        users=users
    )

@admin_bp.route('/fetch_odds', methods=['POST'])
@login_required
def fetch_odds():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))

    try:
        
        week_option = request.form.get('week_option')       
        week = int(request.form.get('week_number')) if week_option == 'override' else get_current_week()  
        games_list, num_of_games = get_nfl_spreads()     
        if not games_list:
            flash("No odds data available for the selected week.", "warning")
            return redirect(url_for('admin.admin_dashboard'))        
        return render_template('display_odds.html', games_list=games_list, week=week)
    except Exception as e:        
        flash(f"An error occurred while fetching the odds: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))


    
@admin_bp.route('/fetch_scores', methods=['POST'])
@login_required
def fetch_scores():
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))

    # Fetch form data for year, season type, and week number
    year = request.form.get('year')
    seasontype = request.form.get('seasontype')
    weeknum = request.form.get('weeknum')
    action = request.form.get('action')

    # Fetch and save the scores using the helper function
    try:
        scores = get_football_scores(year, seasontype, weeknum)  # Fetch the scores
        if action == 'save_to_db':
            result = save_game_scores_to_db(scores, weeknum)  # Save the scores to the database
            flash(f"Successfully saved game scores for week {weeknum}.", "success")

        elif action == 'download_csv':
            # Save the scores to a CSV file and send it for download
            filename = f"football_scores_week{weeknum}.csv"
            save_scores_to_csv(scores, filename)
            return send_file(filename, as_attachment=True)

    except Exception as e:
        print(f"An error occurred while fetching or saving the scores: {e}")
        flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for('admin.admin_dashboard'))



@admin_bp.route('/save_odds', methods=['POST'])
@login_required
def save_odds():

    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))    

    try:
        action = request.form.get('action')
        games_list, week = get_nfl_spreads()
        week = int(request.form.get('week'))
        if action == "db":
            save_spreads_to_db(games_list, week)
            flash(f"Odds for week {week} have been saved to the database.", "success")
        elif action == "csv":
            filename = f'nfl_spreads_week_{week}.csv'
            save_to_csv(games_list, filename)
            flash(f"Odds for week {week} have been saved to {filename}.", "success")
        else:
            flash("Invalid action.", "danger")

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
    
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/display_odds')
def display_odds():
   
    # Get the current week from the settings or determine it dynamically
    settings = Settings.query.first()
    current_week = settings.current_week if settings else get_current_week()
    games = Game.query.filter_by(week=current_week).all()
    return render_template('display_odds.html', games_list=games)

@admin_bp.route('/admin_scores', methods=['GET'])
@login_required
def admin_scores():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))

    # Get the selected week from query params, or default to 'all'
    selected_week = request.args.get('week', 'all')
    
    try:
        if selected_week != 'all':
            selected_week = int(selected_week)
    except ValueError:
        flash("Invalid week selected.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    # Get the selected user (optional for filtering by user)
    selected_user = request.args.get('user', 'all')

    try:
        if selected_user != 'all':
            selected_user = int(selected_user)
    except ValueError:
        flash("Invalid user selected.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    # Fetch all users from the database
    all_users = User.query.order_by(User.username).all()

    # Prepare a dictionary for user totals, initialized to 0
    user_totals = {user.username: 0 for user in all_users}

    # Fetch the user scores for the selected week or all weeks
    if selected_week == 'all':
        # Sum up all weeks
        user_scores = db.session.query(UserScore.user_id, db.func.sum(UserScore.score).label('total_score')) \
                                .group_by(UserScore.user_id).all()
    else:
        # Fetch only the user scores for the selected week
        user_scores = UserScore.query.filter_by(week=selected_week).all()

    # Populate user_totals based on the query results
    for score in user_scores:
        if selected_week == 'all':
            user_totals[User.query.get(score.user_id).username] = score.total_score
        else:
            user_totals[User.query.get(score.user_id).username] = score.score

    # Fetch games and picks based on filters (week and optionally user)
    if selected_week == 'all':
        games = Game.query.order_by(Game.week).all()
    else:
        games = Game.query.filter_by(week=selected_week).all()

    if selected_week == 'all' and selected_user == 'all':
        picks = Pick.query.all()
    elif selected_week == 'all':
        picks = Pick.query.filter_by(user_id=selected_user).all()
    elif selected_user == 'all':
        picks = Pick.query.filter_by(week=selected_week).all()
    else:
        picks = Pick.query.filter_by(week=selected_week, user_id=selected_user).all()

    # Prepare the game and pick data for display
    game_picks = []

    for game in games:
        game_data = {
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
                points_earned = pick.points_earned  # Assuming points are calculated and stored
                game_data['picks'].append({
                    'username': pick.user.username,
                    'confidence': pick.confidence,
                    'points_earned': points_earned,
                    'user_id': pick.user_id
                })

        game_picks.append(game_data)

    # Fetch distinct weeks for the dropdown
    weeks = db.session.query(Game.week).distinct().order_by(Game.week).all()
    weeks = [week[0] for week in weeks]

    return render_template(
        'admin_scores.html',
        game_picks=game_picks,  # Pass the game_picks data for detailed display
        user_totals=user_totals,  # Pass user totals for summary
        selected_week=selected_week,
        weeks=weeks,
        selected_user=selected_user,
        users=all_users
    )






@admin_bp.route('/admin_calculate_scores', methods=['POST']) 
@login_required
def admin_calculate_scores():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))

    selected_week = request.form.get('week', 'all')

    if selected_week == 'all':
        # Calculate scores for all weeks
        for week in range(1, get_current_week + 1):  # Assuming you track the current week
            user_scores = calculate_user_scores(week=week)
            save_scores_to_db(user_scores, week)
        flash("Total scores for all users have been calculated.", "success")
    else:
        try:
            selected_week = int(selected_week)
        except ValueError:
            flash("Invalid week selected.", "danger")
            return redirect(url_for('admin.admin_dashboard'))

        user_scores = calculate_user_scores(week=selected_week)
        save_scores_to_db(user_scores, selected_week)
        flash(f"Scores for Week {selected_week} have been calculated.", "success")

    return redirect(url_for('admin.admin_dashboard'))

def save_scores_to_db(game_scores, week):
    """
    Save or update game scores in the database for a specific week.
    This function assumes that game_scores is a list of dictionaries with game details.
    """
    print(f"game_scores structure: {game_scores}")  # Debug print to show the full structure
    
    # Check if game_scores is a list
    if isinstance(game_scores, list):
        for index, game_score in enumerate(game_scores):
            print(f"Processing item {index}: {game_score}")  # Print each item in the list
            
            if isinstance(game_score, dict):
                home_team = game_score.get('home_team')  # Extract home team
                away_team = game_score.get('away_team')  # Extract away team
                home_score = game_score.get('home_score')  # Extract home team score
                away_score = game_score.get('away_score')  # Extract away team score
                status = game_score.get('status')  # Extract game status
                
                # Ensure that required fields are present
                if home_team and away_team and home_score is not None and away_score is not None:
                    # Check if the game record already exists for this week
                    game_record = Game.query.filter_by(home_team=home_team, away_team=away_team, week=week).first()
                    
                    if game_record:
                        # Update existing game record
                        game_record.home_team_score = home_score
                        game_record.away_team_score = away_score
                        game_record.status = status
                        print(f"Updated game record for {home_team} vs {away_team}")
                    else:
                        # Create a new game record if it doesn't exist
                        game_record = Game(
                            home_team=home_team,
                            away_team=away_team,
                            home_team_score=home_score,
                            away_team_score=away_score,
                            status=status,
                            week=week
                        )
                        db.session.add(game_record)
                        print(f"Added new game record for {home_team} vs {away_team}")
                else:
                    print(f"Missing required data for game {index}: {game_score}")
            else:
                print(f"Unexpected structure for item {index}: {game_score}")
        
        # Commit the changes to the database
        db.session.commit()
        print(f"Committed all game scores for week {week}")
    else:
        print("Error: game_scores is not a list!")

@admin_bp.route('/admin_override_score', methods=['POST'])
@login_required
def admin_override_score():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))

    # Get data from the form
    user_id = request.form.get('user_id')
    week = request.form.get('week')
    game_id = request.form.get('game_id')
    new_score = request.form.get('new_score')

    # Convert the new_score to a float
    try:
        new_score = float(new_score)
    except ValueError:
        flash("Invalid score value.", "danger")
        return redirect(url_for('admin.admin_scores', week=week))

    # Find the pick associated with this game and user
    pick = Pick.query.filter_by(user_id=user_id, game_id=game_id, week=week).first()

    if not pick:
        flash("Pick not found.", "danger")
        return redirect(url_for('admin.admin_scores', week=week))

    # Update the points_earned field and set is_overridden to True
    pick.points_earned = new_score
    pick.is_overridden = True  # Mark the pick as overridden
    db.session.add(pick)
    db.session.commit()

    # Call the existing calculate_user_scores function to recalculate the total points for the user
    calculate_user_scores(week)

    flash("Score successfully overridden and total updated.", "success")
    return redirect(url_for('admin.admin_scores', week=week))




@admin_bp.route('/process_user_scores', methods=['POST'])
@login_required
def process_user_scores():
    # Check if the current user has admin permissions
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))

    try:
        # Assuming this function returns the current week (you can adjust this as needed)
        current_week = get_current_week()  

        # Fetch all distinct weeks available in the games table, excluding the current week
        available_weeks = db.session.query(Game.week).distinct().order_by(Game.week).all()
        available_weeks = [week[0] for week in available_weeks if week[0] != current_week]

        for week in available_weeks:
            games = Game.query.filter_by(week=week).all()

            # Process each game for the week
            for game in games:
                # Skip games that don't have necessary score or spread data
                if game.home_team_score is None or game.away_team_score is None or game.spread is None:
                    print(f"Skipping game {game.id} due to missing data")
                    continue

                # Process the game and calculate margin, spread, etc.
                try:
                    home_team_margin = game.home_team_score - game.away_team_score
                    final_spread = abs(game.spread)
                    points_earned = 1 if home_team_margin > final_spread else 0  # Simplified calculation
                except Exception as calc_error:
                    print(f"Error processing game {game.id}: {calc_error}")
                    continue

            # Calculate user scores for the week using your calculate_user_scores function
            user_scores = calculate_user_scores(week=week)

            if not isinstance(user_scores, dict):
                print(f"Invalid user_scores for week {week}. Skipping...")
                continue

            # Fetch all user_scores for the users involved in this week's games
            user_ids = list(user_scores.keys())
            existing_user_scores = UserScore.query.filter(UserScore.user_id.in_(user_ids), UserScore.week == week).all()

            # Create a mapping for existing scores to easily update them later
            user_score_map = {user_score.user_id: user_score for user_score in existing_user_scores}

            # Iterate through the calculated user scores and update/create UserScore records
            for user_id, week_score in user_scores.items():
                if user_id in user_score_map:
                    # Update the existing UserScore for the week
                    user_score_map[user_id].score = week_score  # Update the score instead of incrementing
                else:
                    # Create a new UserScore for the week
                    new_user_score = UserScore(
                        user_id=user_id,
                        week=week,  # Ensure the week is set correctly
                        score=week_score,
                        calculated_at=datetime.utcnow()
                    )
                    db.session.add(new_user_score)

            # Commit all the changes for the week
            db.session.commit()

        flash("Successfully processed and saved user scores", "success")

    except Exception as e:
        # Rollback any changes if an error occurs during the process
        db.session.rollback()
        print(f"An error occurred while processing user scores: {e}")
        flash(f"An error occurred while processing user scores: {str(e)}", "danger")

    return redirect(url_for('admin.admin_dashboard'))


