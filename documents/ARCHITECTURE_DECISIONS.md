# Architecture Decisions & Implementation Notes

## Multi-Tenancy Implementation (Step 1)

### Design Decision: Context Variables + Database-Level Isolation
- **Rationale:** Defense-in-depth approach ensures tenant data cannot leak even if code bypasses context checks
- **Implementation:** 
  - ContextVar for request-level tenant tracking
  - tenant_id as required foreign key on ALL tenant-owned tables
  - Unique constraints scoped to (tenant_id, entity)
  - Migration system for schema consistency

### Unique Constraint Strategy
```sql
UNIQUE (tenant_id, name)              -- User within tenant
UNIQUE (tenant_id, project_name)       -- Project within tenant
UNIQUE (tenant_id, framework_id, code) -- Standard code within framework/tenant
```

This prevents accidental data overlap while allowing same entity names across tenants.

### Tenant Assignment Pattern
1. User registers → Default tenant created (`default-<user-id>`)
2. Organization admin assigns users to organizations within tenant
3. All queries automatically scoped to user's tenant
4. Platform admin can be cross-tenant

## Core Domain Model (Step 2)

### Alignment Engine Architecture
```
Content/Objective/Lesson/Assessment
           ↓
      [Alignment Service]
           ↓
    Score (0-1): Semantic similarity + concept match
    Confidence (0-1): Source diversity + evidence strength
    Evidence: Retrieved sources, cross-references
    Status: candidate → reviewed → approved/rejected
```

### Curriculum Structure Hierarchy
```
Curriculum (v1.0)
  ├─ Unit 1 (Introduction)
  │   ├─ Objective 1.1
  │   ├─ Objective 1.2
  │   └─ Sub-Unit 1.A
  └─ Unit 2 (Advanced Topics)
      └─ Objective 2.1
```

Pattern supports:
- Nested units (modules within modules)
- Multiple objectives per unit
- Versioning at curriculum level
- Grade/subject tagging

### Assessment Blueprint Structure
```json
{
  "total_items": 25,
  "cognitive_levels": {
    "remember": 5,
    "understand": 8,
    "apply": 7,
    "analyze": 3,
    "evaluate": 2
  },
  "standards_coverage": {
    "standard_id_1": 3,
    "standard_id_2": 4
  }
}
```

Used for:
- Assessment planning before generation
- Validation after item creation
- Reporting on cognitive demand

## Service Layer Patterns (Step 2)

### Exception Handling
- Validation errors → ValueError with clear message
- Not found → ValueError (will translate to 404 in API layer)
- Auth/permission → Will handle at middleware layer
- Logging at INFO level for create/update, WARNING for failures

### Tenant Context Enforcement
Every service method:
```python
tenant_id = get_current_tenant_id()  # Raises if not set
query = db.query(Model).filter(Model.tenant_id == tenant_id)
```

This ensures NO cross-tenant data leakage is possible.

### Bulk Operations
AssessmentService.create_assessment example:
- Accept list of items
- Create each independently with error logging
- Return successfully created items
- Caller can retry failed items

## Remaining Work (Steps 3+)

### Step 3: Agent Infrastructure (PENDING)

**Challenge:** Current codebase has LangChain/LangGraph version conflicts
- Agents are imported but commented out
- Need compatible versions installation
- Tests needed for agent behavior

**Recommended Approach:**
1. Create `requirements-agents.txt` with pinned versions
2. Test locally with simple agent
3. Implement agents incrementally
4. Add agent tests to CI/CD

**Agent Implementations Needed (per spec §13):**
- Intake Agent → request interpretation, tenant/user context
- Content Agent → content analysis, extraction, generation
- Standards Agent → standards retrieval, crosswalks
- Curriculum Agent → curriculum retrieval, prerequisites
- Alignment Agent → content-standard-curriculum relationships
- Instructional Agent → lesson plans, strategies
- Assessment Agent → questions, blueprints, answer keys
- Activity Agent → classroom activities, differentiation
- Personalization Agent → remediation, enrichment
- Reporting Agent → curriculum/alignment/coverage reports
- QA Agent → validation, grounding, hallucination detection

### API Layer (PARTIALLY DONE)

**What exists:**
- `/api/auth/*` - Authentication endpoints
- `/api/projects/*` - Project management
- `/api/content/*` - Content ingestion
- `/api/workflows/*` - Generic workflows
- `/api/skills/*` - Skills listing

**What needs to be added:**
- `/api/v1/standards/*` - Standards CRUD & search
- `/api/v1/curricula/*` - Curriculum CRUD & structure
- `/api/v1/alignments/*` - Alignment creation, review, search
- `/api/v1/lessons/*` - Lesson creation & publishing
- `/api/v1/assessments/*` - Assessment CRUD & validation
- `/api/v1/activities/*` - Activity management
- `/api/v1/organizations/*` - Organization management
- `/api/v1/tenants/*` - Tenant administration

### Database Considerations

**Current:** SQLite for development
**For Production:** PostgreSQL recommended for:
- Row-level security (RLS) for additional tenant isolation
- Full-text search on standards/content
- pgvector extension for embeddings
- Connection pooling

**Migration path:**
1. Keep SQLite for dev/testing
2. Create Alembic migrations for production schema
3. Document connection string configuration

### Security Checkpoints

**Implemented:**
- ✅ Tenant isolation at DB level
- ✅ User-to-tenant assignment validation
- ✅ Context-based authorization

**Needed:**
- ❌ RBAC (role-based access control) for permissions
- ❌ API rate limiting
- ❌ Request validation (Pydantic models in API layer)
- ❌ Secrets management (API keys, LLM tokens)
- ❌ Audit logging integration
- ❌ Data encryption at rest/in transit

## Performance Considerations

### Indexing Strategy
Indexes created for:
- `users.tenant_id` - Find users per tenant
- `projects.tenant_id` - Find projects per tenant
- `content.tenant_id` - Find content per tenant
- Similar for all tenant-owned entities

**For Production:**
- Composite indexes: (tenant_id, status) for filtering
- Foreign key indexes for joins
- Consider partitioning large tables by tenant

### N+1 Query Prevention
All services use SQLAlchemy relationships, but API layer should:
- Use `eager_loading` where needed (e.g., assessments with items)
- Implement pagination on large result sets
- Cache standards framework (infrequently updated)

## Testing Strategy

**Unit Tests Needed:**
- StandardsService (create, search, hierarchy)
- CurriculumService (structure, coverage analysis)
- AlignmentService (scoring, review workflow)
- TenantService (isolation, assignment)

**Integration Tests Needed:**
- Multi-tenant request flow
- Alignment with curriculum coverage
- Lesson generation with standards
- Assessment item creation with validation

**Agent Tests Needed:**
- Individual agent behavior
- LangGraph workflow execution
- Tool availability and permissions
- Output validation
