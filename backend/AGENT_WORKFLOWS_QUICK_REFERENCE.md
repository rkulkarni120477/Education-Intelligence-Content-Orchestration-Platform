# Agent Workflows - Quick Reference

## Files Overview

| File | Purpose | Status |
|------|---------|--------|
| `services/agent_workflow_executor.py` | Core executor service | ✅ Created |
| `api/agent_workflows.py` | API routes for agent-workflow management | ✅ Created |
| `database/models.py` | Workflow model updates | ✅ Modified |
| `api/agents.py` | Enhanced agents API | ✅ Modified |
| `api_routes.py` | Router integration | ✅ Modified |
| `migrate_add_agent_workflows.py` | Database migration script | ✅ Created |
| `test_agent_workflows.py` | Test suite | ✅ Created |
| `AGENT_WORKFLOWS_GUIDE.md` | Complete user guide | ✅ Created |
| `AGENT_WORKFLOWS_IMPLEMENTATION.md` | Implementation details | ✅ Created |

## Database Changes

### New Workflow Columns
```sql
ALTER TABLE workflows ADD COLUMN assigned_agents JSON DEFAULT '[]';
ALTER TABLE workflows ADD COLUMN execution_trigger VARCHAR(50) DEFAULT 'manual';
ALTER TABLE workflows ADD COLUMN is_automatable BOOLEAN DEFAULT FALSE;
```

### AgentRun Column Rename
```sql
-- execution_id → workflow_execution_id
ALTER TABLE agent_runs ADD COLUMN workflow_execution_id VARCHAR(36);
UPDATE agent_runs SET workflow_execution_id = execution_id;
```

## API Endpoints

### Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/agent-workflows/assign` | Assign workflow to agent |
| DELETE | `/v1/agent-workflows/unassign` | Remove assignment |
| POST | `/v1/agent-workflows/execute` | Execute workflow as agent |
| GET | `/v1/agent-workflows/{agent_id}/workflows` | List agent's workflows |
| GET | `/v1/agent-workflows/{workflow_id}/agents` | List workflow's agents |

## Core Classes & Methods

### AgentWorkflowExecutor Service

```python
from services.agent_workflow_executor import AgentWorkflowExecutor

# Execute workflow as agent (async)
result = await AgentWorkflowExecutor.execute_workflow_for_agent(
    agent_id="extract_requirements",
    workflow_id="uuid",
    tenant_id="tenant-id",
    workflow_input={...},
    db=db_session
)

# Get agent's workflows
workflows = AgentWorkflowExecutor.get_agent_workflows(
    agent_id="extract_requirements",
    tenant_id="tenant-id",
    db=db_session
)

# Assign workflow to agent
success = AgentWorkflowExecutor.assign_workflow_to_agent(
    agent_id="extract_requirements",
    workflow_id="uuid",
    tenant_id="tenant-id",
    db=db_session
)

# Unassign workflow from agent
success = AgentWorkflowExecutor.unassign_workflow_from_agent(
    agent_id="extract_requirements",
    workflow_id="uuid",
    tenant_id="tenant-id",
    db=db_session
)
```

## Available Agents

All 13 system agents can be assigned workflows:

1. `validate_request_and_access` - Request Validator
2. `inspect_package_contents` - Package Inspector
3. `extract_requirements` - Requirements Extractor
4. `ingest_and_normalize_course_materials` - Course Ingestion Engine
5. `retrieve_authorized_context` - Context Retriever
6. `map_workforce_skills` - Skill Mapper
7. `calculate_coverage_and_gaps` - Gap Analyzer
8. `draft_recommendations` - Recommendation Engine
9. `generate_course_updates` - Content Generator
10. `accessibility_check` - Accessibility Auditor
11. `content_governance` - Content Governance Agent
12. `persist_artifacts` - Data Persister
13. `emit_audit_events` - Audit Logger

## Request/Response Examples

### Assign Workflow
```json
POST /v1/agent-workflows/assign
{
  "agent_id": "extract_requirements",
  "workflow_id": "abc-123",
  "auto_execute": false
}

Response:
{
  "status": "success",
  "message": "Agent extract_requirements assigned to workflow",
  "workflow_id": "abc-123",
  "agent_id": "extract_requirements"
}
```

### Execute Workflow
```json
POST /v1/agent-workflows/execute
{
  "agent_id": "extract_requirements",
  "workflow_id": "abc-123",
  "input_data": {
    "program_id": "prog_001",
    "program_name": "Computer Science",
    "course_ids": ["course_001"],
    "input_package_id": "pkg_001",
    "input_package_format": "zip",
    "input_skill_framework_id": "framework_001"
  }
}

Response:
{
  "status": "success",
  "execution_id": "exec-456",
  "workflow_id": "abc-123",
  "workflow_name": "Workforce Alignment",
  "agent_id": "extract_requirements",
  "result": { ... }
}
```

