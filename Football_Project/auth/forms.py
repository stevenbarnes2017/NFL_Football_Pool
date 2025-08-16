# Football_Project/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp, ValidationError
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
    submit = SubmitField("Create account")

    # Server-side uniqueness & reserved checks (case-insensitive) — no DB changes required
    def validate_username(self, field):
        uname = field.data
        if uname.lower() in RESERVED_USERNAMES:
            raise ValidationError("That username is reserved.")
        exists = (
            db.session.query(User.id)
            .filter(func.lower(User.username) == uname.lower())
            .first()
        )
        if exists:
            raise ValidationError("That username is taken.")

    def validate_email(self, field):
        exists = (
            db.session.query(User.id)
            .filter(func.lower(User.email) == field.data.lower())
            .first()
        )
        if exists:
            raise ValidationError("An account already exists for that email.")


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
