# Workflow Agent Execution Setup Guide

## Overview
All 13 workflow agents have been integrated and configured to execute automatically when workflows are triggered. This document explains the complete setup.

## Agents Configured

### Phase 1: Validation & Setup (2 Agents)
1. **Request Validator** - Validates workflow request, tenant context, and user permissions
2. **Package Inspector** - Inspects course package contents and validates format

### Phase 2: Requirements Extraction (1 Agent)
3. **Requirements Extractor** *(AI-Powered)* - Extracts institution requirements using AWS Bedrock Claude

### Phase 3: Course Ingestion (1 Agent)
4. **Course Ingestion Engine** - Ingests and normalizes course materials from packages

### Phase 4: Analysis & Mapping (3 Agents)
5. **Context Retriever** - Retrieves authorized context for analysis
6. **Skill Mapper** *(AI-Powered)* - Maps workforce skills to course content using AWS Bedrock
7. **Gap Analyzer** - Calculates skill coverage and identifies gaps

### Phase 5+: Recommendations & Finalization (6 Agents)
8. **Recommendation Engine** *(AI-Powered)* - Generates curriculum improvement recommendations
9. **Content Generator** - Generates updated course materials based on recommendations
10. **Accessibility Auditor** - Runs accessibility audit on course materials
11. **Validator** - Validates export package format and structure
12. **Data Persister** - Persists workflow results to database
13. **Audit Logger** - Emits audit events for compliance tracking

## Architecture

### Workflow Execution Flow

```
POST /v1/workforce-alignment/workflows
    ↓
[API: create_workflow()]
    ↓
1. Validate Input Parameters
2. Create WorkforceAlignmentState
3. Save Workflow Definition to Database
4. Execute Workflow Asynchronously
    ↓
[Workflow Graph Execution]
    ↓
validate_request_and_access
    ↓
inspect_package_contents
    ↓
extract_requirements (🤖 AI)
    ↓
[Human Checkpoint: Requirements Confirmation]
    ↓
ingest_and_normalize_course_materials
    ↓
[Human Checkpoint: Course Structure Review]
    ↓
retrieve_authorized_context
    ↓
map_workforce_skills (🤖 AI)
    ↓
calculate_coverage_and_gaps
    ↓
[Human Checkpoint: Mapping Review]
    ↓
draft_recommendations (🤖 AI)
    ↓
[Human Checkpoint: Recommendations Approval]
    ↓
generate_course_updates
    ↓
accessibility_check
    ↓
[Human Checkpoint: Accessibility Review]
    ↓
validate_export_package
    ↓
[Human Checkpoint: Final Approval]
    ↓
persist_artifacts
    ↓
emit_audit_events
    ↓
END
    ↓
Save WorkflowExecution & AgentRun records
```

## How Agents Are Tracked

### 1. Agent Execution Service
**File:** `backend/services/agent_execution_service.py`

When each agent executes:
```
start_agent_execution(agent_name, execution_id)
    ↓
update_agent_progress(10%, 30%, 80%, 100%)
    ↓
complete_agent_execution()
```

### 2. Agent Run Records
**Database Table:** `agent_runs`

Each agent execution creates a record:
- `id`: Unique identifier
- `tenant_id`: Multi-tenant support
- `execution_id`: Links to workflow execution
- `agent_name`: Agent identifier (e.g., "extract_requirements")
- `agent_type`: Type (validation, ai_powered, data_processing, etc.)
- `status`: pending → running → completed/failed
- `input_data`: Data passed to agent
- `output_data`: Agent results
- `started_at`: Execution start time
- `completed_at`: Execution completion time

### 3. Agent Box UI Tracking
**Frontend:** `frontend/components/Common/AgentBox.tsx`

Displays real-time execution:
- Agent name
- Orange progress bar (0-100%)
- Progress percentage
- Auto-hides when execution completes

