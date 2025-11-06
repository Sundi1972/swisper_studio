"""
SwisperStudio SDK

Simple integration for tracing Swisper LangGraph applications.

v0.5.0 - Q2 Tracing Toggle + Tool Observations:
- Dynamic tracing toggle (on/off per project)
- Universal tool observation extraction (no decorators!)
- Redis-cached toggle checks (<2ms overhead)
- Full cost tracking (316 models, CHF for KVANT)
- LLM reasoning capture
- 50x faster than HTTP (10ms overhead)

v0.4.0 - Redis Streams Architecture:
- 50x faster (500ms → 10ms overhead)
- LLM reasoning capture
- Connection status verification
- Per-node configuration

Usage:
    from swisper_studio_sdk import create_traced_graph, initialize_redis_publisher
    
    # Initialize once at startup (async)
    await initialize_redis_publisher(
        redis_url="redis://redis:6379",
        project_id="your-project-id",
        stream_name="observability:events",
        verify_consumer=True
    )
    
    # One-line change to add tracing
    graph = create_traced_graph(
        GlobalSupervisorState,
        trace_name="supervisor"
    )
"""

from swisper_studio_sdk.tracing.decorator import traced
from swisper_studio_sdk.tracing.graph_wrapper import create_traced_graph
from swisper_studio_sdk.tracing.client import initialize_tracing  # Deprecated, use Redis
from swisper_studio_sdk.tracing.redis_publisher import initialize_redis_publisher, close_redis_publisher
from swisper_studio_sdk.wrappers import wrap_llm_adapter, wrap_tools

__version__ = "0.5.0"  # Q2: Tracing toggle + universal tool observations

__all__ = [
    "traced",
    "create_traced_graph",
    "initialize_tracing",  # Deprecated - use initialize_redis_publisher
    "initialize_redis_publisher",
    "close_redis_publisher",
    "wrap_llm_adapter",
    "wrap_tools",
]

