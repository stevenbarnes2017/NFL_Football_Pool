"""add email_notifications_enabled to user

Revision ID: d38b17241d81
Revises: 4f7aedb40845
Create Date: 2026-08-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd38b17241d81'
down_revision = '4f7aedb40845'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true'))
        )

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('email_notifications_enabled', server_default=None)


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('email_notifications_enabled')