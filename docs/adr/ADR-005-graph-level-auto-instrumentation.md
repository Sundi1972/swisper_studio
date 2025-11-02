# ADR-005: Graph-Level Auto-Instrumentation

**Status:** ✅ Accepted  
**Date:** 2025-11-01  
**Deciders:** Development Team, Product Owner  
**Context:** Phase 1 - SDK Integration Strategy

---

## Context and Problem Statement

Developers need to add tracing to existing Swisper deployments. Swisper uses LangGraph with potentially dozens of nodes per graph. Adding tracing should be **PO-friendly** (minimal code changes) and **developer-friendly** (zero boilerplate).

**Question:** How can we make tracing integration as simple as possible?

---

## Decision Drivers

* **Developer experience** - Minimize code changes required
* **PO-friendliness** - PO should be able to enable tracing
* **Maintainability** - No boilerplate in every node
* **Completeness** - Ensure all nodes are traced (no gaps)
* **Flexibility** - Still allow custom tracing for specific nodes

---

## Considered Options

1. **Manual decorator per node** - Developers add `@traced` to every function
2. **Graph-level auto-instrumentation** - One wrapper instruments entire graph
3. **Configuration-based** - YAML file specifies which nodes to trace
4. **Bytecode injection** - Automatic at runtime (no code changes)

---

## Decision Outcome

**Chosen option:** "Graph-level auto-instrumentation"

**Rationale:**

The integration should be **ONE LINE CHANGE**. This is the simplest possible developer experience.

### How It Works

**Before (no tracing):**
```python
from langgraph.graph import StateGraph

graph = StateGraph(GlobalSupervisorState)
graph.add_node("intent_classification", intent_classification_node)
graph.add_node("memory", memory_node)
graph.add_node("planner", planner_node)
# ... 20 more nodes ...

app = graph.compile()
```

**After (with tracing - ONE LINE!):**
```python
from langgraph.graph import StateGraph
from swisper_studio_sdk import create_traced_graph  # ← Add import

graph = create_traced_graph(  # ← Change this line
    GlobalSupervisorState,
    trace_name="global_supervisor"
)

graph.add_node("intent_classification", intent_classification_node)
graph.add_node("memory", memory_node)
graph.add_node("planner", planner_node)
# All nodes automatically traced, zero decorators needed!

app = graph.compile()
```

### Implementation

```python
# swisper_studio_sdk/tracing/graph_wrapper.py

from langgraph.graph import StateGraph
from .decorator import traced

def create_traced_graph(state_class, trace_name: str):
    """
    Create StateGraph with automatic node tracing.
    
    Monkey-patches add_node() to auto-wrap functions with @traced.
    """
    graph = StateGraph(state_class)
    
    # Save original add_node method
    original_add_node = graph.add_node
    
    # Create wrapper that auto-traces
    def traced_add_node(name: str, func):
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
```

**What happens:**
1. Developer calls `create_traced_graph()` instead of `StateGraph()`
2. Returns a StateGraph instance (100% compatible)
3. When `graph.add_node()` is called, it automatically wraps the function with `@traced`
4. All nodes are traced without any decorators!

### Optional: Manual Tracing for Fine Control

```python
# If developer wants custom tracing for specific node
@traced("intent_classification", observation_type="GENERATION", metadata={"priority": "high"})
async def intent_classification_node(state):
    # Custom tracking for this node
    return state
```

### Positive Consequences

* ✅ **Minimal code changes** - 1 import + 1 line
* ✅ **PO can enable tracing** - Simple enough for non-developers
* ✅ **Complete coverage** - All nodes automatically traced
* ✅ **No boilerplate** - Zero decorators needed
* ✅ **Flexible** - Can still add manual decorators for custom behavior
* ✅ **Backward compatible** - Returns standard StateGraph

### Negative Consequences

* ❌ "Magic" behavior (monkey-patching might confuse some developers)
* ❌ Requires understanding of how create_traced_graph works
* ❌ Potential conflicts if LangGraph changes add_node signature

---

## Pros and Cons of the Options

### Option 1: Manual decorator per node

```python
@traced("node1")
async def node1(state): ...

@traced("node2")
async def node2(state): ...

@traced("node3")
async def node3(state): ...
# ... repeat for every node
```

