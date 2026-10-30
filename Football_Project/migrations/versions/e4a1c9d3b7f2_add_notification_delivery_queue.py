"""add notification delivery queue

Revision ID: e4a1c9d3b7f2
Revises: d2b7e4c1a9f3
Create Date: 2026-10-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4a1c9d3b7f2'
down_revision = 'd2b7e4c1a9f3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notification_delivery',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notification_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=10), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=12), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('next_attempt_at', sa.DateTime(), nullable=False),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.String(length=300), nullable=True),
        sa.Column('email_subject', sa.String(length=300), nullable=True),
        sa.Column('email_html', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['notification_id'], ['notification.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['notification_subscription.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('notification_id', 'channel', 'subscription_id', name='uq_notification_delivery_target'),
    )
    op.create_index(op.f('ix_notification_delivery_notification_id'), 'notification_delivery', ['notification_id'], unique=False)
    op.create_index('ix_notification_delivery_due', 'notification_delivery', ['status', 'next_attempt_at'], unique=False)


def downgrade():
    op.drop_index('ix_notification_delivery_due', table_name='notification_delivery')
    op.drop_index(op.f('ix_notification_delivery_notification_id'), table_name='notification_delivery')
    op.drop_table('notification_delivery')
