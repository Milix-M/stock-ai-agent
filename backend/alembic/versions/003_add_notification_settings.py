"""Add notification settings table

Revision ID: 003
Revises: 002
Create Date: 2026-03-27 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.has_table(conn, 'notification_settings'):
        return
    op.create_table(
        'notification_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('recommend_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('recommend_min_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('price_alert_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('price_alert_threshold', sa.Numeric(5, 2), nullable=True),
        sa.Column('volume_surge_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('volume_surge_multiplier', sa.Numeric(5, 2), nullable=True),
        sa.Column('daily_report_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('push_subscription', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('notification_settings')
