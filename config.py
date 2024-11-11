import os
class Config:
    SECRET_KEY = 'password'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///picks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

    BREVO_API_KEY = os.environ.get('BREVO_API_KEY')