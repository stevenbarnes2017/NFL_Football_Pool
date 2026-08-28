from .extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
from sqlalchemy import DateTime
from zoneinfo import ZoneInfo
from werkzeug.security import generate_password_hash, check_password_hash
# ----------------------------
# Group Model
# ----------------------------
class PoolGroup(db.Model):
    __tablename__ = "pool_group"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    members = db.relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    picks = db.relationship("Pick", back_populates="group")
    scores = db.relationship("UserScore", back_populates="group", cascade="all, delete-orphan")

class GroupMember(db.Model):
    __tablename__ = "group_member"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("pool_group.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    group = db.relationship("PoolGroup", back_populates="members")
    user = db.relationship("User", back_populates="group_memberships")

    __table_args__ = (
        db.UniqueConstraint("user_id", "group_id", name="uq_group_member_user_group"),
    )
# ----------------------------
# User Model
# ----------------------------
PREFERRED_PWHASH = "pbkdf2:sha256:50000"  # Standardize password hashing


class JobRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(50), nullable=False, index=True)
    ran_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ok = db.Column(db.Boolean, default=True, nullable=False)

    inserted = db.Column(db.Integer, default=0)
    updated = db.Column(db.Integer, default=0)
    unchanged = db.Column(db.Integer, default=0)
    failed_weeks = db.Column(db.Integer, default=0)

    message = db.Column(db.String(255), nullable=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    full_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(20))
    favorite_team = db.Column(db.String(50))
    password = db.Column(db.String(255), nullable=False)  # 255 is safe for hashes
    is_admin = db.Column(db.Boolean, default=False)
    sms_opt_in = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    email_notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)
    notification_enabled = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # Remove the duplicated relationship; you had 'scores' twice
    picks = db.relationship('Pick', backref='user', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship(
        "UserScore",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    group_memberships = db.relationship(
        "GroupMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    notification_subscriptions = db.relationship(
        "NotificationSubscription",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def set_password(self, plaintext: str) -> None:
        # Standardize what we write going forward (consistent format)
        self.password = generate_password_hash(plaintext, method=PREFERRED_PWHASH)

    def check_password(self, plaintext: str) -> bool:
        return check_password_hash(self.password, plaintext)

    def is_password_hashed(self) -> bool:
        """Optional helper; detect if the stored value looks like a hash."""
        try:
            # If this doesn't raise, it's a supported hash string
            check_password_hash(self.password, "x")
            return True
        except Exception:
            return False
# ----------------------------
# Pick Model
# ----------------------------
class Pick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    team_picked = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Integer, nullable=True)
    pick_time = db.Column(db.DateTime, default=datetime.utcnow)
    week = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    is_overridden = db.Column(db.Boolean, default=False)
    tiebreaker_score = db.Column(db.Integer, nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("pool_group.id"), nullable=False)
    group = db.relationship("PoolGroup", back_populates="picks")

    __table_args__ = (
        db.UniqueConstraint("user_id", "game_id", "group_id", name="uq_pick_user_game_group"),
    )

    # ✅ ADD THIS:
    #user = db.relationship('User', backref='picks', lazy=True)

    def __repr__(self):
        return f'<Pick {self.id} - User {self.user_id} - Game {self.game_id} - Team {self.team_picked}>'


# ----------------------------
# Settings Model
# ----------------------------
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_week = db.Column(db.Integer, nullable=False)

    season_year = db.Column(db.Integer, nullable=False, default=2026)
    season_type = db.Column(db.String(10), nullable=False, default="REG")  # REG / POST
    season_locked = db.Column(db.Boolean, nullable=False, default=True)


# ----------------------------
# Game Model (now linked to Schedule)
# ----------------------------
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # ESPN event id (global unique)
    game_id = db.Column(db.String(50), unique=True, nullable=False)

    # Season context
    season_year = db.Column(db.Integer, nullable=False)
    season_type = db.Column(db.String(20), nullable=False)  
    # preseason | regular | postseason

    week = db.Column(db.Integer, nullable=True)
    week_label = db.Column(db.String(10), nullable=True)

    home_team = db.Column(db.String(50), nullable=False)
    away_team = db.Column(db.String(50), nullable=False)

    spread = db.Column(db.Float, nullable=True)
    favorite_team = db.Column(db.String(50), nullable=True)

    commence_time_mt = db.Column(DateTime(timezone=True), nullable=True)

    home_team_score = db.Column(db.Integer, nullable=True)
    away_team_score = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=True)

    is_tiebreaker = db.Column(db.Boolean, nullable=False, default=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    picks = db.relationship('Pick', backref='game', lazy=True)

# ----------------------------
# UserScore Model
# ----------------------------
class UserScore(db.Model):
    __tablename__ = "user_score"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    week = db.Column(db.Integer, nullable=False)
    season_year = db.Column(db.Integer, nullable=False)
    season_type = db.Column(db.String(10), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    group_id = db.Column(db.Integer, db.ForeignKey("pool_group.id"), nullable=False, index=True)

    user = db.relationship("User", back_populates="scores")
    group = db.relationship("PoolGroup", back_populates="scores")

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "week",
            "season_year",
            "season_type",
            "group_id",
            name="uq_user_score_user_week_season_group",
        ),
    )
#------------------------------
# Announcements and Message Board
#------------------------------

class Announcement(db.Model):
    __tablename__ = "announcement"
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(140), nullable=False)
    body = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Optional season context (recommended so you can show “Postseason Week 1”)
    season_year = db.Column(db.Integer, nullable=True)
    season_type = db.Column(db.String(20), nullable=True)  # "PRE"/"REG"/"POST"
    week = db.Column(db.Integer, nullable=True)

    pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_by = db.relationship("User", backref=db.backref("announcements", lazy=True))

