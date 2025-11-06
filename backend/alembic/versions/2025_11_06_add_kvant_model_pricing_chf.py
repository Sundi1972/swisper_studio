"""Add KVANT model pricing (CHF)

Revision ID: add_kvant_pricing_chf
Revises: (previous migration)
Create Date: 2025-11-06

Adds pricing for KVANT/Swisper models used in production.
Prices are in CHF (Swiss Francs) per 1 million tokens.

Source: Swisper team pricing table (2025-11-06)
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = 'add_kvant_pricing_chf'
down_revision = 'c85a4ae4ef21'  # remove_user_id_foreign_key_from_traces
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add KVANT model pricing"""
    
    # Insert KVANT model pricing (CHF per 1M tokens)
    # These are Swisper's production models
    op.execute("""
        INSERT INTO model_pricing 
        (id, project_id, hosting_provider, model_name, input_price_per_million, output_price_per_million, created_at, updated_at)
        VALUES
        -- KVANT Chat Models (Multilingual Dialogue)
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-apertus-8b', 0.17, 0.19, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-apertus-70b', 0.82, 0.89, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'swiss-ai/Apertus-8b-Instruct-2509', 0.17, 0.19, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'swiss-ai/Apertus-70b-Instruct-2509', 0.82, 0.89, now(), now()),
        
        -- KVANT Embedding Models
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-bge-m3', 0.012, 0, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'BAAI/bge-m3', 0.012, 0, now(), now()),
        
        -- KVANT Reranker Models
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-bge-reranker', 0.003, 0, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'BAAI/bge-reranker-v2-m3', 0.003, 0, now(), now()),
        
        -- DeepSeek R1 (Reasoning Models)
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-deepseeekr1-70b', 0.5, 0.65, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-deepseeekr1-676b', 1.699, 4.958, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B', 0.5, 0.65, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'deepseek-ai/DeepSeek-R1', 1.699, 4.958, now(), now()),
        
        -- Gemma Models
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-gemma-12b-it', 0.14, 0.233, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'google/gemma-3-12b-it', 0.14, 0.233, now(), now()),
        
        -- GPT-OSS Models
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-gpt-oss-120b', 0.143, 0.588, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'openai/gpt-oss-120b', 0.143, 0.588, now(), now()),
        
        -- Granite Models
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-granite-33-8b', 0.2, 0.2, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-granite-emb-278m', 0, 0.1, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-granite-vision-2b', 0.05, 0.175, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'ibm-granite/granite-3.3-8b-instruct', 0.2, 0.2, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'ibm-granite/granite-embedding-278m-multilingual', 0, 0.1, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'ibm-granite/granite-vision-2b', 0.05, 0.175, now(), now()),
        
        -- Llama 3.3 Models
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-llama33-70b', 0.454, 0.573, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'meta-llama/Llama-3.3-70B-Instruct', 0.454, 0.573, now(), now()),
        
        -- Llama 4 Models (Maverick & Scout)
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-llama4-maverick', 0.225, 0.898, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-llama4-scout-17b', 0.19, 0.536, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'meta-llama/Llama4-Maverick-178-16bf-Instruct', 0.225, 0.898, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'meta-llama/Llama-4-Scout-17B-16f-Instruct', 0.19, 0.536, now(), now()),
        
        -- Mistral Models
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-mistral-v03-7b', 0.101, 0.155, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'mistralai/Mistral-7B-Instruct-v0.3', 0.101, 0.155, now(), now()),
        
        -- Qwen Models (Reasoning)
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-qwen3-8b', 0.035, 0.138, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-qwq-32b', 0.438, 0.533, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'inference-qwq25-v1-72b', 0.717, 1.691, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'Qwen/Qwen3-8B', 0.035, 0.138, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'Qwen/QwQ-32B', 0.438, 0.533, now(), now()),
        (gen_random_uuid()::text, NULL, 'kvant', 'Qwen/Qwen2.5-VL-72B-Instruct', 0.717, 1.691, now(), now())
        
        ON CONFLICT (project_id, hosting_provider, model_name) DO UPDATE SET
            input_price_per_million = EXCLUDED.input_price_per_million,
            output_price_per_million = EXCLUDED.output_price_per_million,
            updated_at = now();
    """)


def downgrade() -> None:
    """Remove KVANT model pricing"""
    op.execute("""
        DELETE FROM model_pricing 
        WHERE hosting_provider = 'kvant';
    """)