**Polling Mechanism:** Frontend polls `/api/v1/agents/execution-status` every 500ms

## How Workflows Use Agents

### 1. Workflow Definition
Workflows stored in database with agent definitions:
```json
{
  "agents": [
    {"id": "validate_request_and_access", "name": "validate_request_and_access"},
    {"id": "extract_requirements", "name": "extract_requirements"},
    {"id": "map_workforce_skills", "name": "map_workforce_skills"},
    ...
  ]
}
```

### 2. Orchestrator Execution
**File:** `backend/orchestrator/orchestrator.py`

Each agent execution:
1. Calls `start_agent_execution(agent_name)`
2. Updates progress: 10%, 30%, 80%, 100%
3. Creates AgentRun database record
4. Calls `complete_agent_execution()`

### 3. Workflow Graph Integration
**File:** `backend/workflows/workforce_alignment_graph.py`

All 13 agents connected in LangGraph StateGraph:
- Entry point: `validate_request_and_access`
- 5 Human checkpoints with decision logic
- Exit point: `emit_audit_events`

## Starting a Workflow

### Option 1: Via API (Recommended)

**Endpoint:** `POST /v1/workforce-alignment/workflows`

**Request:**
```json
{
  "program_id": "prog-001",
  "program_name": "Bachelor of Computer Science",
  "course_ids": ["course-101", "course-102"],
  "input_package_id": "pkg-001",
  "input_package_format": "imscc",
  "input_skill_framework_id": "framework-001",
  "input_style_guide_id": "guide-001"
}
```

**Response:**
```json
{
  "status": "success",
  "workflow_id": "exec-abc123",
  "message": "Workflow execution started with all agents",
  "agents_count": 13
}
```

**What Happens:**
1. Workflow execution starts asynchronously
2. 13 agents execute in sequence
3. AI agents (3) call AWS Bedrock Claude
4. Human checkpoints pause for user decisions
5. AgentRun records created for each agent
6. Agent Box displays progress in sidebar
7. Workflow completes and saves results

### Option 2: Via cURL

```bash
curl -X POST http://localhost:8000/v1/workforce-alignment/workflows \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "program_id": "prog-001",
    "program_name": "Test Program",
    "course_ids": ["course-1"],
    "input_package_id": "pkg-001",
    "input_package_format": "imscc",
    "input_skill_framework_id": "framework-001"
  }'
```

## Monitoring Agent Execution

### 1. Agent Box in Sidebar
- Shows current executing agent
- Orange progress bar
- Auto-updates every 500ms
- Disappears when complete

### 2. Agents Page Workflow Column
**URL:** `http://localhost:3002/agents`

Shows which workflows use each agent:
- ✅ Agent: "Skill Mapper" → Workflows: ["Alignment Workflow - CS Program"]
- ✅ Agent: "Requirements Extractor" → Workflows: ["Alignment Workflow - CS Program"]

### 3. AI Statistics
**URL:** `http://localhost:3002/agents?tab=ai-statistics`

Shows:
- Total requests: Number of agent executions
- Total tokens: Input + output tokens used
- Estimated cost: Based on AWS Bedrock pricing
- Provider: AWS Bedrock
- Models: Claude Opus 5 Sonnet

### 4. Database Records
**Query all agent executions:**
```sql
SELECT * FROM agent_runs 
WHERE tenant_id = 'tenant-xyz'
ORDER BY started_at DESC;
```

**Get workflow execution details:**
```sql
SELECT 
  we.id, 
  we.status, 
  we.started_at, 
  we.completed_at,
  COUNT(ar.id) as agent_count
FROM workflow_executions we
LEFT JOIN agent_runs ar ON we.id = ar.execution_id
WHERE we.tenant_id = 'tenant-xyz'
GROUP BY we.id
ORDER BY we.started_at DESC;
```

## Key Features Implemented

✅ **All 13 Agents Registered**
- Each agent has metadata and status tracking

