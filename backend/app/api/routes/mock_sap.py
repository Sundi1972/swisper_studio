"""Mock SAP endpoints for testing (simulates Swisper SAP)"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List

router = APIRouter()

# Mock data (simulates Swisper's database)
MOCK_LLM_CONFIGS = {
    "global_planner": {
        "node_name": "global_planner",
        "default_model": "gpt-4-turbo",
        "default_temperature": 0.7,
        "default_max_tokens": 4000,
        "langsmith_tracing": True
    },
    "intent_classification": {
        "node_name": "intent_classification",
        "default_model": "gpt-4",
        "default_temperature": 0.8,
        "default_max_tokens": 2000,
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

