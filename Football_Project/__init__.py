# __init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import User  # Import your User model
from .extensions import db  # Assuming db is initialized in extensions.py
<<<<<<< HEAD
=======
from flask_migrate import Migrate
>>>>>>> 128523e0dbc489f40d5f6df48db8a3b0113a97a8


def create_app():
    app = Flask(__name__)

    # App configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///picks.db'
    app.config['SECRET_KEY'] = 'password'
    
    # Initialize extensions
    db.init_app(app)
  
<<<<<<< HEAD
=======
    #Initialize Flask-Migrate
    migrate = Migrate(app, db)
>>>>>>> 128523e0dbc489f40d5f6df48db8a3b0113a97a8

    # Initialize the login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints (after initializing extensions)
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Define the user_loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
