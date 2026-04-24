"""add group_id to board_thread

Revision ID: 9349093b0ef4
Revises: 34511464c83b
Create Date: 2026-04-22 08:00:12.783237

"""
from alembic import op
import sqlalchemy as sa


revision = '9349093b0ef4'
down_revision = '34511464c83b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('board_thread', schema=None) as batch_op:
        batch_op.add_column(sa.Column('group_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_board_thread_group_id'), ['group_id'], unique=False)
        batch_op.create_foreign_key(None, 'pool_group', ['group_id'], ['id'])


def downgrade():
    with op.batch_alter_table('board_thread', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_board_thread_group_id'))
        batch_op.drop_column('group_id')