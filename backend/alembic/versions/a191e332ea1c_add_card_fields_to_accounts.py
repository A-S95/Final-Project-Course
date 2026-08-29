"""add card expiration/plafond fields to accounts

Revision ID: a191e332ea1c
Revises: 268124a9d9c3
Create Date: 2026-08-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a191e332ea1c'
down_revision: Union[str, Sequence[str], None] = '268124a9d9c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ambos opcionais (NULL por omissão): nem toda a conta é um cartão, e
    # mesmo as que são podem não ter estes dados preenchidos ainda.
    op.add_column('accounts', sa.Column('card_expiration_date', sa.Date(), nullable=True))
    op.add_column(
        'accounts', sa.Column('card_plafond', sa.Numeric(precision=12, scale=2), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('accounts', 'card_plafond')
    op.drop_column('accounts', 'card_expiration_date')
