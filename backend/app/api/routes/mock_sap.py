"""Mock SAP endpoints for testing (simulates Swisper SAP)"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List

router = APIRouter()

# Mock data (simulates Swisper's database with real Kvant model configs)
MOCK_LLM_CONFIGS = {
    "default": {
        "node_name": "default",
        "default_temperature": 0.2,
        "default_max_tokens": 10000,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Default fallback configuration for undefined nodes",
        "langsmith_tracing": True
    },
    "fact_relevance_classifier": {
        "node_name": "fact_relevance_classifier",
        "default_temperature": 0.1,
        "default_max_tokens": 500,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Classification only",
        "langsmith_tracing": True
    },
    "user_interface": {
        "node_name": "user_interface",
        "default_temperature": 0.2,
        "default_max_tokens": 5000,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Handles dialogue and UI",
        "langsmith_tracing": True
    },
    "global_planner": {
        "node_name": "global_planner",
        "default_temperature": 0.1,
        "default_max_tokens": 10000,
        "use_json_mode": True,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "top_p": 0.2,
        "description": "Global planning and routing",
        "langsmith_tracing": True
    },
    "research_planner": {
        "node_name": "research_planner",
        "default_temperature": 0.2,
        "default_max_tokens": 10000,
        "use_json_mode": True,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Research-specific planning",
        "langsmith_tracing": True
    },
    "completion_evaluator": {
        "node_name": "completion_evaluator",
        "default_temperature": 0.2,
        "default_max_tokens": 10000,
        "use_json_mode": False,
        "default_model": "inference-qwen3-8b",
        "fallback_model": "gpt-4.1",
        "description": "Evaluate task completion",
        "langsmith_tracing": True
    },
    "productivity_planner": {
        "node_name": "productivity_planner",
        "default_temperature": 0.1,
        "default_max_tokens": 10000,
        "use_json_mode": True,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Productivity task routing and planning",
        "langsmith_tracing": True
    },
    "productivity_write": {
        "node_name": "productivity_write",
        "default_temperature": 0.1,
        "default_max_tokens": 12000,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Data collection and confirmation",
        "langsmith_tracing": True
    },
    "rag_generation": {
        "node_name": "rag_generation",
        "default_temperature": 0.2,
        "default_max_tokens": 10000,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Generate responses from retrieved context",
        "langsmith_tracing": True
    },
    "document_analysis": {
        "node_name": "document_analysis",
        "default_temperature": 0.1,
        "default_max_tokens": 10000,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Analyze document content",
        "langsmith_tracing": True
    },
    "document_parsing": {
        "node_name": "document_parsing",
        "default_temperature": 0.0,
        "default_max_tokens": 8000,
        "use_json_mode": False,
        "default_model": "inference-qwq25-vl-72b",
        "fallback_model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "description": "Parse structured document data",
        "langsmith_tracing": True
    },
    "doc_agent_reactive_planner": {
        "node_name": "doc_agent_reactive_planner",
        "default_temperature": 0.2,
        "default_max_tokens": 12000,
        "use_json_mode": True,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "top_p": 0.1,
        "description": "Reactive planning for document agents",
        "langsmith_tracing": True
    },
    "email_rag_generation": {
        "node_name": "email_rag_generation",
        "default_temperature": 0.2,
        "default_max_tokens": 5000,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Generate responses from email context",
        "langsmith_tracing": True
    },
    "indexing": {
        "node_name": "indexing",
        "default_temperature": 0.2,
        "default_max_tokens": 3000,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Index and categorize content",
        "langsmith_tracing": True
    },
    "chat_summary": {
        "node_name": "chat_summary",
        "default_temperature": 0.2,
        "default_max_tokens": 800,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Summarize chat conversations",
        "langsmith_tracing": True
    },
    "embedding": {
        "node_name": "embedding",
        "default_temperature": 0.0,
        "default_max_tokens": 0,
        "use_json_mode": False,
        "default_model": "inference-bge-m3",
        "fallback_model": "text-embedding-3-large",
        "description": "Generate embeddings for semantic search",
        "langsmith_tracing": True
    },
    "document_metadata": {
        "node_name": "document_metadata",
        "default_temperature": 0.2,
        "default_max_tokens": 2000,
        "use_json_mode": False,
        "default_model": "inference-mistral-v03-7b",
        "fallback_model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "description": "Extract document metadata",
        "langsmith_tracing": True
    },
    "fact_extractor": {
        "node_name": "fact_extractor",
        "default_temperature": 0.1,
        "default_max_tokens": 2500,
        "use_json_mode": False,
        "default_model": "inference-qwq-32b",
        "fallback_model": "gpt-4.1",
        "description": "Extract facts from content",
        "langsmith_tracing": True
    },
    "intent_classification": {
        "node_name": "intent_classification",
        "default_temperature": 0.0,
        "default_max_tokens": 1024,
        "use_json_mode": False,
        "default_model": "inference-qwq-32b",
        "fallback_model": "gpt-4.1",
        "top_p": 0.1,
        "description": "Classify user intent",
        "langsmith_tracing": True
    },
    "preference_extractor": {
        "node_name": "preference_extractor",
        "default_temperature": 0.1,
        "default_max_tokens": 2500,
        "use_json_mode": False,
        "default_model": "inference-qwq-32b",
        "fallback_model": "gpt-4.1",
        "description": "Extract user preferences from content",
        "langsmith_tracing": True
    },
    "email_classification": {
        "node_name": "email_classification",
        "default_temperature": 0.1,
        "default_max_tokens": 4096,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "description": "Fast email classification",
        "langsmith_tracing": False
    },
    "title_generator": {
        "node_name": "title_generator",
        "default_temperature": 0.3,
        "default_max_tokens": 100,
        "use_json_mode": False,
        "default_model": "inference-llama4-maverick",
        "fallback_model": "gpt-4.1",
        "description": "Generate conversation titles",
        "langsmith_tracing": False
    }
}


class LLMConfigUpdate(BaseModel):
    """Request model for updating LLM config"""
    default_model: str | None = None
    default_temperature: float | None = Field(None, ge=0.0, le=2.0)
    default_max_tokens: int | None = Field(None, ge=100, le=32000)
    langsmith_tracing: bool | None = None


@router.get("/schema")
async def get_schema():
    """Mock SAP: Return config schema"""
    return {
        "version": "1.0",
        "tables": [
            {
                "name": "llm_node_config",
                "description": "LLM configuration per LangGraph node",
                "primary_key": "node_name",
                "fields": [
                    {
                        "name": "node_name",
                        "type": "string",
                        "required": True,
                        "immutable": True,
                        "max_length": 100,
                        "description": "LangGraph node identifier",
                        "placeholder": "e.g., global_planner"
                    },
                    {
                        "name": "default_model",
                        "type": "select",
                        "required": True,
                        "options": [
                            "inference-llama4-maverick",
                            "inference-llama4-scout-17b",
                            "inference-llama33-70b",
                            "inference-apertus-8b",
                            "inference-apertus-70b",
                            "inference-deepseekr1-70b",
                            "inference-deepseekr1-670b",
                            "inference-qwen3-8b",
                            "inference-qwq-32b",
                            "inference-qwq25-vl-72b",
                            "inference-gemma-12b-it",
                            "inference-gpt-oss-120b",
                            "inference-granite-33-8b",
                            "inference-granite-vision-2b",
                            "inference-mistral-v03-7b",
                            "inference-bge-m3",
                            "infer-bge-reranker",
                            "infer-whisper-3lt"
                        ],
                        "default": "inference-llama4-maverick",
                        "description": "Default LLM model for this node (Kvant models)"
                    },
                    {
                        "name": "default_temperature",
                        "type": "number",
                        "required": False,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.1,
                        "default": 0.7,
                        "description": "Sampling temperature (0 = deterministic, 2 = creative)"
                    },
                    {
                        "name": "default_max_tokens",
                        "type": "number",
                        "required": False,
                        "min": 100,
                        "max": 32000,
                        "step": 100,
                        "default": 10000,
                        "description": "Maximum tokens in response"
                    },
                    {
                        "name": "langsmith_tracing",
                        "type": "boolean",
                        "required": False,
                        "default": True,
                        "description": "Enable LangSmith tracing for this node"
                    }
                ]
            }
        ]
    }


@router.get("/llm_node_config")
async def list_configs():
    """Mock SAP: List all LLM configs"""
    return {
        "table": "llm_node_config",
        "records": list(MOCK_LLM_CONFIGS.values()),
        "count": len(MOCK_LLM_CONFIGS)
    }


@router.get("/llm_node_config/{node_name}")
async def get_config(node_name: str):
    """Mock SAP: Get single LLM config"""
    if node_name not in MOCK_LLM_CONFIGS:
        raise HTTPException(status_code=404, detail=f"Config not found: {node_name}")
    return MOCK_LLM_CONFIGS[node_name]


@router.put("/llm_node_config/{node_name}")
async def update_config(node_name: str, data: LLMConfigUpdate):
    """Mock SAP: Update LLM config"""
    if node_name not in MOCK_LLM_CONFIGS:
        raise HTTPException(status_code=404, detail=f"Config not found: {node_name}")
    
    # Validate temperature range (Pydantic handles this via Field constraints)
    update_dict = data.model_dump(exclude_unset=True)
    
    # Update mock data
    MOCK_LLM_CONFIGS[node_name].update(update_dict)
    
    return MOCK_LLM_CONFIGS[node_name]

