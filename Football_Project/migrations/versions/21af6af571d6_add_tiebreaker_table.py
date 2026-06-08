"""add tiebreaker table

Revision ID: 21af6af571d6
Revises: 3e4aa4248eb6
Create Date: 2026-06-08 10:36:31.412607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21af6af571d6'
down_revision = '3e4aa4248eb6'
branch_labels = None
depends_on = None


def upgrade():
    # Add tiebreaker_score to pick (nullable - it's optional)
    op.add_column('pick', sa.Column('tiebreaker_score', sa.Integer(), nullable=True))
 
    # Add is_tiebreaker to game (nullable first, then backfill, then not null)
    op.add_column('game', sa.Column('is_tiebreaker', sa.Boolean(), nullable=True))
    op.execute('UPDATE game SET is_tiebreaker = false')
    op.alter_column('game', 'is_tiebreaker', nullable=False)
 
 
def downgrade():
    op.drop_column('pick', 'tiebreaker_score')
    op.drop_column('game', 'is_tiebreaker')
    # ### end Alembic commands ###
