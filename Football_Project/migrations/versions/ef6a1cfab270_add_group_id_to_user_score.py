"""add group_id to user_score

Revision ID: ef6a1cfab270
Revises: d51906b73d7c
"""

from alembic import op
import sqlalchemy as sa


revision = "ef6a1cfab270"
down_revision = "d51906b73d7c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user_score", schema=None) as batch_op:
        batch_op.add_column(sa.Column("group_id", sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f("ix_user_score_group_id"), ["group_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_user_score_group_id_pool_group",
            "pool_group",
            ["group_id"],
            ["id"],
        )

    conn = op.get_bind()

    conn.execute(sa.text("""
        UPDATE user_score
        SET group_id = pg.id
        FROM pool_group pg
        WHERE pg.slug = :slug
          AND user_score.group_id IS NULL
    """), {"slug": "main-pool"})

    with op.batch_alter_table("user_score", schema=None) as batch_op:
        batch_op.alter_column(
            "group_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade():
    with op.batch_alter_table("user_score", schema=None) as batch_op:
        batch_op.alter_column(
            "group_id",
            existing_type=sa.Integer(),
            nullable=True,
        )
        batch_op.drop_constraint("fk_user_score_group_id_pool_group", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_user_score_group_id"))
        batch_op.drop_column("group_id")