### Get Agent Workflows
```
GET /v1/agent-workflows/extract_requirements/workflows

Response:
[
  {
    "workflow_id": "abc-123",
    "workflow_name": "Workforce Alignment",
    "description": "...",
    "agent_id": "extract_requirements",
    "is_automatable": false,
    "execution_trigger": "manual"
  }
]
```

## Testing

### Run Tests
```bash
cd backend
python test_agent_workflows.py
```

### Manual Testing
```bash
# Test assignment
curl -X POST "http://localhost:8000/api/v1/agent-workflows/assign" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"extract_requirements","workflow_id":"abc-123","auto_execute":false}'

# Test execution
curl -X POST "http://localhost:8000/api/v1/agent-workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id":"extract_requirements",
    "workflow_id":"abc-123",
    "input_data":{"program_id":"p1","program_name":"CS","course_ids":["c1"],"input_package_id":"pkg1","input_package_format":"zip","input_skill_framework_id":"f1"}
  }'
```

## Database Queries

### Find Agents for Workflow
```python
from database.models import Workflow
from database.db import SessionLocal

db = SessionLocal()
workflow = db.query(Workflow).filter(Workflow.id == "abc-123").first()
agents = workflow.assigned_agents  # List of agent IDs
```

### Find Workflows for Agent
```python
workflows = db.query(Workflow).filter(
    Workflow.assigned_agents.contains("extract_requirements")
).all()
```

### Check Execution History
```python
from database.models import WorkflowExecution, AgentRun

executions = db.query(WorkflowExecution).filter(
    WorkflowExecution.workflow_id == "abc-123"
).order_by(WorkflowExecution.started_at.desc()).all()

agent_runs = db.query(AgentRun).filter(
    AgentRun.agent_name == "extract_requirements",
    AgentRun.status == "completed"
).all()
```

## Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| 404 Not Found | Workflow doesn't exist | Verify workflow_id |
| 403 Forbidden | Agent not assigned | Use assign endpoint first |
| 400 Bad Request | Invalid input | Check required fields |
| 500 Server Error | Execution failed | Check logs, review input |

## Performance Tips

1. **Caching**: Cache assigned workflows list in frontend
2. **Batch Operations**: Assign multiple agents at once via separate requests
3. **Async**: Always use async execution for non-blocking operations
4. **Monitoring**: Track execution times by agent type
5. **Cleanup**: Archive old execution records periodically

## Common Tasks

### Add Agent to New Workflow
```python
# 1. Create workflow (if not exists)
# 2. Assign agent
result = await AgentWorkflowExecutor.execute_workflow_for_agent(...)
```

### List All Agents
```python
from api.agents import REGISTERED_AGENTS
agents = list(REGISTERED_AGENTS.keys())
```

### Get Execution Results
```python
from database.models import WorkflowExecution
execution = db.query(WorkflowExecution).filter(
    WorkflowExecution.id == execution_id
).first()
output = execution.output_data
```

### Monitor Workflow Status
```python
# In dashboard or monitoring tool
GET /api/v1/agents/ → returns agents with assigned_workflows
GET /api/v1/agent-workflows/{agent_id}/workflows → lists available workflows
```

## Migration Commands

```bash
# Apply migration
cd backend
python migrate_add_agent_workflows.py

# Verify migration
python -c "from database.models import Workflow; print([c.name for c in Workflow.__table__.columns])"
```

## Troubleshooting

### Check Module Imports
```bash
python -c "from api.agent_workflows import router; print('OK')"
```

### Verify Database Schema
```bash
python -c "
from database.models import Workflow
cols = [c.name for c in Workflow.__table__.columns]
print('assigned_agents' in cols)
print('execution_trigger' in cols)
print('is_automatable' in cols)
"
```

### Check API Availability
```bash
curl http://localhost:8000/api/v1/agents/
```

## Related Documentation

- **Complete Guide**: `AGENT_WORKFLOWS_GUIDE.md`
- **Implementation Details**: `AGENT_WORKFLOWS_IMPLEMENTATION.md`
- **Test Suite**: `test_agent_workflows.py`
- **Source Code**: 
  - `services/agent_workflow_executor.py`
  - `api/agent_workflows.py`
  - `database/models.py`

## Support

For issues:
1. Check logs: `tail -f backend.log`
2. Review test suite: `test_agent_workflows.py`
3. Read guide: `AGENT_WORKFLOWS_GUIDE.md`
4. Check implementation: `AGENT_WORKFLOWS_IMPLEMENTATION.md`
