from .extensions import db
from flask_login import UserMixin
from datetime import datetime


#Create Classes that define the user and pick.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    picks = db.relationship('Pick', backref='user', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)  # Add this line to distinguish admins

class Pick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    team_picked = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Integer, nullable=False)
    pick_time = db.Column(db.DateTime, default=datetime.utcnow)
    week = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    is_overridden = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Pick {self.id} - User {self.user_id} - Game {self.game_id}>'
    
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_week = db.Column(db.Integer, nullable=False, default=1)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(50), nullable=False)
    away_team = db.Column(db.String(50), nullable=False)
    spread = db.Column(db.Float, nullable=True)
    favorite_team = db.Column(db.String(50), nullable=True)
    commence_time_mt = db.Column(db.String(50), nullable=True)
    home_team_score = db.Column(db.Integer, nullable=True)
    away_team_score = db.Column(db.Integer, nullable=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=True)
    week = db.Column(db.Integer, nullable=False)
    picks = db.relationship('Pick', backref='game', lazy=True)

    def __repr__(self):
        return f'<Game {self.id} - {self.home_team} vs {self.away_team}>'


class UserScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)  # Track scores by week
    score = db.Column(db.Float, nullable=False, default=0)  # Allow score to be updated or overridden
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)  # Track when the score was calculated

    # Relationships
    user = db.relationship('User', backref=db.backref('scores', lazy=True))