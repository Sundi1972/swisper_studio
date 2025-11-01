# Agent Creation Guide

**Audience:** Developers, Architects  
**Last Updated:** October 29, 2025  
**Status:** Production Standard

---

## 🎯 Overview

This guide walks you through creating a new LangGraph agent in the Swisper system.

**Prerequisites:**
- Understanding of LangGraph (StateGraph, nodes, edges)
- Familiarity with async Python
- Knowledge of the prompt asset pattern

---

## 🤔 Step 1: Determine If You Need an Agent or Service

### **Create an AGENT if:**
- ✅ Multi-step workflow with planning/iteration
- ✅ Needs state management across steps
- ✅ Complex decision-making (conditional routing)
- ✅ Example: "Plan research → Execute search → Evaluate results → Iterate"

### **Create a SERVICE if:**
- ✅ Single-purpose utility
- ✅ Stateless operation
- ✅ Example: "Extract entities from text"

**Rule of Thumb:** If it needs a loop or conditional execution based on results, make it an agent. If it's a single function call, make it a service.

---

## 🏗️ Step 2: Create Agent Structure

Navigate to the agents directory:

```bash
cd backend/app/api/services/agents
mkdir my_agent
cd my_agent
```

Create the following file structure:

```
my_agent/
├── __init__.py
├── my_agent.py                 # Main agent class
├── agent_state.py              # State definition
└── nodes/
    ├── __init__.py
    ├── planner_node.py
    ├── execution_node.py
    └── planner_helpers/        # ✅ If planner uses LLM
        ├── prompt_builder.py
        └── prompts/
            └── planning.md
```

---

## 📝 Step 3: Define State

Create the state TypedDict that will be passed between nodes.

**File:** `agent_state.py`

```python
from typing import TypedDict, Optional, List, Any

class MyAgentState(TypedDict):
    """State for MyAgent workflow"""
    user_message: str
    plan: Optional[str]
    results: Optional[List[Any]]
    error: Optional[str]
```