class BoardThread(db.Model):
    __tablename__ = "board_thread"
    id = db.Column(db.Integer, primary_key=True)

    group_id = db.Column(db.Integer, db.ForeignKey("pool_group.id"), nullable=True, index=True)

    title = db.Column(db.String(180), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    season_year = db.Column(db.Integer, nullable=True)
    season_type = db.Column(db.String(20), nullable=True)
    week = db.Column(db.Integer, nullable=True)

    pinned = db.Column(db.Boolean, default=False, nullable=False)
    locked = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    last_activity_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    created_by = db.relationship("User", backref=db.backref("board_threads", lazy=True))
    group = db.relationship("PoolGroup", backref=db.backref("board_threads", lazy=True))

class BoardPost(db.Model):
    __tablename__ = "board_post"
    id = db.Column(db.Integer, primary_key=True)

    thread_id = db.Column(db.Integer, db.ForeignKey("board_thread.id"), nullable=False)
    author_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False) # soft delete
    edited_at = db.Column(db.DateTime, nullable=True)

    thread = db.relationship("BoardThread", backref=db.backref("posts", lazy=True, order_by="BoardPost.created_at"))
    author = db.relationship("User", backref=db.backref("board_posts", lazy=True))

class GroupInvite(db.Model):
    __tablename__ = "group_invite"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("pool_group.id"), nullable=False, index=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    group = db.relationship("PoolGroup", backref=db.backref("invites", lazy=True))
    created_by = db.relationship("User", backref=db.backref("created_invites", lazy=True))

class ReminderJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    group_id = db.Column(db.Integer, db.ForeignKey("pool_group.id"), nullable=False)
    season_year = db.Column(db.Integer, nullable=False)
    season_type = db.Column(db.String(10), nullable=False)
    week = db.Column(db.Integer, nullable=False)

    reminder_type = db.Column(db.String(50), nullable=False)
    channel = db.Column(db.String(20), nullable=False)  # email, sms
    scheduled_for = db.Column(db.DateTime(timezone=True), nullable=False)

    sent_at = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.String(20), default="pending")  # pending, sent, skipped, failed
    details = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint(
            "group_id",
            "season_year",
            "season_type",
            "week",
            "reminder_type",
            "channel",
            name="uq_reminder_once"
        ),
    )

