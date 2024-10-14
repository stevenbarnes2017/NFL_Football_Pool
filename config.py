class Config:
    SECRET_KEY = 'password'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///picks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes