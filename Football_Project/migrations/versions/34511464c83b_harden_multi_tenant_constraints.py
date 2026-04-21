"""harden multi tenant constraints

Revision ID: 34511464c83b
Revises: ef6a1cfab270
Create Date: 2026-04-20 07:56:13.574809
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "34511464c83b"
down_revision = "ef6a1cfab270"
branch_labels = None
depends_on = None


def upgrade():
    # group_member
    # If the old unique constraint already exists and is correct, replace it with the new name.
    with op.batch_alter_table("group_member", schema=None) as batch_op:
        batch_op.drop_constraint("uq_group_member_group_user", type_="unique")
        batch_op.create_unique_constraint(
            "uq_group_member_user_group",
            ["user_id", "group_id"],
        )

    # pick
    with op.batch_alter_table("pick", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_pick_user_game_group",
            ["user_id", "game_id", "group_id"],
        )

    # user_score
    with op.batch_alter_table("user_score", schema=None) as batch_op:
        batch_op.alter_column(
            "score",
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            type_=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "group_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_unique_constraint(
            "uq_user_score_user_week_season_group",
            ["user_id", "week", "season_year", "season_type", "group_id"],
        )


def downgrade():
    with op.batch_alter_table("user_score", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_user_score_user_week_season_group",
            type_="unique",
        )
        batch_op.alter_column(
            "group_id",
            existing_type=sa.Integer(),
            nullable=True,
        )
        batch_op.alter_column(
            "score",
            existing_type=sa.Integer(),
            type_=sa.DOUBLE_PRECISION(precision=53),
            existing_nullable=False,
        )

    with op.batch_alter_table("pick", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_pick_user_game_group",
            type_="unique",
        )

    with op.batch_alter_table("group_member", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_group_member_user_group",
            type_="unique",
        )
        batch_op.create_unique_constraint(
            "uq_group_member_group_user",
            ["group_id", "user_id"],
        )