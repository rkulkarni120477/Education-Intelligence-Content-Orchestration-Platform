# Next Steps & Implementation Roadmap

## Summary of Completed Work

### Step 1: Multi-Tenancy Foundation ✅
**Time to implement:** ~2-3 hours
**Deliverables:**
- Tenant & Organization models
- 13 core domain models added (Standards, Curriculum, Alignment, Lessons, etc.)
- Multi-tenancy enforced at database level
- Migration system created
- Tenant context middleware
- Tenant service for management

**Files Created:** 9 files, ~2000 lines of code

### Step 2: Core Domain Model Services ✅
**Time to implement:** ~3-4 hours
**Deliverables:**
- StandardsService (15 methods)
- CurriculumService (10 methods)
- AlignmentService (12 methods)
- LessonService (8 methods)
- AssessmentService (10 methods)

**Files Created:** 5 service files, ~1200 lines of code

**Key Features:**
- Full CRUD operations on all domain entities
- Tenant isolation enforced in every query
- Curriculum coverage analysis
- Alignment scoring and review workflow
- Assessment validation
- Activity and lesson management

---

## Step 3: Agent Infrastructure (IN PROGRESS)

### 3.1 Resolve LangChain/LangGraph Version Conflicts (CRITICAL)
**Current Status:** Agents are commented out in app.py due to version issues

**What to do:**
```bash
# 1. Create clean requirements file
pip install langchain==0.3.x langgraph==0.1.x pydantic==2.x

# 2. Test basic agent
python -c "from langchain_openai import ChatOpenAI; print('OK')"

# 3. Create simple LangGraph workflow test
```

**Estimated Time:** 1-2 hours

### 3.2 Implement Multi-Agent Architecture (per Spec §13)

#### Phase 1: Base Agent Framework (2-3 hours)
- [ ] Create base agent class with standard interface
- [ ] Implement agent input/output schemas
- [ ] Create agent registry/factory
- [ ] Add logging and monitoring

#### Phase 2: Specialist Agents (6-8 hours)
Priority order:
1. **Intake Agent** - Parse requirements, extract context
2. **Standards Agent** - Retrieve standards, support searches
3. **Content Agent** - Analyze content, extract concepts
4. **Alignment Agent** - Generate alignments, score them
5. **Curriculum Agent** - Manage curriculum context

Then add remaining agents:
6. **Instructional Agent** - Lesson planning
7. **Assessment Agent** - Question generation
8. **QA Agent** - Validation and grounding

#### Phase 3: LangGraph Workflows (4-5 hours)
- [ ] Create main workflow orchestrator
- [ ] Implement Intake → Content → Alignment flow
- [ ] Add conditional branching (confidence thresholds)
- [ ] Implement human-in-the-loop checkpoints
- [ ] Add workflow state persistence

### 3.3 REST API Endpoints (4-5 hours)

**Standards Endpoints:**
```
POST   /api/v1/standards/frameworks
GET    /api/v1/standards/frameworks
GET    /api/v1/standards/frameworks/{id}
POST   /api/v1/standards
GET    /api/v1/standards (with filters)
GET    /api/v1/standards/{id}
GET    /api/v1/standards/search?q=...
```

**Curriculum Endpoints:**
```
POST   /api/v1/curricula
GET    /api/v1/curricula
GET    /api/v1/curricula/{id}
GET    /api/v1/curricula/{id}/structure
POST   /api/v1/curricula/{id}/units
GET    /api/v1/curricula/{id}/coverage?framework_id=...
```

**Alignment Endpoints:**
```
POST   /api/v1/alignments
GET    /api/v1/alignments (candidates)
GET    /api/v1/alignments/{id}
PUT    /api/v1/alignments/{id}/review (approve/reject)
GET    /api/v1/alignments/content/{content_id}
GET    /api/v1/alignments/standard/{standard_id}
```

**Lesson Endpoints:**
```
POST   /api/v1/lessons
GET    /api/v1/lessons
GET    /api/v1/lessons/{id}
POST   /api/v1/lessons/{id}/activities
POST   /api/v1/lessons/{id}/publish
```

**Assessment Endpoints:**
```
POST   /api/v1/assessments
GET    /api/v1/assessments
GET    /api/v1/assessments/{id}
POST   /api/v1/assessments/{id}/items
GET    /api/v1/assessments/{id}/validate
POST   /api/v1/assessments/{id}/publish
```

---

## Implementation Checklist

### Immediate Next Actions (Day 1)
- [ ] Fix LangChain/LangGraph installation
- [ ] Update app.py to include TenantMiddleware
- [ ] Add initial tenant/organization creation in seed data
- [ ] Test multi-tenant isolation with unit tests
- [ ] Create sample seed data (framework, standards, curriculum)

### Short Term (Week 1-2)
- [ ] Implement REST API routes for all domain models
- [ ] Add Pydantic request/response schemas
- [ ] Implement Intake Agent for basic workflow
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Create integration tests for key flows