✅ **Agent Execution Tracking**
- Every agent execution creates an AgentRun record
- Progress tracked: 10% → 30% → 80% → 100%
- Real-time UI updates via Agent Box

✅ **AI-Powered Agents (3)**
- Requirements Extractor
- Skill Mapper
- Recommendation Engine
- All use AWS Bedrock Claude models

✅ **Human Checkpoints (5)**
- Requirements confirmation
- Course structure review
- Mapping & gap review
- Recommendations approval
- Accessibility review
- Final approval

✅ **Workflow Persistence**
- Workflows stored in database
- Execution history preserved
- Audit trail via emit_audit_events agent

✅ **Error Handling**
- Agent failures captured
- Error messages logged
- Workflow status set to "failed"
- Async execution with proper error handling

## Testing the Setup

### 1. Verify All Agents Load
```bash
curl http://localhost:8000/api/v1/agents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Should return 13 agents with all details.

### 2. Start a Workflow
```bash
curl -X POST http://localhost:8000/v1/workforce-alignment/workflows \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "program_id": "test-prog",
    "program_name": "Test Program",
    "course_ids": ["test-course"],
    "input_package_id": "test-pkg",
    "input_package_format": "imscc",
    "input_skill_framework_id": "test-framework"
  }'
```

### 3. Monitor Execution
- Check Agent Box in sidebar for real-time progress
- Check `/api/v1/agents/execution-status` for current agent
- Check database `agent_runs` table for records

### 4. View Results
- Agents page shows workflow assignments
- AI statistics shows token usage
- Execution history in database

## Troubleshooting

### Workflow Not Starting
- Check AWS credentials in `.env`
- Verify Bedrock models are enabled in AWS console
- Check backend logs for errors
- Verify database connection

### Agents Not Showing in "Workflows" Column
- Ensure workflow is created with agent definitions
- Check database `workflow_executions` and `agent_runs` tables
- Verify agent_name matches registered agent IDs

### Agent Box Not Appearing
- Check if workflow is actually executing
- Verify polling endpoint: `/api/v1/agents/execution-status`
- Check browser console for errors
- Verify WebSocket/polling connectivity

### AI Agents Failing
- Check AWS credentials and region
- Verify Bedrock models are enabled
- Check AWS Bedrock service limits
- Review error messages in logs

## Database Schema

### workflow_executions
```sql
CREATE TABLE workflow_executions (
  id VARCHAR(36) PRIMARY KEY,
  tenant_id VARCHAR(36) NOT NULL,
  workflow_id VARCHAR(36),
  status VARCHAR(50),  -- pending, running, completed, failed
  input_data JSON,
  output_data JSON,
  error_message TEXT,
  started_at DATETIME,
  completed_at DATETIME,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);
```

### agent_runs
```sql
CREATE TABLE agent_runs (
  id VARCHAR(36) PRIMARY KEY,
  tenant_id VARCHAR(36) NOT NULL,
  execution_id VARCHAR(36) NOT NULL,
  agent_name VARCHAR(255),
  agent_type VARCHAR(100),
  status VARCHAR(50),
  input_data JSON,
  output_data JSON,
  error_message TEXT,
  started_at DATETIME,
  completed_at DATETIME,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  FOREIGN KEY (execution_id) REFERENCES workflow_executions(id)
);
```

## Summary

All 13 workflow agents are now fully integrated and ready to execute:

1. ✅ Agents registered in database
2. ✅ Workflow graph connects all agents
3. ✅ API endpoint triggers workflow execution
4. ✅ Async execution with proper error handling
5. ✅ Real-time tracking via Agent Box
6. ✅ Database records for audit trail
7. ✅ AI agents using AWS Bedrock
8. ✅ Human checkpoints for approvals
9. ✅ Complete workflow state management

**Start a workflow now:** Use the `POST /v1/workforce-alignment/workflows` endpoint!
