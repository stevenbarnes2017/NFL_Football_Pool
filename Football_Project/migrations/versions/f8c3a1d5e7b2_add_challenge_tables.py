"""add challenge tables

Revision ID: f8c3a1d5e7b2
Revises: d38b17241d81
Create Date: 2026-08-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f8c3a1d5e7b2"
down_revision = "d38b17241d81"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "challenge",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("creator_user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("season_type", sa.String(length=10), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["cancelled_by_user_id"],
            ["user.id"],
            name="fk_challenge_cancelled_by_user",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["creator_user_id"],
            ["user.id"],
            name="fk_challenge_creator_user",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["pool_group.id"],
            name="fk_challenge_group",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_challenge"),
    )
    op.create_index(
        "ix_challenge_group_created",
        "challenge",
        ["group_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_challenge_season_week",
        "challenge",
        ["season_year", "season_type", "week"],
        unique=False,
    )
    op.create_index(
        "ix_challenge_creator_user",
        "challenge",
        ["creator_user_id"],
        unique=False,
    )

    op.create_table(
        "challenge_participant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenge.id"],
            name="fk_challenge_participant_challenge",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_challenge_participant_user",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_challenge_participant"),
        sa.UniqueConstraint(
            "challenge_id",
            "user_id",
            name="uq_challenge_participant_challenge_user",
        ),
    )
    op.create_index(
        "ix_challenge_participant_user_challenge",
        "challenge_participant",
        ["user_id", "challenge_id"],
        unique=False,
    )

    op.create_table(
        "challenge_game",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenge.id"],
            name="fk_challenge_game_challenge",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["game_id"],
            ["game.id"],
            name="fk_challenge_game_game",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_challenge_game"),
        sa.UniqueConstraint(
            "challenge_id",
            "display_order",
            name="uq_challenge_game_challenge_display_order",
        ),
        sa.UniqueConstraint(
            "challenge_id",
            "game_id",
            name="uq_challenge_game_challenge_game",
        ),
    )
    op.create_index(
        "ix_challenge_game_game",
        "challenge_game",
        ["game_id"],
        unique=False,
    )

    op.create_table(
        "challenge_pick",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("challenge_game_id", sa.Integer(), nullable=False),
        sa.Column("team_picked", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["challenge_game_id"],
            ["challenge_game.id"],
            name="fk_challenge_pick_challenge_game",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenge.id"],
            name="fk_challenge_pick_challenge",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["challenge_participant.id"],
            name="fk_challenge_pick_participant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_challenge_pick"),
        sa.UniqueConstraint(
            "participant_id",
            "challenge_game_id",
            name="uq_challenge_pick_participant_game",
        ),
    )


def downgrade():
    op.drop_table("challenge_pick")

    op.drop_index("ix_challenge_game_game", table_name="challenge_game")
    op.drop_table("challenge_game")

    op.drop_index(
        "ix_challenge_participant_user_challenge",
        table_name="challenge_participant",
    )
    op.drop_table("challenge_participant")

    op.drop_index("ix_challenge_creator_user", table_name="challenge")
    op.drop_index("ix_challenge_season_week", table_name="challenge")
    op.drop_index("ix_challenge_group_created", table_name="challenge")
    op.drop_table("challenge")
