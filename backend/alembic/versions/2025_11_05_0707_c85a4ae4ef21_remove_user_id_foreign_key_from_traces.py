"""remove_user_id_foreign_key_from_traces

Revision ID: c85a4ae4ef21
Revises: 5be6d2b38e49
Create Date: 2025-11-05 07:07:03.253782+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c85a4ae4ef21'
down_revision: Union[str, None] = '5be6d2b38e49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove foreign key constraint on traces.user_id to allow external user IDs.
    
    SwisperStudio is an observability platform for external systems.
    External systems (like Swisper) have their own user databases.
    user_id should be treated as an external identifier, not a database FK.
    
    This fix unblocks Swisper integration (Phase 5.1).
    """
    # Drop foreign key constraint if it exists
    op.drop_constraint('fk_traces_user', 'traces', type_='foreignkey')
    
    # Make user_id nullable (optional field)
    op.alter_column('traces', 'user_id',
                    existing_type=sa.String(),
                    nullable=True)
    
    # Add index for performance (still want to filter by user_id)
    op.create_index('idx_traces_user_id', 'traces', ['user_id'], unique=False)


def downgrade() -> None:
    """
    Restore foreign key constraint (not recommended for production).
    
    Warning: This will fail if traces exist with user_ids not in users table.
    """
    # Drop index
    op.drop_index('idx_traces_user_id', table_name='traces')
    
    # Make user_id non-nullable
    op.alter_column('traces', 'user_id',
                    existing_type=sa.String(),
                    nullable=False)
    
    # Restore foreign key constraint
    op.create_foreign_key('fk_traces_user', 'traces', 'users',
                         ['user_id'], ['id'])
