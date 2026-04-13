"""add season fields to userscore

Revision ID: 94d2f735e51c
Revises: e5ec80ea09b1
Create Date: 2026-01-12 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "94d2f735e51c"
down_revision = "e5ec80ea09b1"
branch_labels = None
depends_on = None

def upgrade():
    # 1) add as nullable first
    with op.batch_alter_table("user_score") as batch_op:
        batch_op.add_column(sa.Column("season_year", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("season_type", sa.String(length=10), nullable=True))

    # 2) backfill existing rows (choose defaults that match your existing data)
    op.execute("UPDATE user_score SET season_year = 2025 WHERE season_year IS NULL")
    op.execute("UPDATE user_score SET season_type = 'REG' WHERE season_type IS NULL")

    # 3) enforce NOT NULL after backfill
    with op.batch_alter_table("user_score") as batch_op:
        batch_op.alter_column("season_year", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("season_type", existing_type=sa.String(length=10), nullable=False)

def downgrade():
    with op.batch_alter_table("user_score") as batch_op:
        batch_op.drop_column("season_type")
        batch_op.drop_column("season_year")
