# Football_Project/auth/routes.py
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from Football_Project import db
from Football_Project.models import User
from . import auth_bp
from .forms import RegisterForm, LoginForm


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data,
        )
        user.set_password(form.password.data)  # <-- hash here
        db.session.add(user)
        db.session.commit()

        flash("Account created. Welcome!", "success")
        login_user(user)
        return redirect(request.args.get("next") or url_for("main.index"))

    if request.method == "POST":
        # optional: flash field errors so the form doesn't feel like it "reset"
        for field, errs in form.errors.items():
            for e in errs:
                flash(f"{field.capitalize()}: {e}", "danger")

    return render_template("auth/register.html", form=form)



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        ident = (form.username.data or "").strip()   # or .identifier if you use that
        pwd   = form.password.data or ""

        user = User.query.filter(func.lower(User.username) == ident.lower()).first()
        if not user:
            user = User.query.filter(func.lower(User.email) == ident.lower()).first()

        if user and user.check_password(pwd):
            # Optional: upgrade legacy plaintext → preferred hash
            if not user.is_password_hashed():
                user.set_password(pwd)
                db.session.commit()

            login_user(user, remember=form.remember.data)
            return redirect(request.args.get("next") or url_for("main.index"))

        flash("Invalid credentials.", "danger")

    return render_template("auth/login.html", form=form)




@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Signed out.", "success")
    return redirect(url_for("main.index"))
