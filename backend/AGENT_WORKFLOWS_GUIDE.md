# Agent Workflow Execution Guide

This guide explains how to set up and execute workflows through agents in the Education Intelligence & Content Orchestration Platform.

## Overview

The agent-workflow execution system enables:
- **Agent Assignment**: Assign workflows to specific agents for execution
- **Workflow Execution**: Trigger workflows through agent endpoints
- **Execution Tracking**: Monitor agent executions with full audit trail
- **Automation Support**: Configure workflows for automatic agent execution

## Architecture

### Components

1. **Agent Registry** (`api/agents.py`)
   - Hardcoded registry of 13 system agents
   - Tracks agent capabilities and usage statistics
   - Provides agent status and workflow associations

2. **Workflow System** (`workflows/`)
   - LangGraph-based workflow definitions
   - State management for multi-step processes
   - Human checkpoint support

3. **Agent Workflow Executor** (`services/agent_workflow_executor.py`)
   - Executes workflows on behalf of agents
   - Manages permissions and access control
   - Tracks execution history

4. **Agent Workflows API** (`api/agent_workflows.py`)
   - REST endpoints for agent-workflow management
   - Workflow assignment and execution

## Database Changes

### Workflow Model Updates

Three new fields added to the `Workflow` table:

```python
assigned_agents: JSON          # List of agent IDs that can execute this workflow
execution_trigger: String(50)  # "manual", "event-driven", or "scheduled"
is_automatable: Boolean        # Can be auto-executed by agents
```

### AgentRun Model Update

Updated field name:
- Changed: `execution_id` → `workflow_execution_id` (for clarity)

### Migration

Run the migration script to apply changes:

```bash
cd backend
python migrate_add_agent_workflows.py
```

## API Endpoints

### 1. Assign Workflow to Agent

**Endpoint**: `POST /api/v1/agent-workflows/assign`

**Request**:
```json
{
  "agent_id": "extract_requirements",
  "workflow_id": "workflow-uuid-123",
  "auto_execute": false
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Agent extract_requirements assigned to workflow",
  "workflow_id": "workflow-uuid-123",
  "agent_id": "extract_requirements"
}
```

### 2. Get Agent's Assigned Workflows

**Endpoint**: `GET /api/v1/agent-workflows/{agent_id}/workflows`

**Response**:
```json
[
  {
    "workflow_id": "workflow-uuid-123",
    "workflow_name": "Workforce Alignment",
    "description": "Aligns course content with workforce skills",
    "agent_id": "extract_requirements",
    "is_automatable": false,
    "execution_trigger": "manual"
  }
]
```

### 3. Execute Workflow as Agent

**Endpoint**: `POST /api/v1/agent-workflows/execute`

**Request**:
```json
{
  "agent_id": "extract_requirements",
  "workflow_id": "workflow-uuid-123",
  "input_data": {
    "program_id": "prog_001",
    "program_name": "Computer Science",
    "course_ids": ["course_001", "course_002"],
    "input_package_id": "pkg_001",
    "input_package_format": "zip",
    "input_skill_framework_id": "framework_001"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "execution_id": "exec-uuid-456",
  "workflow_id": "workflow-uuid-123",
  "workflow_name": "Workforce Alignment",
  "agent_id": "extract_requirements",
  "result": {
    "workflow_status": "completed",
    "completed_nodes": ["validate_request_and_access", "extract_requirements"],
    "extracted_learning_objectives": [...]
  }
}
```

### 4. Unassign Workflow from Agent

**Endpoint**: `DELETE /api/v1/agent-workflows/unassign`

**Request**:
```json
{
  "agent_id": "extract_requirements",
  "workflow_id": "workflow-uuid-123"
}
```

### 5. Get Workflow's Assigned Agents

**Endpoint**: `GET /api/v1/agent-workflows/{workflow_id}/agents`

**Response**:
```json
{
  "workflow_id": "workflow-uuid-123",
  "workflow_name": "Workforce Alignment",
  "assigned_agents": ["extract_requirements", "map_workforce_skills"],
  "agent_count": 2,
  "is_automatable": true
}
```

## Available Agents

All agents from the registry can be assigned workflows:

| Agent ID | Name | Type | Description |
|----------|------|------|-------------|
| `validate_request_and_access` | Request Validator | validation | Validates workflow request, tenant context, and permissions |
| `inspect_package_contents` | Package Inspector | validation | Inspects course package contents and validates format |
| `extract_requirements` | Requirements Extractor | ai_powered | Extracts institution requirements using Claude AI |
| `ingest_and_normalize_course_materials` | Course Ingestion Engine | data_processing | Ingests and normalizes course materials from packages |
| `retrieve_authorized_context` | Context Retriever | retrieval | Retrieves authorized context for analysis |
| `map_workforce_skills` | Skill Mapper | ai_powered | Maps workforce skills to course content using AI |
| `calculate_coverage_and_gaps` | Gap Analyzer | analysis | Calculates skill coverage and identifies gaps |
| `draft_recommendations` | Recommendation Engine | ai_powered | Drafts course improvement recommendations |
| `generate_course_updates` | Content Generator | data_processing | Generates updated course materials |
| `accessibility_check` | Accessibility Auditor | compliance | Runs accessibility audit on course materials |
| `content_governance` | Content Governance Agent | compliance | Checks indexed content quality and recommends human approval |
| `persist_artifacts` | Data Persister | storage | Persists workflow results to database |
| `emit_audit_events` | Audit Logger | compliance | Emits audit events for compliance tracking |

