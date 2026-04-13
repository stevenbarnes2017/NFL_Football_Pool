"""add multigroup foundation

Revision ID: c5256fd7a465
Revises: 94d2f735e51c
Create Date: 2026-04-13 11:04:12.400678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c5256fd7a465"
down_revision = "94d2f735e51c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pool_group",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "group_member",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["pool_group.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "user_id", name="uq_group_member_group_user"),
    )

    with op.batch_alter_table("group_member", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_group_member_group_id"), ["group_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_group_member_user_id"), ["user_id"], unique=False)

    with op.batch_alter_table("pick", schema=None) as batch_op:
        batch_op.add_column(sa.Column("group_id", sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f("ix_pick_group_id"), ["group_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_pick_group_id_pool_group",
            "pool_group",
            ["group_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("pick", schema=None) as batch_op:
        batch_op.drop_constraint("fk_pick_group_id_pool_group", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_pick_group_id"))
        batch_op.drop_column("group_id")

    with op.batch_alter_table("group_member", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_group_member_user_id"))
        batch_op.drop_index(batch_op.f("ix_group_member_group_id"))

    op.drop_table("group_member")
    op.drop_table("pool_group")