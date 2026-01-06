"""Add season lock fields to settings

Revision ID: 8be601664434
Revises: 4bf07f95f7a2
Create Date: 2026-01-05 18:48:43.216053

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8be601664434'
down_revision = '4bf07f95f7a2'
branch_labels = None
depends_on = None


def upgrade():
    # --- Add season lock fields to settings ---
    op.add_column("settings", sa.Column("season_year", sa.Integer(), nullable=False, server_default="2025"))
    op.add_column("settings", sa.Column("season_type", sa.String(length=10), nullable=False, server_default="REG"))
    op.add_column("settings", sa.Column("season_locked", sa.Boolean(), nullable=False, server_default=sa.text("true")))

    # Remove defaults after backfill (keeps schema clean)
    op.alter_column("settings", "season_year", server_default=None)
    op.alter_column("settings", "season_type", server_default=None)
    op.alter_column("settings", "season_locked", server_default=None)

    # NOTE: We are intentionally NOT applying the detected user.password length change here.
    # We'll handle that separately if you actually want it.


def downgrade():
    op.drop_column("settings", "season_locked")
    op.drop_column("settings", "season_type")
    op.drop_column("settings", "season_year")