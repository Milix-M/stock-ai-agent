"""Change watchlist from stock_id (UUID) to stock_code (String)

Revision ID: 002
Revises: 001
Create Date: 2026-03-26 08:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing unique constraint and foreign key
    op.drop_constraint('watchlists_user_id_fkey', 'watchlists', type_='foreignkey')
    op.drop_constraint('watchlists_pkey', 'watchlists', type_='primary')

    # Add stock_code column temporarily
    op.add_column('watchlists', sa.Column('stock_code', sa.String(20), nullable=True))

    # Migrate data: copy stock.code to watchlist.stock_code
    op.execute("""
        UPDATE watchlists w
        SET stock_code = s.code
        FROM stocks s
        WHERE w.stock_id = s.id
    """)

    # Drop stock_id column
    op.drop_column('watchlists', 'stock_id')

    # Make stock_code not nullable
    op.alter_column('watchlists', 'stock_code', nullable=False)

    # Add new unique constraint on user_id + stock_code
    op.create_unique_constraint('uix_user_stock_code', 'watchlists', ['user_id', 'stock_code'])


def downgrade() -> None:
    # For rollback: recreate stock_id and restore foreign key
    op.add_column(
        'watchlists',
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stocks.id'), nullable=True)
    )

    # Migrate back: find stock.id from stock.code
    op.execute("""
        UPDATE watchlists w
        SET stock_id = s.id
        FROM stocks s
        WHERE w.stock_code = s.code
    """)

    # Drop stock_code column
    op.drop_column('watchlists', 'stock_code')

    # Make stock_id not nullable
    op.alter_column('watchlists', 'stock_id', nullable=False)

    # Drop unique constraint
    op.drop_constraint('uix_user_stock_code', 'watchlists', type_='unique')
