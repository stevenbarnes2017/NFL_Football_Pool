"""add weekly recap table

Revision ID: c7e1f3a9b2d4
Revises: b4d8e2a19f6c
Create Date: 2026-10-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7e1f3a9b2d4'
down_revision = 'b4d8e2a19f6c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'weekly_recap',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('season_year', sa.Integer(), nullable=False),
        sa.Column('season_type', sa.String(length=10), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('headline', sa.String(length=200), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['pool_group.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'group_id', 'season_year', 'season_type', 'week',
            name='uq_weekly_recap_group_season_week',
        ),
    )


def downgrade():
    op.drop_table('weekly_recap')
