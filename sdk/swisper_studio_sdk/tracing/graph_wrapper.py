"""
LangGraph wrapper for automatic tracing

create_traced_graph() enables ONE-LINE integration for Swisper.

Usage:
    # Before:
    # graph = StateGraph(GlobalSupervisorState)

    # After (ONE LINE CHANGE):
    graph = create_traced_graph(GlobalSupervisorState, trace_name="supervisor")

    # All nodes added to this graph are automatically traced!
"""

from typing import Type, TypeVar
from langgraph.graph import StateGraph
import asyncio
import copy
import functools
import logging
import uuid
from datetime import datetime

from .decorator import traced
from .client import get_studio_client
from .context import set_current_trace, set_current_observation, get_current_trace, get_current_observation
from .redis_publisher import publish_event, get_redis_client, is_tracing_enabled_for_project, get_project_id
from .. import __version__

logger = logging.getLogger(__name__)

TState = TypeVar('TState')

# Global heartbeat task tracker (one per project)
_heartbeat_tasks = {}


async def _publish_heartbeat_loop(project_id: str):
    """
    Publish heartbeat events every 10 seconds.
    
    Allows Swisper to show green indicator when:
    - Tracing toggle is ON
    - SDK is alive and publishing
    
    Heartbeat format:
    {
        "event_type": "heartbeat",
        "data": {
            "project_id": "...",
            "sdk_version": "0.5.0",
            "timestamp": "2025-11-07T07:30:00Z"
        }
    }
    """
    try:
        while True:
            try:
                await publish_event(
                    event_type="heartbeat",
                    trace_id=None,  # Not tied to specific trace
                    data={
                        "project_id": project_id,
                        "sdk_version": __version__,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                logger.debug(f"💓 Heartbeat published for project {project_id[:8]}...")
            except Exception as e:
                logger.warning(f"Failed to publish heartbeat: {e}")
            
            await asyncio.sleep(10)  # Heartbeat every 10 seconds
    except asyncio.CancelledError:
        logger.info(f"Heartbeat task cancelled for project {project_id[:8]}...")
        raise


def _start_heartbeat_task(project_id: str):
    """
    Start heartbeat publishing task for a project (if not already running).
    
    Only one heartbeat task per project_id.
    Task runs in background and publishes every 10 seconds.
    """
    if project_id not in _heartbeat_tasks:
        task = asyncio.create_task(_publish_heartbeat_loop(project_id))
        _heartbeat_tasks[project_id] = task
        logger.info(f"💓 Started heartbeat task for project {project_id[:8]}...")


def create_traced_graph(
    state_class: Type[TState],
    trace_name: str,
    auto_trace_all_nodes: bool = True,
) -> StateGraph:
    """
    Create a StateGraph with automatic node tracing.

    This is the key integration feature - enables tracing with minimal code changes.

    Args:
        state_class: The LangGraph state class
        trace_name: Name for traces created by this graph
        auto_trace_all_nodes: If True, automatically wraps all nodes with @traced

    Returns:
        StateGraph instance with tracing enabled

    Example:
        graph = create_traced_graph(GlobalSupervisorState, trace_name="supervisor")
        graph.add_node("intent_classification", intent_classification_node)
        # intent_classification_node is automatically traced!
    """
    graph = StateGraph(state_class)

    if auto_trace_all_nodes:
        # Save original add_node method
        original_add_node = graph.add_node

        # Create wrapper that auto-traces
        def traced_add_node(name: str, func):
            """
            Replacement for add_node that automatically wraps functions with @traced.

            This is the "magic" that makes the one-line integration work.
            """
            # Wrap function with @traced decorator
            # Use "AUTO" to trigger type detection based on captured LLM data
            wrapped_func = traced(
                name=name,
                observation_type="AUTO"  # Will auto-detect GENERATION/TOOL/AGENT/SPAN
            )(func)

            # Call original add_node with wrapped function
            return original_add_node(name, wrapped_func)

        # Replace add_node with auto-tracing version
        graph.add_node = traced_add_node

    # Wrap compile to create trace on invocation
    original_compile = graph.compile

    def traced_compile(*args, **kwargs):
        """Wrap compile to intercept ainvoke and create traces"""
        compiled_graph = original_compile(*args, **kwargs)
        original_ainvoke = compiled_graph.ainvoke

        @functools.wraps(original_ainvoke)
        async def traced_ainvoke(input_state, config=None, **invoke_kwargs):
            """
            Create trace before running graph (Redis Streams version).

            Context-aware:
            - If already in a trace context (nested agent), reuse existing trace
            - If not in trace context (top-level), create new trace
            """
            redis_client = get_redis_client()

            if not redis_client:
                # Tracing not initialized, run normally
                return await original_ainvoke(input_state, config, **invoke_kwargs)

            # Check if we're already in a trace context (nested agent call)
            existing_trace_id = get_current_trace()
            existing_parent_obs = get_current_observation()

            if existing_trace_id:
                # NESTED AGENT: We're inside another traced graph
                # Don't create new trace - create observation under existing trace
                print(f"🔗 Nested agent '{trace_name}' detected, using existing trace: {existing_trace_id[:12]}...")

                parent_obs_id = str(uuid.uuid4())

                try:
                    # Create observation for this nested graph (AGENT type)
                    await publish_event(
                        event_type="observation_start",
                        trace_id=existing_trace_id,  # Reuse existing trace!
                        observation_id=parent_obs_id,
                        data={
                            "name": trace_name,
                            "type": "AGENT",  # Nested agent
                            "parent_observation_id": existing_parent_obs,  # Link to caller!
                            "input": copy.deepcopy(input_state) if isinstance(input_state, dict) else None,
                            "start_time": datetime.utcnow().isoformat(),
                        }
                    )

                    # Set as current observation (child observations will nest under this)
                    parent_token = set_current_observation(parent_obs_id)

                    # Run graph with nested context
                    result = await original_ainvoke(input_state, config, **invoke_kwargs)

                    # End nested agent observation
                    await publish_event(
                        event_type="observation_end",
                        trace_id=existing_trace_id,
                        observation_id=parent_obs_id,
                        data={
                            "output": copy.deepcopy(result) if isinstance(result, dict) else None,
                            "level": "DEFAULT",
                            "end_time": datetime.utcnow().isoformat(),
                        }
                    )

                    return result

                finally:
                    # Restore parent observation context
                    set_current_observation(existing_parent_obs, parent_token)
                    # DON'T clear trace - still in parent graph!

            else:
                # TOP-LEVEL AGENT: Create new trace
                
                # Q2: Check if tracing is enabled for this project (per-request check, 1-2ms)
                project_id = get_project_id()
                if project_id:
                    tracing_enabled = await is_tracing_enabled_for_project(project_id)
                    if not tracing_enabled:
                        logger.info(f"⏸️ Tracing disabled for project {project_id[:8]}..., skipping trace creation")
                        # Run graph normally WITHOUT tracing
                        return await original_ainvoke(input_state, config, **invoke_kwargs)
                    
                    # Tracing is enabled - start heartbeat task (if not already running)
                    _start_heartbeat_task(project_id)
                
                print(f"📍 Top-level agent '{trace_name}', creating new trace...")

                try:
                    user_id = input_state.get("user_id") if isinstance(input_state, dict) else None
                    session_id = input_state.get("chat_id") or input_state.get("session_id") if isinstance(input_state, dict) else None

                    # Extract first sentence of user message for meaningful trace name
                    trace_display_name = trace_name  # Default
                    if isinstance(input_state, dict):
                        user_message = input_state.get("user_message") or input_state.get("message")
                        if user_message and isinstance(user_message, str):
                            # Get first sentence (up to 100 chars)
                            first_sentence = user_message.split('.')[0].split('?')[0].split('!')[0]
                            if len(first_sentence) > 100:
                                first_sentence = first_sentence[:97] + "..."
                            trace_display_name = first_sentence.strip() or trace_name

                    # Generate trace ID locally
                    trace_id = str(uuid.uuid4())

                    # REDIS STREAMS: Publish trace start event (1-2ms, non-blocking)
                    await publish_event(
                        event_type="trace_start",
                        trace_id=trace_id,
                        data={
                            "name": trace_display_name,  # Use first sentence as name!
                            "user_id": user_id,
                            "session_id": session_id,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                    # Set trace context for observations
                    set_current_trace(trace_id)

                    # Create parent observation for the graph (hierarchical structure)
                    parent_obs_id = str(uuid.uuid4())

                    # REDIS STREAMS: Publish observation start event
                    await publish_event(
                        event_type="observation_start",
                        trace_id=trace_id,
                        observation_id=parent_obs_id,
                        data={
                            "name": trace_name,
                            "type": "AGENT",  # Graph is an agent
                            "parent_observation_id": None,  # Top level
                            "input": copy.deepcopy(input_state) if isinstance(input_state, dict) else None,
                            "start_time": datetime.utcnow().isoformat(),
                        }
                    )

                    # Set as current observation immediately
                    parent_token = set_current_observation(parent_obs_id)

                except Exception as e:
                    # If trace creation fails, continue without tracing
                    print(f"⚠️ Failed to create trace: {e}")
                    return await original_ainvoke(input_state, config, **invoke_kwargs)

                # Run graph with trace context
                try:
                    result = await original_ainvoke(input_state, config, **invoke_kwargs)

                    # REDIS STREAMS: Publish observation end event
                    await publish_event(
                        event_type="observation_end",
                        trace_id=trace_id,
                        observation_id=parent_obs_id,
                        data={
                            "output": copy.deepcopy(result) if isinstance(result, dict) else None,
                            "level": "DEFAULT",
                            "end_time": datetime.utcnow().isoformat(),
                        }
                    )

                    return result
                finally:
                    # Clear observation and trace context (end of top-level trace)
                    set_current_observation(None, parent_token)
                    set_current_trace(None)

        # Replace ainvoke with traced version
        compiled_graph.ainvoke = traced_ainvoke
        return compiled_graph

    # Replace compile with our wrapper
    graph.compile = traced_compile

    return graph

