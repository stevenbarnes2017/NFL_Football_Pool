from Football_Project import create_app, scheduler

app = create_app()

with app.app_context():
    scheduler.start()