"""add_users_and_auth

Revision ID: 1b23175c5a26
Revises: 130a927e2862
Create Date: 2025-11-03 06:33:38.042687+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '1b23175c5a26'
down_revision: Union[str, None] = '130a927e2862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add user authentication system:
    1. Create users table with roles
    2. Add github_repo_url to projects
    3. Add owner_id foreign key to projects
    4. Add created_by_user_id to config_versions
    5. Add deployed_by_user_id to config_deployments
    6. Add foreign key on traces.user_id → users.id
    7. Create default admin user
    """
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='viewer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    
    # 2. Add github_repo_url to projects
    op.add_column('projects', sa.Column('github_repo_url', sa.String(length=500), nullable=True))
    
    # 3. Add owner_id to projects (nullable for now, will backfill)
    op.add_column('projects', sa.Column('owner_id', sa.String(length=36), nullable=True))
    
    # 4. Add created_by_user_id to config_versions (if table exists)
    # Skip for now - config tables will be created with user references later
    # op.add_column('config_versions', sa.Column('created_by_user_id', sa.String(length=36), nullable=True))
    
    # 5. Add deployed_by_user_id to config_deployments (if table exists)
    # Skip for now - config tables will be created with user references later
    # op.add_column('config_deployments', sa.Column('deployed_by_user_id', sa.String(length=36), nullable=True))
    
    # 6. Create default admin user (password: admin123 - MUST change after first login!)
    # Pre-generated bcrypt hash for "admin123" with cost factor 12
    # Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOVDBQYnBPmR3JRMYBqHQTMfzJ8LqCT5u
    op.execute("""
        INSERT INTO users (id, email, password_hash, name, role, is_active, created_at, updated_at)
        VALUES (
            'admin-user-uuid-0000-000000000001',
            'admin@swisperstudio.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOVDBQYnBPmR3JRMYBqHQTMfzJ8LqCT5u',
            'System Administrator',
            'admin',
            true,
            now(),
            now()
        )
    """)
    
    # 7. Backfill existing projects with admin user as owner
    op.execute("""
        UPDATE projects 
        SET owner_id = 'admin-user-uuid-0000-000000000001'
        WHERE owner_id IS NULL
    """)
    
    # 8. Add foreign key constraints (after backfill)
    op.create_foreign_key('fk_projects_owner', 'projects', 'users', ['owner_id'], ['id'])
    # Config table foreign keys skipped - will be added when config tables are created
    # op.create_foreign_key('fk_config_versions_user', 'config_versions', 'users', ['created_by_user_id'], ['id'])
    # op.create_foreign_key('fk_config_deployments_user', 'config_deployments', 'users', ['deployed_by_user_id'], ['id'])
    
    # 9. Clean up invalid user_id values in traces (set to NULL if user doesn't exist)
    op.execute("""
        UPDATE traces
        SET user_id = NULL
        WHERE user_id IS NOT NULL
        AND user_id NOT IN (SELECT id FROM users)
    """)
    
    # 10. Add foreign key on traces.user_id (if column exists)
    # Note: traces.user_id already exists as string, just add FK constraint
    op.create_foreign_key('fk_traces_user', 'traces', 'users', ['user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    """Rollback authentication changes"""
    # Remove foreign keys
    op.drop_constraint('fk_traces_user', 'traces', type_='foreignkey')
    # Config FKs skipped - not created
    # op.drop_constraint('fk_config_deployments_user', 'config_deployments', type_='foreignkey')
    # op.drop_constraint('fk_config_versions_user', 'config_versions', type_='foreignkey')
    op.drop_constraint('fk_projects_owner', 'projects', type_='foreignkey')
    
    # Remove columns
    # Config columns skipped - not created
    # op.drop_column('config_deployments', 'deployed_by_user_id')
    # op.drop_column('config_versions', 'created_by_user_id')
    op.drop_column('projects', 'owner_id')
    op.drop_column('projects', 'github_repo_url')
    
    # Drop users table
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
