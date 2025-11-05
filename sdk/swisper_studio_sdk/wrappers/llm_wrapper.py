"""
LLM Wrapper - Automatic capture of LLM calls

Intercepts Swisper's llm_adapter.get_structured_output() to capture prompts, 
responses, tokens, and model parameters.

v0.3.0: Now implemented based on actual Swisper code analysis.
"""

import logging
from typing import Optional
from ..tracing.context import get_current_observation

logger = logging.getLogger(__name__)

# Global state to track if wrapper is active
_llm_wrapper_active = False


def wrap_llm_adapter() -> None:
    """
    Wrap Swisper's TokenTrackingLLMAdapter to capture LLM telemetry.
    
    Based on analysis of Helvetiq codebase:
    - Path: backend.app.api.services.llm_adapter.token_tracking_llm_adapter
    - Method: get_structured_output(messages, schema, agent_type, ...)
    - Returns: StructuredOutputResult with result, token_usage, prompt_tokens, completion_tokens
    
    Called from: initialize_tracing()
    """
    global _llm_wrapper_active
    
    if _llm_wrapper_active:
        return  # Already wrapped
    
    try:
        # Import Swisper's LLM adapter
        from app.api.services.llm_adapter.token_tracking_llm_adapter import TokenTrackingLLMAdapter
        
        # Save original method
        original_get_structured_output = TokenTrackingLLMAdapter.get_structured_output
        
        # Create wrapper
        async def wrapped_get_structured_output(self, messages, schema, agent_type=None, 
                                               on_reasoning_chunk=None, llm_reasoning_language=None, 
                                               metadata=None):
            """
            Wrapped get_structured_output that captures LLM telemetry.
            
            Captures:
            - Messages (prompts sent to LLM)
            - Schema (what we're asking for)
            - Result (LLM response)
            - Tokens (prompt + completion)
            - Agent type (for model identification)
            """
            # Store telemetry in context BEFORE calling LLM
            obs_id = get_current_observation()
            if obs_id:
                # We're in a traced observation - capture prompts
                _store_llm_input({
                    "messages": messages,
                    "agent_type": agent_type,
                    "schema_name": schema.__name__ if schema else None,
                })
            
            # Call original method
            result = await original_get_structured_output(
                self, messages, schema, agent_type, 
                on_reasoning_chunk, llm_reasoning_language, metadata
            )
            
            # Store telemetry AFTER getting result
            if obs_id:
                _store_llm_output({
                    "result": result.result.model_dump() if hasattr(result.result, 'model_dump') else str(result.result),
                    "total_tokens": result.token_usage,
                    "prompt_tokens": result.prompt_tokens,
                    "completion_tokens": result.completion_tokens,
                })
            
            return result
        
        # Replace method
        TokenTrackingLLMAdapter.get_structured_output = wrapped_get_structured_output
        _llm_wrapper_active = True
        
        logger.info("✅ LLM adapter wrapped for prompt capture")
        
    except ImportError as e:
        # Swisper structure different or not running in Swisper context
        logger.debug(f"LLM adapter not available for wrapping: {e}")
        pass
    except Exception as e:
        logger.warning(f"Failed to wrap LLM adapter: {e}")
        pass


# Global storage for LLM telemetry (temporary until observation update)
_llm_telemetry_store = {}


def _store_llm_input(data: dict) -> None:
    """Store LLM input data in current observation context"""
    obs_id = get_current_observation()
    if obs_id:
        if obs_id not in _llm_telemetry_store:
            _llm_telemetry_store[obs_id] = {}
        _llm_telemetry_store[obs_id]['input'] = data


def _store_llm_output(data: dict) -> None:
    """Store LLM output data in current observation context"""
    obs_id = get_current_observation()
    if obs_id:
        if obs_id not in _llm_telemetry_store:
            _llm_telemetry_store[obs_id] = {}
        _llm_telemetry_store[obs_id]['output'] = data


def get_llm_telemetry(obs_id: str) -> Optional[dict]:
    """Get stored LLM telemetry for an observation"""
    return _llm_telemetry_store.get(obs_id)


