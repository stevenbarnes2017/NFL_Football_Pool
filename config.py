import os
class Config:
    SECRET_KEY = 'password'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///picks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,   # 5 minutes (good match for your job cadence)
}
