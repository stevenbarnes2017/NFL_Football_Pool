# Football_Project/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp, ValidationError, Optional
)
from sqlalchemy import func

from Football_Project import db
from Football_Project.models import User

# 3–20 chars, letters/digits/underscore only (no spaces/specials)
USERNAME_RE = r"^[A-Za-z0-9_]{3,20}$"

# Block obvious/reserved names (extend as needed)
RESERVED_USERNAMES = {
    "admin", "administrator", "moderator", "support", "help",
    "root", "system", "null", "undefined", "api", "staff"
}

def _strip(v: str | None) -> str | None:
    return v.strip() if isinstance(v, str) else v

class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=20, message="Use 3–20 characters."),
            Regexp(USERNAME_RE, message="Letters, numbers, or underscore only."),
        ],
        filters=[_strip],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=255)],
        filters=[lambda s: _strip(s).lower() if s else s],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"autocomplete": "new-password"},
    )
    password_confirm = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    group_id = SelectField("Join a Group", coerce=int, validators=[Optional()])
    create_group = BooleanField("Create a New Group")
    new_group_name = StringField("New Group Name", validators=[Optional()])
    submit = SubmitField("Create account")

    # Server-side uniqueness & reserved checks (case-insensitive) — no DB changes required
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data, is_active=True).first()
        if user:
            raise ValidationError("That username is taken. Please choose a different one.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data, is_active=True).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")

class LoginForm(FlaskForm):
    # Allow username OR email in one field
    username = StringField(
        "Username",
        validators=[DataRequired()],
        filters=[_strip],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")