**Pros:**
* Explicit (no magic)
* Fine-grained control
* Easy to understand

**Cons:**
* ❌ **Boilerplate hell** (decorator on every function)
* ❌ **Easy to forget** (miss nodes, incomplete tracing)
* ❌ **Not PO-friendly** (requires touching code)
* ❌ **Maintenance burden** (every new node needs decorator)

### Option 2: Graph-level auto-instrumentation ✅ CHOSEN

**Pros:**
* ✅ **Minimal code changes** (1 line)
* ✅ **Complete coverage** (can't forget nodes)
* ✅ **PO-friendly**
* ✅ **Maintainable**

**Cons:**
* Monkey-patching (some developers dislike "magic")
* Potential compatibility issues with future LangGraph versions

### Option 3: Configuration-based

```yaml
# tracing_config.yaml
enabled: true
nodes:
  - intent_classification
  - memory
  - planner
```

**Pros:**
* No code changes at all
* Configuration-driven

**Cons:**
* ❌ **Separate config file to maintain** (YAML out of sync with code)
* ❌ **Manual list** (still need to specify every node)
* ❌ **Runtime discovery needed** (complex)

### Option 4: Bytecode injection

**Pros:**
* Truly zero code changes

**Cons:**
* ❌ **Too magical** (hard to debug)
* ❌ **Complex to implement** (AST manipulation)
* ❌ **Fragile** (breaks with Python updates)

---

## Implementation Notes

### Compatibility Check

Before implementing, verify LangGraph's `add_node` signature:

```python
# LangGraph source
class StateGraph:
    def add_node(self, name: str, action: RunnableLike):
        # Implementation
```

Our wrapper must maintain this exact signature.

### Testing Strategy

```python
@pytest.mark.asyncio
async def test_create_traced_graph_compatibility():
    """Verify create_traced_graph returns compatible StateGraph"""
    
    # Create traced graph
    graph = create_traced_graph(TestState, trace_name="test")
    
    # Should work exactly like regular StateGraph
    graph.add_node("node1", node1_func)
    graph.add_edge("node1", "node2")
    graph.set_entry_point("node1")
    
    app = graph.compile()
    result = await app.ainvoke({"value": 0})
    
    # Verify traces were sent
    assert traces_sent_count() == 1
    assert observations_sent_count() == 1
```

### Documentation for Developers

```markdown
# Swisper SDK - Quick Start

## Enable Tracing (30 seconds)

1. Install SDK:
   ```bash
   pip install swisper-studio-sdk
   ```

2. Add environment variables:
   ```bash
   SWISPER_STUDIO_URL=https://studio.swisper.com
   SWISPER_STUDIO_API_KEY=your-api-key
   ```

3. Change ONE line in your graph:
   ```python
   # Before:
   # graph = StateGraph(GlobalSupervisorState)
   
   # After:
   from swisper_studio_sdk import create_traced_graph
   graph = create_traced_graph(GlobalSupervisorState, trace_name="supervisor")
   ```

4. Done! All nodes are now traced.
```

---

## Links

* **Integration Guide:** [Swisper Studio Integration](../guides/swisper_studio_integration_guide.md)
* **SDK Implementation:** Phase 1 - SDK Tasks
* **Decorator Implementation:** `swisper_studio_sdk/tracing/decorator.py`

---

## Validation

**Success Metrics:**
- ✅ Integration takes < 30 minutes for new deployment
- ✅ PO can enable tracing following documentation
- ✅ 100% node coverage (all nodes traced)
- ✅ Zero nodes missed (automatic vs. manual decorators)
- ✅ Compatible with all LangGraph graph types

**Review Date:** After Phase 1 SDK testing with real Swisper instance

---

## Notes

**Alternative for Paranoid Developers:**

If developers don't like "magic," they can still use manual decorators:

```python
# Explicit tracing (no create_traced_graph)
@traced("node1")
async def node1(state): ...

@traced("node2")
async def node2(state): ...
```

Both approaches work! We provide the auto-instrumentation for convenience.

**Future Enhancement (Phase 5):**
- Visual configurator in SwisperStudio UI
- PO selects nodes to trace (checkboxes)
- SwisperStudio generates config
- No code changes at all!