## Usage Examples

### Python Example

```python
import asyncio
from services.agent_workflow_executor import AgentWorkflowExecutor
from database.db import SessionLocal

async def run_workflow_as_agent():
    db = SessionLocal()
    
    result = await AgentWorkflowExecutor.execute_workflow_for_agent(
        agent_id="extract_requirements",
        workflow_id="workflow-uuid-123",
        tenant_id="tenant-uuid-789",
        workflow_input={
            "program_id": "prog_001",
            "program_name": "Data Science",
            "course_ids": ["course_001"],
            "input_package_id": "pkg_001",
            "input_package_format": "zip",
            "input_skill_framework_id": "framework_001",
        },
        db=db
    )
    
    print(f"Execution ID: {result['execution_id']}")
    print(f"Status: {result['status']}")
    
    db.close()

# Run the async function
asyncio.run(run_workflow_as_agent())
```

### cURL Example

```bash
# Assign workflow to agent
curl -X POST "http://localhost:8000/api/v1/agent-workflows/assign" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "agent_id": "extract_requirements",
    "workflow_id": "workflow-uuid-123",
    "auto_execute": false
  }'

# Get agent workflows
curl -X GET "http://localhost:8000/api/v1/agent-workflows/extract_requirements/workflows" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Execute workflow as agent
curl -X POST "http://localhost:8000/api/v1/agent-workflows/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "agent_id": "extract_requirements",
    "workflow_id": "workflow-uuid-123",
    "input_data": {
      "program_id": "prog_001",
      "program_name": "Computer Science",
      "course_ids": ["course_001"],
      "input_package_id": "pkg_001",
      "input_package_format": "zip",
      "input_skill_framework_id": "framework_001"
    }
  }'
```

### JavaScript/Frontend Example

```javascript
// Get agent workflows
async function getAgentWorkflows(agentId) {
  const response = await fetch(
    `/api/v1/agent-workflows/${agentId}/workflows`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.json();
}

// Execute workflow as agent
async function executeWorkflowAsAgent(agentId, workflowId, inputData) {
  const response = await fetch('/api/v1/agent-workflows/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      agent_id: agentId,
      workflow_id: workflowId,
      input_data: inputData
    })
  });
  return response.json();
}

// Assign workflow to agent
async function assignWorkflowToAgent(agentId, workflowId) {
  const response = await fetch('/api/v1/agent-workflows/assign', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      agent_id: agentId,
      workflow_id: workflowId,
      auto_execute: false
    })
  });
  return response.json();
}
```

## Execution Flow

1. **Assignment**: Admin assigns a workflow to one or more agents
2. **Validation**: System verifies agent has permission to execute workflow
3. **Execution**: Workflow graph is invoked with agent as initiator
4. **Tracking**: All agent runs and workflow executions are recorded
5. **Completion**: Results are stored with full audit trail

## Monitoring

### Check Execution History

```python
from database.models import WorkflowExecution, AgentRun
from database.db import SessionLocal

db = SessionLocal()

# Get workflow executions by agent
agent_executions = db.query(WorkflowExecution).join(
    AgentRun,
    WorkflowExecution.id == AgentRun.workflow_execution_id
).filter(
    AgentRun.agent_name == "extract_requirements"
).all()

for execution in agent_executions:
    print(f"Execution: {execution.id}")
    print(f"Status: {execution.status}")
    print(f"Started: {execution.started_at}")
    print(f"Completed: {execution.completed_at}")
```

### Check Agent Usage

```python
from database.models import AgentRun
from sqlalchemy import func

# Count agent runs
agent_run_count = db.query(func.count(AgentRun.id)).filter(
    AgentRun.agent_name == "extract_requirements",
    AgentRun.status == "completed"
).scalar()

print(f"Agent executions completed: {agent_run_count}")
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Workflow not found | Invalid workflow ID | Verify workflow ID exists in tenant |
| Agent not assigned | Agent hasn't been assigned to workflow | Use assign endpoint first |
| Workflow not active | Workflow status is not "active" | Activate workflow before execution |
| Permission denied | Tenant/agent mismatch | Verify tenant context is correct |
| Input validation failed | Missing required fields | Provide all required input parameters |

## Testing

Run the test suite:

```bash
cd backend
python test_agent_workflows.py
```

## Best Practices

1. **Assign Before Execute**: Always assign a workflow to an agent before attempting execution
2. **Input Validation**: Ensure all required input fields are provided
3. **Tenant Context**: Maintain proper tenant isolation for multi-tenant deployments
4. **Error Handling**: Implement retry logic for transient failures
5. **Monitoring**: Track execution times and success rates by agent
6. **Automation**: Use `is_automatable` flag only for trusted, well-tested workflows
7. **Permissions**: Restrict agent assignment to authorized users only

## Future Enhancements

Planned features:
- [ ] Event-driven workflow triggers
- [ ] Scheduled workflow execution (cron-based)
- [ ] Workflow result callbacks
- [ ] Agent-to-agent workflow handoff
- [ ] Conditional agent selection
- [ ] Workflow retry policies
- [ ] Agent capability versioning
