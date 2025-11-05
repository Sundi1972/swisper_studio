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
import copy
import functools

from .decorator import traced
from .client import get_studio_client
from .context import set_current_trace, set_current_observation

TState = TypeVar('TState')


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
            wrapped_func = traced(
                name=name,
                observation_type="SPAN"
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
            """Create trace before running graph"""
            client = get_studio_client()
            
            if not client:
                # Tracing not initialized, run normally
                return await original_ainvoke(input_state, config, **invoke_kwargs)
            
            # Create trace
            try:
                user_id = input_state.get("user_id") if isinstance(input_state, dict) else None
                session_id = input_state.get("chat_id") or input_state.get("session_id") if isinstance(input_state, dict) else None
                
                trace_id = await client.create_trace(
                    name=trace_name,
                    user_id=user_id,
                    session_id=session_id,
                )
                
                # Set trace context for observations
                set_current_trace(trace_id)
                
                # FIX: Create parent observation for the graph (Issue #1)
                # This makes all child nodes nest under "global_supervisor" parent
                parent_obs_id = await client.create_observation(
                    trace_id=trace_id,
                    name=trace_name,  # "global_supervisor"
                    type="AGENT",  # Graph is an agent
                    parent_observation_id=None,  # Top level
                    input=copy.deepcopy(input_state) if isinstance(input_state, dict) else None,
                )
                
                # Set as current observation so child nodes nest under it
                parent_token = set_current_observation(parent_obs_id)
                
            except Exception as e:
                # If trace creation fails, continue without tracing
                print(f"⚠️ Failed to create trace: {e}")
                return await original_ainvoke(input_state, config, **invoke_kwargs)
            
            # Run graph with trace context
            try:
                result = await original_ainvoke(input_state, config, **invoke_kwargs)
                
                # FIX: End parent observation with result
                try:
                    await client.end_observation(
                        observation_id=parent_obs_id,
                        output=copy.deepcopy(result) if isinstance(result, dict) else None,
                        level="DEFAULT",
                    )
                except Exception:
                    # Ignore if ending parent observation fails
                    pass
                
                return result
            finally:
                # Clear observation and trace context
                set_current_observation(None, parent_token)
                set_current_trace(None)
        
        # Replace ainvoke with traced version
        compiled_graph.ainvoke = traced_ainvoke
        return compiled_graph
    
    # Replace compile with our wrapper
    graph.compile = traced_compile

    return graph

