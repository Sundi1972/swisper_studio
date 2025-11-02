# SwisperStudio SDK

Simple integration for tracing Swisper LangGraph applications.

## Installation

```bash
pip install swisper-studio-sdk
# Or with uv:
uv pip install swisper-studio-sdk
```

## Quick Start (30 seconds)

### 1. Initialize at Startup

```python
# In your main.py or startup code
from swisper_studio_sdk import initialize_tracing

initialize_tracing(
    api_url="https://studio.swisper.com",  # Your SwisperStudio instance
    api_key="your-api-key",                # From SwisperStudio
    project_id="your-project-id",          # Your project in SwisperStudio
)
```

### 2. ONE LINE CHANGE to Enable Tracing

```python
# Before:
from langgraph.graph import StateGraph
graph = StateGraph(GlobalSupervisorState)

# After (change ONE line):
from swisper_studio_sdk import create_traced_graph
graph = create_traced_graph(GlobalSupervisorState, trace_name="supervisor")

# That's it! All nodes added to this graph are automatically traced!
```

### 3. Add Nodes as Normal

```python
# Add nodes - they're automatically traced!
graph.add_node("intent_classification", intent_classification_node)
graph.add_node("memory", memory_node)
graph.add_node("planner", planner_node)
graph.add_node("ui_node", ui_node)

# Compile and run as usual
app = graph.compile()
result = await app.ainvoke(initial_state)

# All executions are now traced to SwisperStudio! 🎉
```

## Features

- ✅ **One-line integration** - `create_traced_graph()` instead of `StateGraph()`
- ✅ **Auto-instrumentation** - All nodes automatically traced
- ✅ **State capture** - Captures input/output state at each node
- ✅ **Error tracking** - Captures exceptions and error messages
- ✅ **Nested observations** - Supports parent-child relationships
- ✅ **Zero boilerplate** - No decorators needed on individual nodes

## Advanced Usage

### Manual Tracing (Optional)

For fine-grained control, you can still use `@traced` decorator directly:

```python
from swisper_studio_sdk import traced

@traced("intent_classification", observation_type="GENERATION")
async def intent_classification_node(state):
    # Custom metadata or specific observation type
    return state
```

### Observation Types

- `SPAN` - Generic execution span (default)
- `GENERATION` - LLM generation
- `EVENT` - Point-in-time event
- `TOOL` - Tool call
- `AGENT` - Agent execution

## How It Works

`create_traced_graph()` monkey-patches the `add_node()` method to automatically wrap node functions with the `@traced` decorator. This means:

1. You call `create_traced_graph()` once
2. Every `graph.add_node()` call automatically wraps the function
3. All nodes are traced without any additional code

It's pure Python magic that makes integration PO-friendly! ✨

## Requirements

- Python 3.11+
- LangGraph
- httpx

## License

MIT

