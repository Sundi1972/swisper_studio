"""
SwisperStudio SDK

Simple integration for tracing Swisper LangGraph applications.

Usage:
    from swisper_studio_sdk import create_traced_graph, initialize_tracing
    
    # Initialize once at startup
    initialize_tracing(
        api_url="https://studio.swisper.com",
        api_key="your-api-key"
    )
    
    # One-line change to add tracing
    graph = create_traced_graph(
        GlobalSupervisorState,
        trace_name="supervisor"
    )
"""

from swisper_studio_sdk.tracing.decorator import traced
from swisper_studio_sdk.tracing.graph_wrapper import create_traced_graph
from swisper_studio_sdk.tracing.client import initialize_tracing
from swisper_studio_sdk.wrappers import wrap_llm_adapter, wrap_tools

__version__ = "0.3.2"  # Phase 5.1: Fix AUTO type enum validation

__all__ = [
    "traced",
    "create_traced_graph",
    "initialize_tracing",
    "wrap_llm_adapter",
    "wrap_tools",
]

