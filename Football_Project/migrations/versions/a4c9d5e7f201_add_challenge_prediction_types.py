"""add challenge prediction types

Revision ID: a4c9d5e7f201
Revises: b4d8e2a19f6c
Create Date: 2026-09-08
"""

from alembic import op
import sqlalchemy as sa


revision = "a4c9d5e7f201"
down_revision = "b4d8e2a19f6c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "challenge",
        sa.Column("challenge_type", sa.String(length=20), nullable=False, server_default="winner"),
    )
    op.add_column("challenge_game", sa.Column("over_under_line", sa.Float(), nullable=True))
    op.alter_column("challenge_pick", "team_picked", existing_type=sa.String(length=50), nullable=True)
    op.add_column("challenge_pick", sa.Column("predicted_home_score", sa.Integer(), nullable=True))
    op.add_column("challenge_pick", sa.Column("predicted_away_score", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("challenge_pick", "predicted_away_score")
    op.drop_column("challenge_pick", "predicted_home_score")
    op.alter_column("challenge_pick", "team_picked", existing_type=sa.String(length=50), nullable=False)
    op.drop_column("challenge_game", "over_under_line")
    op.drop_column("challenge", "challenge_type")
