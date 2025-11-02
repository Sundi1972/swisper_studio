#!/bin/bash
# Create Phase 2 test data for "Production Swisper" project
# Demonstrates: nested observations, LLM telemetry, cost tracking, different observation types

set -e

API_KEY="dev-api-key-change-in-production"
BASE_URL="http://localhost:8001/api/v1"

echo "🚀 Creating Phase 2 Test Data for 'Production Swisper'"
echo "=================================================="

# Get Production Swisper project ID
echo "📋 Fetching Production Swisper project..."
PROJECT_RESPONSE=$(curl -s -X GET "$BASE_URL/projects?page=1&limit=100" \
  -H "X-API-Key: $API_KEY")

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$PROJECT_ID" ]; then
  echo "❌ No projects found. Creating Production Swisper project..."
  PROJECT_CREATE=$(curl -s -X POST "$BASE_URL/projects" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Production Swisper",
      "swisper_url": "http://localhost:8000",
      "swisper_api_key": "prod-swisper-key",
      "description": "Production environment"
    }')
  PROJECT_ID=$(echo "$PROJECT_CREATE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
fi

echo "✅ Using project: $PROJECT_ID"

# Create trace
TRACE_ID="trace-$(date +%s)"
echo ""
echo "📝 Creating trace: $TRACE_ID"

curl -s -X POST "$BASE_URL/traces" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$TRACE_ID\",
    \"project_id\": \"$PROJECT_ID\",
    \"name\": \"User Request: What's my next meeting?\",
    \"user_id\": \"user_123\",
    \"session_id\": \"session_456\",
    \"tags\": [\"calendar\", \"productivity\"],
    \"input\": {\"message\": \"What's my next meeting?\"}
  }" > /dev/null

echo "✅ Trace created"

# Create nested observations showing Phase 2 features

echo ""
echo "🌳 Creating observation tree..."

# Root: Global Supervisor Agent
SUPERVISOR_ID="supervisor-$(date +%s)"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
END_TIME=$(date -u -d "+5 seconds" +%Y-%m-%dT%H:%M:%SZ)

echo "  └─ Global Supervisor (AGENT)"
curl -s -X POST "$BASE_URL/observations" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$SUPERVISOR_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"type\": \"AGENT\",
    \"name\": \"global_supervisor\",
    \"start_time\": \"$NOW\",
    \"end_time\": \"$END_TIME\",
    \"input\": {\"user_message\": \"What's my next meeting?\"},
    \"output\": {\"response\": \"Your next meeting is Team Standup at 2pm\"}
  }" > /dev/null

sleep 1

# Child 1: Intent Classification (GENERATION with LLM)
INTENT_ID="intent-$(date +%s)"
INTENT_START=$(date -u -d "+1 second" +%Y-%m-%dT%H:%M:%SZ)
INTENT_END=$(date -u -d "+2 seconds" +%Y-%m-%dT%H:%M:%SZ)
INTENT_COMPLETION=$(date -u -d "+1.5 seconds" +%Y-%m-%dT%H:%M:%SZ)

echo "     ├─ Intent Classification (GENERATION with GPT-4)"
curl -s -X POST "$BASE_URL/observations" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$INTENT_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"parent_observation_id\": \"$SUPERVISOR_ID\",
    \"type\": \"GENERATION\",
    \"name\": \"intent_classification\",
    \"start_time\": \"$INTENT_START\",
    \"end_time\": \"$INTENT_END\",
    \"completion_start_time\": \"$INTENT_COMPLETION\",
    \"model\": \"gpt-4-turbo\",
    \"model_parameters\": {\"temperature\": 0.7, \"max_tokens\": 500},
    \"prompt_tokens\": 150,
    \"completion_tokens\": 50,
    \"input\": {\"message\": \"What's my next meeting?\"},
    \"output\": {\"intent\": \"calendar_query\", \"confidence\": 0.95}
  }" > /dev/null

sleep 1

# Child 2: Memory Node (SPAN)
MEMORY_ID="memory-$(date +%s)"
MEMORY_START=$(date -u -d "+2 seconds" +%Y-%m-%dT%H:%M:%SZ)
MEMORY_END=$(date -u -d "+2.5 seconds" +%Y-%m-%dT%H:%M:%SZ)

echo "     ├─ Memory Retrieval (SPAN)"
curl -s -X POST "$BASE_URL/observations" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$MEMORY_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"parent_observation_id\": \"$SUPERVISOR_ID\",
    \"type\": \"SPAN\",
    \"name\": \"memory_node\",
    \"start_time\": \"$MEMORY_START\",
    \"end_time\": \"$MEMORY_END\",
    \"input\": {\"query\": \"calendar events\"},
    \"output\": {\"events_found\": 3}
  }" > /dev/null

sleep 1

# Child 3: Productivity Agent (nested with own children)
PRODUCTIVITY_ID="productivity-$(date +%s)"
PROD_START=$(date -u -d "+2.5 seconds" +%Y-%m-%dT%H:%M:%SZ)
PROD_END=$(date -u -d "+4.5 seconds" +%Y-%m-%dT%H:%M:%SZ)

