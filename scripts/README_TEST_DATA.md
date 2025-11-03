# Test Data Generator

## Purpose

Create realistic test traces with state transitions for testing SwisperStudio's Phase 2.5 features.

## Prerequisites

```bash
# 1. Backend running
docker compose up -d

# 2. You have a test project created
# Get your PROJECT_ID from: http://localhost:3000/projects
```

## Configuration

Edit `create_test_traces.py` and update:

```python
PROJECT_ID = "your-project-id-here"  # From SwisperStudio
API_KEY = "test-api-key"              # Your API key
```

## Run

```bash
# From project root
cd /root/projects/swisper_studio

# Install dependencies (if not already installed)
pip install httpx

# Edit the script - update PROJECT_ID and API_KEY
nano scripts/create_test_traces.py
# Or use your text editor to update:
# - PROJECT_ID = "your-actual-project-id"
# - API_KEY = "test-api-key"

# Run script
python scripts/create_test_traces.py
```

**IMPORTANT:** The script creates realistic state transitions where:
- Each node receives state from previous node
- Each node adds new fields to state
- State "accumulates" through the workflow
- This triggers "STATE CHANGED" indicators on EACH node!

## What It Creates

**One comprehensive trace with:**
1. Global Supervisor (SPAN) - shows state accumulation
2. Intent Classification (GENERATION) - shows LLM prompt/response with state change
3. Memory Node (SPAN) - shows state enrichment (adds memory_domain)
4. Productivity Agent (AGENT) - shows agent execution
5. Get Calendar Events (TOOL) - shows tool call arguments and response
6. UI Node (GENERATION) - shows final formatting with markdown prompt

**Each observation shows:**
- ✅ State before/after (demonstrates state transitions)
- ✅ LLM prompts (for GENERATION nodes)
- ✅ Tool calls (for TOOL nodes)
- ✅ Realistic GlobalSupervisorState structure from Swisper
- ✅ "STATE CHANGED" indicator in tree view

## View Results

After running:
```
http://localhost:3000/projects/{PROJECT_ID}/traces/{TRACE_ID}
```

The script will print the URL.

## Test Scenarios

**Test these features:**
1. Click observations in tree → details panel updates
2. See "STATE CHANGED" chip for observations that modify state
3. See LLM prompts rendered as markdown
4. See tool call arguments and responses
5. See state diff (green=added, red=removed)
6. Resize panels (drag divider between tree and details)
7. Copy prompts/responses to clipboard
8. Scroll through large state objects

