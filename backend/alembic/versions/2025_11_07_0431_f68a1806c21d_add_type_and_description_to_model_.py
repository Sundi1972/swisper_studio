"""add_type_and_description_to_model_pricing

Revision ID: f68a1806c21d
Revises: 65a68f36fae9
Create Date: 2025-11-07 04:31:52.552118+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f68a1806c21d'
down_revision: Union[str, None] = '65a68f36fae9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Delete all existing model pricing data
    op.execute("DELETE FROM model_pricing")
    
    # Add type column (nullable initially)
    op.add_column('model_pricing', sa.Column('type', sa.String(length=50), nullable=True))
    
    # Add description column (nullable)
    op.add_column('model_pricing', sa.Column('description', sa.Text(), nullable=True))
    
    # Make type NOT NULL after adding it (set default for existing rows if any)
    op.alter_column('model_pricing', 'type', nullable=False, server_default='Chat')
    
    # Remove server default after making it NOT NULL
    op.alter_column('model_pricing', 'type', server_default=None)


def downgrade() -> None:
    op.drop_column('model_pricing', 'description')
    op.drop_column('model_pricing', 'type')
