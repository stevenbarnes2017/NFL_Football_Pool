# Football_Project/auth/routes.py
from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from Football_Project import db
from Football_Project.models import User, GroupMember, PoolGroup
from . import auth_bp
from .forms import RegisterForm, LoginForm


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()

    # Populate group dropdown
    groups = PoolGroup.query.filter_by(is_active=True).order_by(PoolGroup.name).all()
    form.group_id.choices = [(0, "Select a group")] + [(g.id, g.name) for g in groups]

    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)

        # 🔥 Invite takes priority
        pending_token = session.pop("pending_invite_token", None)
        if pending_token:
            return redirect(url_for("main.accept_invite", token=pending_token))

        # 🔥 Create group
        if form.create_group.data and form.new_group_name.data:
            group = PoolGroup(
                name=form.new_group_name.data.strip(),
                is_active=True
            )
            db.session.add(group)
            db.session.flush()

            membership = GroupMember(
                user_id=user.id,
                group_id=group.id,
                role="group_admin",
                is_active=True,
            )
            db.session.add(membership)
            db.session.commit()

            session["active_group_id"] = group.id
            return redirect(url_for("main.dashboard"))

        # 🔥 Join selected group
        if form.group_id.data and form.group_id.data != 0:
            membership = GroupMember(
                user_id=user.id,
                group_id=form.group_id.data,
                role="member",
                is_active=True,
            )
            db.session.add(membership)
            db.session.commit()

            session["active_group_id"] = form.group_id.data
            return redirect(url_for("main.dashboard"))

        # 🔥 fallback
        return redirect(url_for("main.post_auth_group_choice"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        ident = (form.username.data or "").strip()
        pwd = form.password.data or ""

        user = User.query.filter(func.lower(User.username) == ident.lower()).first()
        if not user:
            user = User.query.filter(func.lower(User.email) == ident.lower()).first()

        if user and user.check_password(pwd):
            if not user.is_password_hashed():
                user.set_password(pwd)
                db.session.commit()

            login_user(user, remember=form.remember.data)

            pending_token = session.pop("pending_invite_token", None)
            if pending_token:
                return redirect(url_for("main.accept_invite", token=pending_token))

            has_groups = GroupMember.query.filter_by(
                user_id=user.id,
                is_active=True,
            ).first()

            if not has_groups:
                return redirect(url_for("main.post_auth_group_choice"))

            return redirect(request.args.get("next") or url_for("main.index"))

        flash("Invalid credentials.", "danger")

    return render_template("auth/login.html", form=form)
    

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Signed out.", "success")
    return redirect(url_for("main.index"))
