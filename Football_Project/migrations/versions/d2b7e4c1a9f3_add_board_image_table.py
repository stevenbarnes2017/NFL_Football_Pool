"""add board image table

Revision ID: d2b7e4c1a9f3
Revises: c7e1f3a9b2d4
Create Date: 2026-10-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2b7e4c1a9f3'
down_revision = 'c7e1f3a9b2d4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'board_image',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=32), nullable=False),
        sa.Column('uploader_user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.String(length=30), nullable=False),
        sa.Column('byte_size', sa.Integer(), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['uploader_user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['pool_group.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_board_image_token'), 'board_image', ['token'], unique=True)
    op.create_index(op.f('ix_board_image_group_id'), 'board_image', ['group_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_board_image_group_id'), table_name='board_image')
    op.drop_index(op.f('ix_board_image_token'), table_name='board_image')
    op.drop_table('board_image')
