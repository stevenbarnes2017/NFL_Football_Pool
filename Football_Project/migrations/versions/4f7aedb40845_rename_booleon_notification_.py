"""rename booleon notification_subscription to notification_enabled in user table

Revision ID: 4f7aedb40845
Revises: 2c6801e15571
Create Date: 2026-07-23 01:26:42.726830

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f7aedb40845'
down_revision = '2c6801e15571'
branch_labels = None
depends_on = None

def upgrade():
    # Add the unique constraint
    with op.batch_alter_table('notification_subscription', schema=None) as batch_op:
        batch_op.create_unique_constraint(
            'uq_user_notification_endpoint',
            ['user_id', 'endpoint']
        )

    # Add the new column with a server default so existing rows get False
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'notification_enabled',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('false')
            )
        )

    # Remove the server default so future inserts use the SQLAlchemy model default
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(
            'notification_enabled',
            server_default=None
        )