# scripts/fix_naive_kickoffs.py
import pytz
from Football_Project.app import app
from Football_Project.extensions import db
from Football_Project.models import Game

mt = pytz.timezone("America/Denver")

with app.app_context():
    updated = 0
    for g in Game.query.filter(Game.commence_time_mt.isnot(None)).all():
        dt = g.commence_time_mt
        if dt.tzinfo is None:
            g.commence_time_mt = mt.localize(dt)
            updated += 1
    if updated:
        db.session.commit()
    print(f"Normalized {updated} kickoff datetimes to Mountain time.")
