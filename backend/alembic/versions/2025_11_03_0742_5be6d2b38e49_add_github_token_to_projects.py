"""add_github_token_to_projects

Revision ID: 5be6d2b38e49
Revises: 1b23175c5a26
Create Date: 2025-11-03 07:42:40.899763+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5be6d2b38e49'
down_revision: Union[str, None] = '1b23175c5a26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add github_token column to projects table"""
    op.add_column('projects', sa.Column('github_token', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove github_token column from projects table"""
    op.drop_column('projects', 'github_token')