### Medium Term (Week 2-4)
- [ ] Implement all specialist agents
- [ ] Create LangGraph orchestrator workflows
- [ ] Implement human-in-the-loop review interface
- [ ] Add alignment generation with scoring
- [ ] Create reporting endpoints

### Long Term (Month 2+)
- [ ] Implement RAG for content retrieval
- [ ] Add vector embeddings for semantic search
- [ ] Create frontend UI for platform
- [ ] Implement LMS integrations
- [ ] Add advanced analytics and reporting

---

## Critical Dependencies

### Python Packages
```
# Core
fastapi==0.104.x
sqlalchemy==2.0.x
pydantic==2.x
python-jose==3.3.x

# AI/ML
langchain==0.3.x
langgraph==0.1.x
langchain-openai==0.1.x
langsmith==0.1.x

# Database
alembic==1.13.x  (for migrations)

# Utilities
python-multipart==0.0.x
aiofiles==23.x
```

### Environment Variables Needed
```
# Database
DATABASE_URL=sqlite:///./data/academian.db
# (For production, use PostgreSQL)

# LLM
OPENAI_API_KEY=...
LLM_MODEL=gpt-4-turbo

# Server
SECRET_KEY=...
ALGORITHM=HS256

# Optional: Analytics
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=...
```

---

## Testing Strategy

### Unit Tests (20-30 tests)
- Tenant isolation verification
- Service method behavior
- Error handling

### Integration Tests (15-20 tests)
- API endpoint functionality
- Multi-tenant request handling
- Workflow execution
- Database transactions

### Agent Tests (10-15 tests)
- Agent input/output validation
- Tool execution
- LangGraph workflow paths

### Example Test:
```python
def test_alignment_service_tenant_isolation(db):
    # Create tenant A and B
    # Create content in A, standards in B
    # Alignment creation should fail across tenants
    # ✓ Verify isolation
```

---

## Success Criteria for MVP

### Must Have ✅
- [x] Multi-tenancy with strict isolation
- [x] Standards CRUD and search
- [x] Curriculum structure management
- [x] Content-to-standards alignment
- [ ] Alignment review workflow
- [ ] Lesson generation (AI-assisted)
- [ ] Assessment generation (AI-assisted)
- [ ] Multi-agent orchestration
- [ ] REST API for core operations

### Should Have (Phase 2)
- [ ] Curriculum coverage analysis
- [ ] Differentiation support
- [ ] Rubric generation
- [ ] Export (PDF, DOCX)
- [ ] LMS integration

### Nice to Have (Phase 3+)
- [ ] Personalized recommendations
- [ ] Advanced analytics
- [ ] Collaborative editing
- [ ] Marketplace

---

## File Structure Reference

```
backend/
├── app.py                          # FastAPI app (needs TenantMiddleware)
├── config.py                       # Configuration
├── database/
│   ├── db.py                       # (updated) Migration runner
│   ├── models.py                   # (updated) All models + multi-tenancy
│   └── migrations/
│       ├── 001_initial_schema.py   # Base tables
│       └── 002_add_multi_tenancy.py # Tenant schema
├── auth/
│   ├── auth.py                     # Existing auth
│   └── tenant_context.py           # (NEW) Tenant isolation
├── middleware/
│   ├── __init__.py                 # (NEW)
│   └── tenant_middleware.py        # (NEW) Request context
├── services/
│   ├── tenant_service.py           # (NEW)
│   ├── standards_service.py        # (NEW)
│   ├── curriculum_service.py       # (NEW)
│   ├── alignment_service.py        # (NEW)
│   ├── lesson_service.py           # (NEW)
│   └── ... (existing services)
├── agents/                         # (TO DO)
│   ├── base_agent.py
│   ├── intake_agent.py
│   ├── standards_agent.py
│   ├── content_agent.py
│   ├── alignment_agent.py
│   └── ... (other agents)
├── workflows/                      # (TO DO)
│   ├── orchestrator.py
│   ├── content_alignment.py
│   └── lesson_generation.py
└── api/
    ├── routes/                     # (PARTIAL)
    │   ├── standards.py            # (TO DO)
    │   ├── curricula.py            # (TO DO)
    │   ├── alignments.py           # (TO DO)
    │   ├── lessons.py              # (TO DO)
    │   └── assessments.py          # (TO DO)
    └── schemas/                    # (TO DO)
```

---

## Questions to Address

1. **Database:** Continue with SQLite for MVP, or migrate to PostgreSQL now?
   - Recommendation: SQLite for dev, plan PostgreSQL migration for production

2. **LLM Provider:** Use OpenAI only, or abstract for multiple providers?
   - Recommendation: Abstract now (per spec §29)

3. **Agent State:** Store in database or in-memory?
   - Recommendation: Database for persistence and recovery (per spec §14)

4. **Frontend:** Start React/Next.js UI alongside backend?
   - Recommendation: Complete backend MVP first, UI in parallel

---

## Contact Points

Need clarification on:
- [ ] Preferred LLM provider(s)?
- [ ] Production database choice?
- [ ] Frontend framework preference (React/Vue/Angular)?
- [ ] Timeline constraints?
- [ ] Specific use case prioritization?
