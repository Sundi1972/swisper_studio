"""
@traced decorator for automatic tracing

Captures function inputs, outputs, and execution time.
Works with both sync and async functions.
"""

import asyncio
import copy
import functools
import time
import uuid
from typing import TypeVar, Callable

from .client import get_studio_client
from .context import get_current_trace, get_current_observation, set_current_observation

T = TypeVar('T')


def _detect_observation_type(
    observation_name: str,
    has_llm_data: bool,
    has_tool_data: bool
) -> str:
    """
    Auto-detect observation type based on captured data and naming.
    
    Priority order:
    1. LLM data → GENERATION
    2. Tool data → TOOL  
    3. Name contains "agent" → AGENT
    4. Default → SPAN
    
    Args:
        observation_name: Name of the observation/node
        has_llm_data: Whether LLM telemetry was captured
        has_tool_data: Whether tool telemetry was captured
        
    Returns:
        Observation type string (GENERATION, TOOL, AGENT, or SPAN)
    """
    # Priority 1: LLM data
    if has_llm_data:
        return "GENERATION"
    
    # Priority 2: Tool data
    if has_tool_data:
        return "TOOL"
    
    # Priority 3: Agent naming pattern
    if "agent" in observation_name.lower():
        return "AGENT"
    
    # Default
    return "SPAN"


def traced(
    name: str | None = None,
    observation_type: str = "SPAN",
):
    """
    Auto-trace any function/node.
    
    Usage:
        @traced("my_node")
        async def my_node(state):
            # Your logic
            return state
    
    Args:
        name: Observation name (defaults to function name)
        observation_type: Type of observation (SPAN, GENERATION, EVENT, TOOL, AGENT)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        obs_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            client = get_studio_client()
            if not client:
                # Tracing not initialized, just run function
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            # Get current trace context
            trace_id = get_current_trace()
            if not trace_id:
                # No active trace, skip tracing
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            # Capture input (LangGraph state is a dict or TypedDict)
            # CRITICAL: Must use deep copy to avoid mutations affecting captured state
            input_data = None
            if args:
                try:
                    state = args[0]
                    # TypedDict/dict (most common for LangGraph)
                    if isinstance(state, dict):
                        input_data = copy.deepcopy(state)  # DEEP copy to isolate mutations!
                    # Pydantic models
                    elif hasattr(state, 'model_dump'):
                        input_data = state.model_dump()
                    elif hasattr(state, 'dict'):
                        input_data = state.dict()
                    # Other objects with __dict__
                    elif hasattr(state, '__dict__'):
                        input_data = copy.deepcopy(vars(state))  # DEEP copy
                except Exception:
                    # Skip if serialization fails
                    pass

            # Get parent observation (for nesting)
            parent_obs = get_current_observation()

            # FIRE-AND-FORGET: Generate observation ID locally (no waiting)
            obs_id = str(uuid.uuid4())
            
            # Create observation in background (non-blocking)
            client.create_observation_background(
                trace_id=trace_id,
                name=obs_name,
                type=observation_type,
                observation_id=obs_id,  # Pre-generated
                parent_observation_id=parent_obs,
                input=input_data,
            )

            # Set as current observation immediately (for nested calls)
            token = set_current_observation(obs_id)

            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Capture output (LangGraph returns dict or TypedDict)
                # CRITICAL: Must use deep copy to isolate from input mutations
                output_data = None
                try:
                    # TypedDict/dict (most common for LangGraph)
                    if isinstance(result, dict):
                        output_data = copy.deepcopy(result)  # DEEP copy!
                    # Pydantic models
                    elif hasattr(result, 'model_dump'):
                        output_data = result.model_dump()
                    elif hasattr(result, 'dict'):
                        output_data = result.dict()
                    # Other objects
                    elif hasattr(result, '__dict__'):
                        output_data = copy.deepcopy(vars(result))  # DEEP copy
                except Exception:
                    pass

                # FIRE-AND-FORGET: End observation in background (non-blocking)
                client.end_observation_background(
                    observation_id=obs_id,
                    output=output_data,
                    level="DEFAULT",
                )

                return result

            except Exception as e:
                # FIRE-AND-FORGET: End observation with error in background
                client.end_observation_background(
                    observation_id=obs_id,
                    level="ERROR",
                    status_message=str(e),
                )
                raise

            finally:
                # Reset observation context
                set_current_observation(parent_obs, token)

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            # For sync functions, wrap in async
            @functools.wraps(func)
            async def sync_wrapper(*args, **kwargs) -> T:
                return await async_wrapper(*args, **kwargs)
            return sync_wrapper

    return decorator