class NotificationSubscription(db.Model):
    __tablename__ = "notification_subscription"

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "endpoint",
            name="uq_user_notification_endpoint",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True,
    )

    endpoint = db.Column(db.Text, nullable=False)

    p256dh = db.Column(db.Text, nullable=False)

    auth = db.Column(db.Text, nullable=False)

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    browser = db.Column(db.String(50))

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    last_used = db.Column(db.DateTime)

    user = db.relationship(
        "User",
        back_populates="notification_subscriptions",
    )

    def __repr__(self):
        return f"<NotificationSubscription user={self.user_id} active={self.active}>"


# ----------------------------
# Challenge Models
# ----------------------------
class Challenge(db.Model):
    __tablename__ = "challenge"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("pool_group.id", ondelete="RESTRICT"),
        nullable=False,
    )
    creator_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=True)
    season_year = db.Column(db.Integer, nullable=False)
    season_type = db.Column(db.String(10), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    cancelled_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    group = db.relationship(
        "PoolGroup",
        backref=db.backref("challenges", lazy=True),
    )
    creator = db.relationship(
        "User",
        foreign_keys=[creator_user_id],
        backref=db.backref("created_challenges", lazy=True),
    )
    cancelled_by = db.relationship(
        "User",
        foreign_keys=[cancelled_by_user_id],
        backref=db.backref("cancelled_challenges", lazy=True),
    )
    participants = db.relationship(
        "ChallengeParticipant",
        back_populates="challenge",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    challenge_games = db.relationship(
        "ChallengeGame",
        back_populates="challenge",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    picks = db.relationship(
        "ChallengePick",
        back_populates="challenge",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        db.Index("ix_challenge_group_created", "group_id", "created_at"),
        db.Index(
            "ix_challenge_season_week",
            "season_year",
            "season_type",
            "week",
        ),
        db.Index("ix_challenge_creator_user", "creator_user_id"),
    )


class ChallengeParticipant(db.Model):
    __tablename__ = "challenge_participant"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenge.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=False,
    )
    added_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    challenge = db.relationship("Challenge", back_populates="participants")
    user = db.relationship(
        "User",
        backref=db.backref("challenge_participations", lazy=True),
    )
    picks = db.relationship(
        "ChallengePick",
        back_populates="participant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        db.UniqueConstraint(
            "challenge_id",
            "user_id",
            name="uq_challenge_participant_challenge_user",
        ),
        db.Index(
            "ix_challenge_participant_user_challenge",
            "user_id",
            "challenge_id",
        ),
    )


class ChallengeGame(db.Model):
    __tablename__ = "challenge_game"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenge.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id = db.Column(
        db.Integer,
        db.ForeignKey("game.id", ondelete="RESTRICT"),
        nullable=False,
    )
    display_order = db.Column(db.Integer, nullable=False)
    added_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    challenge = db.relationship("Challenge", back_populates="challenge_games")
    game = db.relationship(
        "Game",
        backref=db.backref("challenge_games", lazy=True),
    )
    picks = db.relationship(
        "ChallengePick",
        back_populates="challenge_game",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        db.UniqueConstraint(
            "challenge_id",
            "game_id",
            name="uq_challenge_game_challenge_game",
        ),
        db.UniqueConstraint(
            "challenge_id",
            "display_order",
            name="uq_challenge_game_challenge_display_order",
        ),
        db.Index("ix_challenge_game_game", "game_id"),
    )


class ChallengePick(db.Model):
    __tablename__ = "challenge_pick"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenge.id", ondelete="CASCADE"),
        nullable=False,
    )
    participant_id = db.Column(
        db.Integer,
        db.ForeignKey("challenge_participant.id", ondelete="CASCADE"),
        nullable=False,
    )
    challenge_game_id = db.Column(
        db.Integer,
        db.ForeignKey("challenge_game.id", ondelete="CASCADE"),
        nullable=False,
    )
    team_picked = db.Column(db.String(50), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    challenge = db.relationship("Challenge", back_populates="picks")
    participant = db.relationship("ChallengeParticipant", back_populates="picks")
    challenge_game = db.relationship("ChallengeGame", back_populates="picks")

    __table_args__ = (
        db.UniqueConstraint(
            "participant_id",
            "challenge_game_id",
            name="uq_challenge_pick_participant_game",
        ),
    )
