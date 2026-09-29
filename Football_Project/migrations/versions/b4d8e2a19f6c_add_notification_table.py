"""add notification table

Revision ID: b4d8e2a19f6c
Revises: f8c3a1d5e7b2
Create Date: 2026-09-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4d8e2a19f6c'
down_revision = 'f8c3a1d5e7b2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=30), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('body', sa.String(length=500), nullable=True),
        sa.Column('url', sa.String(length=300), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('related_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('push_sent_at', sa.DateTime(), nullable=True),
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['pool_group.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_notification_user_type_read', 'notification', ['user_id', 'type', 'read_at'], unique=False)
    op.create_index(op.f('ix_notification_type'), 'notification', ['type'], unique=False)
    op.create_index(op.f('ix_notification_user_id'), 'notification', ['user_id'], unique=False)
    op.create_index(op.f('ix_notification_created_at'), 'notification', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notification_created_at'), table_name='notification')
    op.drop_index(op.f('ix_notification_user_id'), table_name='notification')
    op.drop_index(op.f('ix_notification_type'), table_name='notification')
    op.drop_index('ix_notification_user_type_read', table_name='notification')
    op.drop_table('notification')
