# admin/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, Flask
from flask_login import login_required, current_user
from Football_Project.models import Game, User
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from . import routes

# Initialize extensions without passing the app instance yet
db = SQLAlchemy()



def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///picks.db'  # Example configuration, adjust as necessary
    app.config['SECRET_KEY'] = 'password'
    
    # Initialize extensions with the app
    db.init_app(app)
   

    # Import and register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app





