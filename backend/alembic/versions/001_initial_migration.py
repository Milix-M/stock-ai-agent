"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-03-16 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Stocks table
    op.create_table(
        'stocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('code', sa.String(20), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('market', sa.String(50), nullable=True),
        sa.Column('sector', sa.String(100), nullable=True),
        sa.Column('per', sa.Numeric(10, 2), nullable=True),
        sa.Column('pbr', sa.Numeric(10, 2), nullable=True),
        sa.Column('dividend_yield', sa.Numeric(5, 2), nullable=True),
        sa.Column('market_cap', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Investment patterns table
    op.create_table(
        'investment_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('raw_input', sa.Text(), nullable=False),
        sa.Column('parsed_filters', postgresql.JSONB(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Stock prices table (TimescaleDB hypertable)
    op.create_table(
        'stock_prices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stocks.id'), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('open', sa.Numeric(15, 2), nullable=True),
        sa.Column('high', sa.Numeric(15, 2), nullable=True),
        sa.Column('low', sa.Numeric(15, 2), nullable=True),
        sa.Column('close', sa.Numeric(15, 2), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('adjusted_close', sa.Numeric(15, 2), nullable=True),
    )
    
    # Convert to hypertable
    op.execute("SELECT create_hypertable('stock_prices', 'date', if_not_exists => TRUE)")
    
    # Watchlists table
    op.create_table(
        'watchlists',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stocks.id'), nullable=False),
        sa.Column('alert_threshold', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Push subscriptions table
    op.create_table(
        'push_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('endpoint', sa.Text(), unique=True, nullable=False),
        sa.Column('p256dh', sa.Text(), nullable=False),
        sa.Column('auth', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('push_subscriptions')
    op.drop_table('watchlists')
    op.drop_table('stock_prices')
    op.drop_table('investment_patterns')
    op.drop_table('stocks')
    op.drop_table('users')
