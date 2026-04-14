"""make pick group_id not null

Revision ID: d51906b73d7c
Revises: eae5098b8737
"""

from alembic import op
import sqlalchemy as sa

revision = "d51906b73d7c"
down_revision = "eae5098b8737"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("pick", schema=None) as batch_op:
        batch_op.alter_column(
            "group_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade():
    with op.batch_alter_table("pick", schema=None) as batch_op:
        batch_op.alter_column(
            "group_id",
            existing_type=sa.Integer(),
            nullable=True,
        )