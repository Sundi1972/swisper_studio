"""add_tracing_enabled_to_projects

Revision ID: 65a68f36fae9
Revises: add_kvant_pricing_chf
Create Date: 2025-11-06 14:38:44.140709+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '65a68f36fae9'
down_revision: Union[str, None] = 'add_kvant_pricing_chf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add tracing_enabled column to projects table (default: true)
    op.add_column('projects', sa.Column('tracing_enabled', sa.Boolean(), nullable=False, server_default='true'))
    
    # Add index for fast filtering
    op.create_index('ix_projects_tracing_enabled', 'projects', ['tracing_enabled'])


def downgrade() -> None:
    # Remove index and column
    op.drop_index('ix_projects_tracing_enabled', table_name='projects')
    op.drop_column('projects', 'tracing_enabled')