**Best Practices:**
- Use descriptive field names
- Include Optional types for fields populated during execution
- Document the purpose of each field
- Keep state focused (only what's needed for the workflow)

---

## 🤖 Step 4: Create Agent Class

Implement the main agent class that builds and executes the LangGraph workflow.

**File:** `my_agent.py`

```python
from langgraph.graph import StateGraph, END
from app.api.services.agents.domain_agent_interface import DomainAgentInterface, DomainAgentInput, DomainAgentResult
from .agent_state import MyAgentState
from .nodes.planner_node import planner_node
from .nodes.execution_node import execution_node

class MyAgent(DomainAgentInterface):
    """
    Domain agent for [describe purpose].
    
    Workflow:
    1. Planner Node: Creates execution plan
    2. Execution Node: Executes plan
    3. Returns results
    """
    
    def __init__(self, llm_adapter, correlation_id: str = None):
        self.llm_adapter = llm_adapter
        self.correlation_id = correlation_id
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(MyAgentState)
        
        # Add nodes
        workflow.add_node("planner", planner_node)
        workflow.add_node("execution", execution_node)
        
        # Define edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "execution")
        workflow.add_edge("execution", END)
        
        return workflow.compile()
    
    async def execute(self, input_data: DomainAgentInput) -> DomainAgentResult:
        """Execute agent workflow"""
        initial_state: MyAgentState = {
            "user_message": input_data.query,
            "plan": None,
            "results": None,
            "error": None
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return DomainAgentResult(
            status="success" if not final_state.get("error") else "error",
            content=final_state.get("results"),
            error=final_state.get("error")
        )
```

**Key Points:**
- Implement `DomainAgentInterface` for domain agents
- Build graph in `_build_graph()` method
- Define clear workflow in docstring
- Handle errors gracefully in `execute()`

---

## 🔄 Step 5: Implement Nodes

Create individual node functions that perform specific workflow steps.

### **Planner Node**

**File:** `nodes/planner_node.py`

```python
from ..agent_state import MyAgentState
from .planner_helpers.prompt_builder import build_planning_prompt

async def planner_node(state: MyAgentState, llm_adapter) -> MyAgentState:
    """Create execution plan"""
    
    # Build prompt using pattern
    prompt = build_planning_prompt(
        user_message=state["user_message"]
    )
    
    # Call LLM
    plan = await llm_adapter.ainvoke(prompt)
    
    state["plan"] = plan
    return state
```

### **Prompt Builder (if using LLM)**

**File:** `nodes/planner_helpers/prompt_builder.py`

```python
from pathlib import Path

def build_planning_prompt(user_message: str) -> str:
    """Load planning prompt and inject user message"""
    prompts_dir = Path(__file__).parent / "prompts"
    with open(prompts_dir / "planning.md", 'r') as f:
        template = f.read()
    
    return template.replace("{{USER_MESSAGE}}", user_message)
```

### **Prompt Template**

**File:** `nodes/planner_helpers/prompts/planning.md`

```markdown
[ROLE]
You are a planning assistant.

[TASK: CREATE EXECUTION PLAN]

## User Request
{{USER_MESSAGE}}

## Task
Create a step-by-step plan to fulfill this request.

## Output Format
Return a JSON array of steps:
[
  {"step": 1, "action": "..."},
  {"step": 2, "action": "..."}
]
```

**Best Practices:**
- Follow the prompt asset pattern (`.md` + builder)
- Use `{{PLACEHOLDERS}}` for variables
- Include clear output schema
- Refer to `docs/guides/prompt_writing_guide.md` for detailed prompt structure

---

## 📋 Step 6: Register Agent

Add your agent to the domain agent registry.

**File:** `backend/app/api/services/agents/domain_agent_registry.py`

```python
from .my_agent.my_agent import MyAgent

class DomainAgentRegistry:
    def _register_builtin_agents(self):
        # ... existing agents ...
        
        # Register your new agent
        self.register_agent_factory(
            "my_agent",
            lambda correlation_id=None: MyAgent(
                self.llm_adapter,
                correlation_id=correlation_id
            )
        )
```

**Naming Convention:**
- Use lowercase with underscores: `research_agent`, `productivity_agent`
- Name should describe the domain/capability
- Keep it concise and clear

---

## 🧪 Step 7: Test

Write comprehensive tests for your agent.

**File:** `backend/tests/api/test_my_agent.py`

```python
import pytest
from app.api.services.agents.my_agent.my_agent import MyAgent
from app.api.services.agents.domain_agent_interface import DomainAgentInput

@pytest.mark.asyncio
async def test_my_agent_basic(llm_adapter):
    """Test basic agent execution"""
    agent = MyAgent(llm_adapter)
    
    input_data = DomainAgentInput(
        query="Test query",
        user_id="test-user",
        avatar_id="test-avatar"
    )
    
    result = await agent.execute(input_data)
    
    assert result.status == "success"
    assert result.content is not None

@pytest.mark.asyncio
async def test_my_agent_error_handling(llm_adapter):
    """Test agent error handling"""
    agent = MyAgent(llm_adapter)
    
    input_data = DomainAgentInput(
        query="",  # Empty query should trigger error
        user_id="test-user",
        avatar_id="test-avatar"
    )
    
    result = await agent.execute(input_data)
    
    assert result.status == "error"
    assert result.error is not None
```

**Testing Best Practices:**
- Test happy path (basic execution)
- Test error handling
- Test edge cases
- Mock LLM calls for deterministic tests
- Use fixtures for common setup

**Run tests:**
```bash
# From root directory
poetry run pytest backend/tests/api/test_my_agent.py
```

---

## 📚 Step 8: Document

Create documentation for your agent following the standard structure.

### **During Development:**

**1. Create Spec:**
`docs/specs/spec_my_agent_v1.md`

```markdown
# My Agent Specification v1

## Overview
What the agent does and why it's needed.

## Acceptance Criteria
- Criterion 1
- Criterion 2

## User Stories
As a user, I want to...
```

**2. Create Plan:**
`docs/plans/plan_my_agent_v1.md`

```markdown
# My Agent Implementation Plan v1

## Technical Approach
How we'll build it.

## File Changes
- Create: backend/app/api/services/agents/my_agent/
- Modify: domain_agent_registry.py

## Implementation Steps
1. Step 1
2. Step 2
```

### **After PR Merge:**

**1. Move to Archive:**
```bash
mv docs/specs/spec_my_agent_v1.md docs/archive/
mv docs/plans/plan_my_agent_v1.md docs/archive/
```

**2. Create Guide:**
`docs/guides/my_agent_guide.md`

```markdown
# My Agent Guide

## Purpose
What the agent does.

## How It Works
Architecture and workflow.

## Usage Examples
How to invoke and use it.

## Configuration
Any settings or customizations.
```

---

## ✅ Checklist

Before submitting your agent for review:

**Code:**
- [ ] Agent implements `DomainAgentInterface`
- [ ] State TypedDict defined clearly
- [ ] Nodes follow async pattern
- [ ] Prompts use `.md` + builder pattern
- [ ] Agent registered in `domain_agent_registry.py`
- [ ] Error handling implemented
- [ ] Logging added (use `get_correlated_logger`)

**Tests:**
- [ ] Basic execution test
- [ ] Error handling test
- [ ] Edge case tests
- [ ] All tests pass locally

**Documentation:**
- [ ] Spec created in `docs/specs/`
- [ ] Plan created in `docs/plans/`
- [ ] Code comments added
- [ ] Docstrings complete

**Code Quality:**
- [ ] Types checked (`tsc` if touching frontend)
- [ ] Linting passed (`prettier`)
- [ ] No hardcoded values (use config)
- [ ] Follows existing patterns

---

## 🎓 Advanced Topics

### **Conditional Routing**

Use conditional edges for dynamic workflow:

```python
def should_retry(state: MyAgentState) -> str:
    """Decide whether to retry or finish"""
    if state.get("error") and state.get("retry_count", 0) < 3:
        return "retry"
    return "finish"

workflow.add_conditional_edges(
    "execution",
    should_retry,
    {
        "retry": "planner",
        "finish": END
    }
)
```

### **Iterative Refinement**

Implement loops for iterative improvement:

```python
workflow.add_node("evaluator", evaluator_node)
workflow.add_edge("execution", "evaluator")

def should_continue(state: MyAgentState) -> str:
    if state.get("quality_score", 0) > 0.8:
        return "finish"
    return "refine"

workflow.add_conditional_edges(
    "evaluator",
    should_continue,
    {
        "finish": END,
        "refine": "planner"
    }
)
```

### **Tool Calling**

Integrate external tools:

```python
from langchain.tools import Tool

async def execution_node(state: MyAgentState, llm_adapter) -> MyAgentState:
    """Execute plan with tools"""
    
    tools = [
        Tool(name="search", func=search_func),
        Tool(name="calculator", func=calc_func)
    ]
    
    result = await llm_adapter.ainvoke_with_tools(
        prompt=state["plan"],
        tools=tools
    )
    
    state["results"] = result
    return state
```

---

## 📖 Related Documentation

- **AGENTS.md:** Project-wide architecture guide
- **Prompt Writing Guide:** `docs/guides/prompt_writing_guide.md`
- **Prompt Asset Pattern:** `docs/Documentation/prompt_asset_management_pattern.md`
- **Testing Guide:** `docs/guides/TESTING_GUIDE.md`

---

## 🚀 Example Agents to Study

### **Simple Agent: Wealth Agent**
`backend/app/api/services/agents/wealth_agent/`
- Simple linear workflow
- Good starting point

### **Complex Agent: Research Agent**
`backend/app/api/services/agents/research_agent/`
- Iterative refinement
- Tool calling
- Conditional routing

### **Multi-Provider Agent: Productivity Agent**
`backend/app/api/services/agents/productivity_agent/`
- Provider abstraction
- Complex state management
- Multiple tool integrations

---

**Questions?** Check the example agents or ask the development team! 🚀

