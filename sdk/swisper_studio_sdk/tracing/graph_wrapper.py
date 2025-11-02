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

from .decorator import traced

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

    return graph

