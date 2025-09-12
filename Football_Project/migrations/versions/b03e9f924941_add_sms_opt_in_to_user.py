"""add sms_opt_in to User

Revision ID: b03e9f924941
Revises: 6e89de7c8fb7
Create Date: 2025-09-11 22:30:55.526741
"""
from alembic import op
import sqlalchemy as sa

revision = 'b03e9f924941'
down_revision = '6e89de7c8fb7'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('sms_opt_in', sa.Boolean(), nullable=False, server_default=sa.text('false'))
        )
    # (Optionally drop server default—see note above)

def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('sms_opt_in')
