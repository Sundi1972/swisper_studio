"""Phase 2: Extend observations and add model pricing

Revision ID: 1a2b3c4d5e6f
Revises: 8b62cb96a693
Create Date: 2025-11-02 14:42:00.000000

This migration adds Phase 2 "Rich Tracing" features:
1. Extended observation fields for LLM telemetry (completion_start_time, total_tokens, cost breakdown, model_parameters)
2. New model_pricing table for project-level pricing configuration
3. Additional indexes for cost and model filtering

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, None] = '8b62cb96a693'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Phase 2 fields and tables."""
    
    # Create model_pricing table
    op.create_table(
        'model_pricing',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('hosting_provider', sa.String(length=100), nullable=False),
        sa.Column('model_name', sa.String(length=200), nullable=False),
        sa.Column('input_price_per_million', sa.Numeric(), nullable=False),
        sa.Column('output_price_per_million', sa.Numeric(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'project_id', 
            'hosting_provider', 
            'model_name',
            name='uq_model_pricing_project_provider_model'
        )
    )
    op.create_index('ix_model_pricing_lookup', 'model_pricing', ['project_id', 'hosting_provider', 'model_name'], unique=False)
    op.create_index('ix_model_pricing_project_id', 'model_pricing', ['project_id'], unique=False)
    
    # Extend observations table with Phase 2 fields
    op.add_column('observations', sa.Column('completion_start_time', sa.DateTime(), nullable=True))
    op.add_column('observations', sa.Column('model_parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('observations', sa.Column('total_tokens', sa.Integer(), nullable=True))
    op.add_column('observations', sa.Column('calculated_input_cost', sa.Numeric(), nullable=True))
    op.add_column('observations', sa.Column('calculated_output_cost', sa.Numeric(), nullable=True))
    op.add_column('observations', sa.Column('calculated_total_cost', sa.Numeric(), nullable=True))
    
    # Add indexes for Phase 2 queries
    op.create_index('ix_observations_level', 'observations', ['level'], unique=False)
    op.create_index('ix_observations_model', 'observations', ['model'], unique=False)
    op.create_index('ix_observations_total_cost', 'observations', ['calculated_total_cost'], unique=False)
    
    # Seed default model pricing (common models as of Nov 2024)
    # NULL project_id means this is default pricing for all projects
    op.execute("""
        INSERT INTO model_pricing 
        (id, project_id, hosting_provider, model_name, input_price_per_million, output_price_per_million, created_at, updated_at)
        VALUES
        -- OpenAI models
        (gen_random_uuid()::text, NULL, 'openai', 'gpt-4-turbo', 10.00, 30.00, now(), now()),
        (gen_random_uuid()::text, NULL, 'openai', 'gpt-4', 30.00, 60.00, now(), now()),
        (gen_random_uuid()::text, NULL, 'openai', 'gpt-3.5-turbo', 0.50, 1.50, now(), now()),
        (gen_random_uuid()::text, NULL, 'openai', 'gpt-4o', 2.50, 10.00, now(), now()),
        (gen_random_uuid()::text, NULL, 'openai', 'gpt-4o-mini', 0.15, 0.60, now(), now()),
        -- Anthropic models
        (gen_random_uuid()::text, NULL, 'anthropic', 'claude-3-opus-20240229', 15.00, 75.00, now(), now()),
        (gen_random_uuid()::text, NULL, 'anthropic', 'claude-3-sonnet-20240229', 3.00, 15.00, now(), now()),
        (gen_random_uuid()::text, NULL, 'anthropic', 'claude-3-haiku-20240307', 0.25, 1.25, now(), now()),
        (gen_random_uuid()::text, NULL, 'anthropic', 'claude-3-5-sonnet-20241022', 3.00, 15.00, now(), now()),
        -- Azure OpenAI (same models, different provider for tracking)
        (gen_random_uuid()::text, NULL, 'azure', 'gpt-4-turbo', 10.00, 30.00, now(), now()),
        (gen_random_uuid()::text, NULL, 'azure', 'gpt-4', 30.00, 60.00, now(), now()),
        (gen_random_uuid()::text, NULL, 'azure', 'gpt-35-turbo', 0.50, 1.50, now(), now())
    """)


def downgrade() -> None:
    """Remove Phase 2 additions."""
    
    # Drop indexes on observations
    op.drop_index('ix_observations_total_cost', table_name='observations')
    op.drop_index('ix_observations_model', table_name='observations')
    op.drop_index('ix_observations_level', table_name='observations')
    
    # Drop new columns from observations
    op.drop_column('observations', 'calculated_total_cost')
    op.drop_column('observations', 'calculated_output_cost')
    op.drop_column('observations', 'calculated_input_cost')
    op.drop_column('observations', 'total_tokens')
    op.drop_column('observations', 'model_parameters')
    op.drop_column('observations', 'completion_start_time')
    
    # Drop model_pricing table
    op.drop_index('ix_model_pricing_project_id', table_name='model_pricing')
    op.drop_index('ix_model_pricing_lookup', table_name='model_pricing')
    op.drop_table('model_pricing')