echo "     └─ Productivity Agent (AGENT)"
curl -s -X POST "$BASE_URL/observations" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$PRODUCTIVITY_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"parent_observation_id\": \"$SUPERVISOR_ID\",
    \"type\": \"AGENT\",
    \"name\": \"productivity_agent\",
    \"start_time\": \"$PROD_START\",
    \"end_time\": \"$PROD_END\",
    \"input\": {\"task\": \"fetch calendar events\"},
    \"output\": {\"status\": \"success\"}
  }" > /dev/null

sleep 1

# Grandchild 1: Calendar Tool Call
CALENDAR_ID="calendar-$(date +%s)"
CAL_START=$(date -u -d "+3 seconds" +%Y-%m-%dT%H:%M:%SZ)
CAL_END=$(date -u -d "+3.5 seconds" +%Y-%m-%dT%H:%M:%SZ)

echo "        ├─ Calendar API Call (TOOL)"
curl -s -X POST "$BASE_URL/observations" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$CALENDAR_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"parent_observation_id\": \"$PRODUCTIVITY_ID\",
    \"type\": \"TOOL\",
    \"name\": \"get_calendar_events\",
    \"start_time\": \"$CAL_START\",
    \"end_time\": \"$CAL_END\",
    \"input\": {\"start_date\": \"2025-11-02\", \"end_date\": \"2025-11-02\"},
    \"output\": {\"events\": [{\"title\": \"Team Standup\", \"time\": \"14:00\"}]}
  }" > /dev/null

sleep 1

# Grandchild 2: Response Generation (LLM)
RESPONSE_ID="response-$(date +%s)"
RESP_START=$(date -u -d "+3.5 seconds" +%Y-%m-%dT%H:%M:%SZ)
RESP_END=$(date -u -d "+4.5 seconds" +%Y-%m-%dT%H:%M:%SZ)
RESP_COMPLETION=$(date -u -d "+4 seconds" +%Y-%m-%dT%H:%M:%SZ)

echo "        └─ Response Generation (GENERATION with Claude)"
curl -s -X POST "$BASE_URL/observations" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$RESPONSE_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"parent_observation_id\": \"$PRODUCTIVITY_ID\",
    \"type\": \"GENERATION\",
    \"name\": \"generate_response\",
    \"start_time\": \"$RESP_START\",
    \"end_time\": \"$RESP_END\",
    \"completion_start_time\": \"$RESP_COMPLETION\",
    \"model\": \"claude-3-sonnet-20240229\",
    \"model_parameters\": {\"temperature\": 0.8, \"max_tokens\": 1000},
    \"prompt_tokens\": 300,
    \"completion_tokens\": 100,
    \"input\": {\"calendar_events\": [{\"title\": \"Team Standup\", \"time\": \"14:00\"}]},
    \"output\": {\"response\": \"Your next meeting is Team Standup at 2pm\"}
  }" > /dev/null

sleep 1

# Create one more observation with ERROR status
ERROR_ID="error-$(date +%s)"
ERROR_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo ""
echo "⚠️  Creating observation with ERROR status..."
curl -s -X POST "$BASE_URL/observations" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$ERROR_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"parent_observation_id\": \"$SUPERVISOR_ID\",
    \"type\": \"GENERATION\",
    \"name\": \"failed_llm_call\",
    \"start_time\": \"$ERROR_TIME\",
    \"end_time\": \"$ERROR_TIME\",
    \"model\": \"gpt-4\",
    \"level\": \"ERROR\",
    \"status_message\": \"API rate limit exceeded (429)\",
    \"prompt_tokens\": 0,
    \"completion_tokens\": 0
  }" > /dev/null

echo ""
echo "✅ Test data created successfully!"
echo ""
echo "📊 Summary:"
echo "  - Trace ID: $TRACE_ID"
echo "  - Project: Production Swisper"
echo "  - Observations: 6 total"
echo "    - 1 root (Global Supervisor)"
echo "    - 4 children (Intent, Memory, Productivity, Error)"
echo "    - 2 grandchildren (Calendar Tool, Response Generation)"
echo ""
echo "💰 Expected Costs:"
echo "  - Intent (GPT-4-turbo): 150 + 50 tokens = \$0.003000"
echo "  - Response (Claude-3-Sonnet): 300 + 100 tokens = \$0.002400"
echo "  - Total: \$0.005400"
echo ""
echo "🔗 View in UI:"
echo "  1. Go to: http://localhost:3000"
echo "  2. Login with API key"
echo "  3. Open 'Production Swisper' project"
echo "  4. Click 'Tracing' in sidebar"
echo "  5. Click the trace: 'User Request: What's my next meeting?'"
echo ""
echo "✨ You should see:"
echo "  - Observation tree with 3 levels of nesting"
echo "  - Cost badges on LLM calls"
echo "  - Token counts displayed"
echo "  - Model names shown"
echo "  - ERROR badge on failed observation"
echo "  - Duration calculated for each observation"
echo ""

