# Agentic Workforce Alignment Workflow - Architecture Review & Implementation Plan

**Date:** September 25, 2026  
**Platform:** Education Intelligence & Content Orchestration Platform  
**Scope:** Full architecture inspection and detailed implementation plan for workforce-alignment workflow  

---

## EXECUTIVE SUMMARY

The Education Intelligence & Content Orchestration Platform has a **solid multi-tenant foundation** with existing workflow orchestration, content management, standards frameworks, and alignment infrastructure. The platform can support a comprehensive workforce-alignment workflow with **moderate new development** focused on:

1. **Workforce role/skill domain model** (new)
2. **Requirements extraction and review** (new LangGraph workflow)
3. **Course package ingestion enhancement** (extends existing)
4. **Skill mapping and coverage analysis** (new services + LangGraph node)
5. **Recommendations and draft content** (extends existing content studio)
6. **Accessibility workflow** (reuses existing audit model, extends)
7. **Package validation and export** (new validators)
8. **Human-in-the-loop checkpoints** (use LangGraph interrupts)

**Estimated effort:** 12-16 weeks (4 phases of 3-4 weeks each)

---

## PART 1: EXISTING PLATFORM INSPECTION

### 1.1 Multi-Tenancy & Authorization Foundation

**Status:** ✅ **Fully implemented**

**Entities:**
- `Tenant` (organization boundary)
- `Organization` (sub-unit within tenant)
- `User` (email, username, roles: admin, editor, viewer, user)
- `UserPreferences`, `ApiKey`, `UserSession` (auth infrastructure)

**Observations:**
- ✅ Tenant isolation enforced at database level (`tenant_id` on all domain tables)
- ✅ Middleware applies context (`TenantMiddleware` extracts X-Tenant-ID, sets context)
- ✅ Role-based access control in place (role field on User)
- ⚠️ No fine-grained permission model (can_view, can_edit, can_approve) yet
- ⚠️ Existing roles (admin/editor/viewer) need extension for workflow roles (approver, reviewer, accessibility_reviewer)

**For workforce workflow:**
- Add workflow-specific roles: `program_owner`, `curriculum_reviewer`, `accessibility_reviewer`, `approver`
- Extend permission checks in API and LangGraph nodes
- Reuse existing tenant/org/user infrastructure

### 1.2 Curriculum & Learning Content Model

**Status:** ✅ **Partially implemented**

**Entities:**
- `Curriculum` (named course program, version, grade, subject, status)
- `CurriculumUnit` (hierarchical structure: course → unit → unit)
- `Lesson` (title, objectives, content JSON, status, model/prompt metadata)
- `Activity` (type: discussion/role_play/simulation/project, instructions, duration)
- `LearningObjective` (objective text, cognitive_level, Bloom's taxonomy)
- `Assessment` (type: formative/summative/diagnostic, blueprint JSON)
- `AssessmentItem` (question, answer_key, cognitive_level, distractors, rationale)
- `Content` (general content model: title, type, raw_content, metadata, version)
- `ContentEmbedding` (chunks with embeddings for RAG)

**Observations:**
- ✅ Hierarchy and versioning support
- ✅ Metadata fields for model/prompt tracking
- ✅ Learning objectives and assessment structure
- ✅ Content embeddings already in place (ChromaDB vector store)
- ⚠️ `Lesson.content` is JSON but schema is not enforced
- ⚠️ No explicit "course package" or "import manifest" entity yet
- ⚠️ No source-anchor fields for cross-referencing extracted vs. original content

**For workforce workflow:**
- Add `CoursePackage` entity (manifest, format, source, validation_result)
- Add `CoursePackageVersion` for versioning
- Extend `Content`, `Lesson`, `Activity` with `source_anchor` fields (path, chapter, page, section)
- Add `ExtractedObjective` or metadata to track extraction confidence and source

### 1.3 Standards & Skill Frameworks

**Status:** ✅ **Implemented & functional**

**Entities:**
- `StandardFramework` (name, authority, jurisdiction, version)
- `Standard` (code, description, grade, subject, domain, strand, version)
- **Loaded frameworks:**
  - CCSS (Common Core State Standards)
  - NGSS (Next Generation Science Standards)
  - CSTA (Computer Science Standards)
  - CTE (Career & Technical Education)
  - California State Standards

**Observations:**
- ✅ Multi-framework support with versioning
- ✅ Hierarchical standards (parent_id)
- ✅ 120+ sample standards loaded
- ✅ Standards API endpoints functional
- ⚠️ No `Skill` or `Competency` model distinct from `Standard`
- ⚠️ No `SkillFramework` entity (e.g., CASE framework, O*NET, ACE competency model)
- ⚠️ No proficiency/mastery rubric model
- ⚠️ Existing `Skill` model is basic (name, description, category, proficiency_level, standards JSON)

**For workforce workflow:**
- Add `SkillFramework` entity (similar to StandardFramework for job skills)
- Add `WorkforceSkill` (name, description, framework_id, proficiency_levels)
- Add `SkillProficiencyRubric` (defines beginner/intermediate/advanced/expert for a skill)
- Add `RoleRequirement` (role_id, skill_id, required_proficiency, evidence_type)
- Optionally integrate with O*NET or CASE data via API

### 1.4 Alignment & Coverage

**Status:** ✅ **Core model exists, alignment workspace functional**

**Entities:**
- `Alignment` (source_type, source_id, standard_id/objective_id, score, confidence, evidence, status, reviewed_by, reviewed_at)
- Status values: candidate, reviewed, approved, rejected

**Observations:**
- ✅ Flexible alignment source types (content, objective, lesson, assessment)
- ✅ Confidence and evidence fields present
- ✅ Review workflow with reviewer tracking
- ✅ Sample 218 candidates loaded and working in Alignment Workspace
- ⚠️ Evidence is stored as JSON array but lacks explicit `EvidenceReference` entity for search/reporting
- ⚠️ No `CoverageReport` or `GapAnalysis` entity
- ⚠️ No distinction between human-approved and AI-generated mappings

**For workforce workflow:**
- Add `SkillAlignment` entity (like Alignment but for skill-to-course mappings)
- Add `EvidenceReference` (alignment_id, source_type, source_id, excerpt, anchor)
- Add `CoverageReport` (course_id, framework_id, total_skills, covered_skills, coverage_percent, gaps)
- Add `GapAnalysis` (course_id, skill_id, severity, recommended_action)

### 1.5 Workflow Orchestration

**Status:** ⚠️ **Model exists, but not actively used**

**Entities:**
- `Workflow` (name, definition JSON, status: draft/active/archived, is_template)
- `WorkflowExecution` (status: pending/running/completed/failed, input_data, output_data, error_message)
- `AgentRun` (agent_name, agent_type, status, input/output_data, error_message)

**Observations:**
- ✅ Workflow DAG model is flexible (definition stored as JSON)
- ✅ Execution and agent-run tracking already in place
- ⚠️ **Previous agent-based implementation removed** (deleted agents/ directory in recent work)
- ⚠️ `_run_project_workflow()` disabled (returns "not implemented")
- ⚠️ No existing LangGraph integration
- ⚠️ WorkflowExecution tracking is basic (no checkpoint/resume mechanism)

**For workforce workflow:**
- **Implement using LangGraph** (not the old agent framework)
- Extend `WorkflowExecution` with `checkpoint_data`, `resume_from`, `human_interrupt_reason`, `human_decision`
- Store LangGraph state and checkpoints (use database or dedicated checkpoint backend)
- Record node execution times, model versions, token usage

### 1.6 Content Ingestion & Vector Search

**Status:** ✅ **Infrastructure in place**

**Infrastructure:**
- `ContentEmbedding` model (chunks, embeddings, model_name)
- `ChromaDB` vector store integration (`backend/database/vector_db.py`)
- SentenceTransformer embeddings (`all-MiniLM-L6-v2`)
- RAG pipeline for content retrieval

**Observations:**
- ✅ Vector store set up and functional
- ✅ Chunking and embedding infrastructure ready
- ⚠️ No explicit content-ingestion pipeline for course packages yet
- ⚠️ Package format support (IMSCC, ZIP) not yet documented

**For workforce workflow:**
- Build package-inspection and normalization layer (before embedding)
- Support IMSCC Common Cartridge format (validate, extract manifest, normalize paths)
- Add package version tracking to ContentEmbedding
- Implement safe file parsing and malware scanning

### 1.7 Content Generation & Authoring

**Status:** ✅ **Basic infrastructure present**

**Entities:**
- `AIArtifact` (artifact_type, source_id, model, prompt_version, evidence, confidence, status)
- `GeneratedContent` (from curriculum_workflows; content_type, title, status)
- `Lesson.content`, `Activity.instructions` (JSON fields for content)

**Observations:**
- ✅ Model/prompt version tracking in place
- ✅ Content generation placeholder exists
- ⚠️ No explicit "before/after" comparison or draft versioning
- ⚠️ No guidance library or style-guide integration yet

**For workforce workflow:**
- Add `ContentDraft` entity (course_id, version, parent_version, status, diff_from_approved)
- Add `StyleGuide` entity (tenant_id, name, guidelines JSON, version)
- Add `EditHistory` (draft_id, edited_by, timestamp, changes)
- Extend content generation to preserve and link source material

### 1.8 Accessibility

**Status:** ✅ **Audit model exists, basic implementation**

**Entities:**
- `AccessibilityAudit` (content_id, audit_date, wcag_level, issues, recommendations, status, remediation_notes)

**Observations:**
- ✅ Model supports WCAG level tracking (A, AA, AAA)
- ✅ Issues and recommendations fields present
- ✅ Status tracking (pending, reviewed, remediated)
- ⚠️ No automated checks implemented yet (infrastructure only)
- ⚠️ No formal remediation workflow or post-check validation

**For workforce workflow:**
- Build accessibility check rules (document structure, headings, links, captions, color, alt-text)
- Implement format-specific checks (PDF, DOCX, HTML, IMSCC)
- Add `AccessibilityFinding` entity (issue, location, severity, remediation_proposal)
- Implement recheck after remediation

### 1.9 Audit & Compliance

**Status:** ✅ **Audit log infrastructure present**

**Entities:**
- `AuditLog` (user_id, action, resource_type, resource_id, details, timestamp, ip_address)

**Observations:**
- ✅ Basic audit trail in place
- ⚠️ No workflow-specific audit event types
- ⚠️ No provenance tracking for AI-generated content (model version, prompt, retrieval sources)

**For workforce workflow:**
- Add workflow-specific audit events (requirement_extracted, mapping_approved, recommendation_generated, export_completed)
- Track model/prompt/graph versions in audit context
- Link evidence references to audit trail

### 1.10 API Structure & Patterns

**Status:** ✅ **RESTful FastAPI, well-organized**

**Patterns observed:**
- `/api/v1/` versioning
- Endpoints for: standards, alignments, content, lessons, assessments
- Response envelopes: `{"status": "success", "data": {...}}` or `{"resource": [...]}`
- Pagination with `skip` and `limit`
- Tenant isolation via middleware + `X-Tenant-ID` header

**Observations:**
- ✅ Consistent structure
- ✅ Error handling with proper HTTP codes
- ⚠️ No job/async-task endpoint pattern yet (async work needs to be added)
- ⚠️ No webhook or server-sent events for progress updates

**For workforce workflow:**
- Add async job endpoints (`/api/v1/workflows/{workflow_id}/jobs`)
- Add progress endpoint (`/api/v1/workflows/{workflow_id}/progress`)
- Support long-running tasks (ingestion, analysis, generation)

### 1.11 Frontend Structure & UI Patterns

**Status:** ✅ **Next.js 14, React Query, well-organized**

**Infrastructure:**
- TypeScript + Tailwind CSS
- React Query for server state
- Zustand for auth/global state
- Modular component structure (e.g., `/components/Alignment/`)
- Page routing: `/app/(authenticated)/[feature]/page.tsx`

**Observations:**
- ✅ Modern React stack
- ✅ Established component library (Button, Card, Skeleton, etc.)
- ✅ Alignment Workspace page already built and functional
- ⚠️ No workflow status/progress visualization component yet
- ⚠️ No multi-step form/wizard pattern

**For workforce workflow:**
- Build workflow progress/status component
- Build multi-step form for requirements entry
- Build skill-mapping review interface
- Build gap-analysis dashboard

---

## PART 2: GAP ANALYSIS & NEW REQUIREMENTS

### 2.1 Workforce Role & Skill Domain Model (NOT YET IMPLEMENTED)

**Gap:** No workforce role, job family, or skill framework beyond generic `Skill` model.

**Required entities:**
```
WorkforceRole
├── id, tenant_id
├── name, description
├── job_family (e.g., "Software Engineering", "Nursing")
├── education_level, experience_years
├── authority (e.g., "BLS O*NET", "LinkedIn", "ACE")
├── version, created_at, updated_at

RoleSkillRequirement
├── id, tenant_id
├── role_id → WorkforceRole
├── skill_id → WorkforceSkill
├── required_proficiency (e.g., "intermediate", "advanced")
├── evidence_type (e.g., "job_posting", "competency_framework")
├── priority (critical, high, medium, low)

WorkforceSkill
├── id, tenant_id
├── name, description
├── framework_id → SkillFramework
├── proficiency_rubric_id → SkillProficiencyRubric
├── version

SkillFramework
├── id, tenant_id
├── name (e.g., "O*NET", "CASE", "ACE")
├── authority, version
├── description

SkillProficiencyRubric
├── id, tenant_id
├── skill_id → WorkforceSkill
├── beginner, intermediate, advanced, expert (JSON descriptions)
├── version
```

### 2.2 Requirements Profile (NOT YET IMPLEMENTED)

**Gap:** No structured model for capturing, versioning, and reviewing institution requirements.

**Required entities:**
```
RequirementsProfile
├── id, tenant_id, request_id
├── program_id, program_name
├── target_roles [role_ids] (JSON array)
├── required_skills [skill_ids] (JSON array)
├── course_scope (e.g., curriculum_id, course_ids)
├── accessibility_guidelines, style_guides
├── constraints (duration, delivery format, prerequisites)
├── source_references (links to original requirements docs)
├── status (draft, confirmed, archived)
├── version, created_by, confirmed_by, confirmed_at
├── created_at, updated_at

RequirementEdit
├── id, tenant_id
├── profile_id → RequirementsProfile
├── field_name, old_value, new_value
├── edited_by, edited_at
├── reason (for audit trail)
```

### 2.3 Course Package & Ingestion (PARTIALLY IMPLEMENTED)

**Gap:** No explicit course package entity, manifest validation, or version tracking for imported materials.

**Required entities:**
```
CoursePackage
├── id, tenant_id, request_id
├── curriculum_id → Curriculum
├── format (imscc, zip, upload)
├── original_filename, file_hash
├── manifest (JSON: file list, metadata)
├── validation_result (JSON: errors, warnings)
├── status (pending, ingested, indexed, failed)
├── created_at, updated_at, indexed_at

CoursePackageVersion
├── id, package_id
├── version_number, created_at
├── extraction_result (JSON: extracted structure, errors)
├── indexed_vector_store_id

ContentSourceAnchor
├── id, tenant_id
├── content_id → Content | Lesson | Activity
├── package_id → CoursePackage
├── source_path (e.g., "modules/mod1/lesson1.html")
├── source_location (page, section, heading, timestamp)
├── extraction_confidence (0-1)
├── extracted_by (model name if AI-extracted)
```

### 2.4 Skill Alignment (PARTIALLY IMPLEMENTED)

**Gap:** `Alignment` model exists for standards but not for workforce skills. Need skill-specific alignment with role context.

**Required entities:**
```
SkillAlignment
├── id, tenant_id
├── course_id | lesson_id | activity_id (source)
├── skill_id → WorkforceSkill
├── role_id → WorkforceRole (context: which role requires this skill)
├── proficiency_level (from rubric)
├── evidence [{ location, excerpt, confidence }]
├── mapping_type (approved, candidate, proposed)
├── reviewed_by, reviewed_at, reviewer_notes
├── created_by, created_at

SkillAlignmentEvidence
├── id, alignment_id
├── source_type (content_chunk, learning_objective, assessment_item)
├── source_id, source_anchor
├── excerpt, confidence
├── created_at
```

### 2.5 Coverage & Gap Analysis (NOT YET IMPLEMENTED)

**Gap:** No formal coverage report or gap-analysis entity.

**Required entities:**
```
SkillCoverageReport
├── id, tenant_id, request_id
├── course_id | curriculum_id
├── skill_framework_id → SkillFramework
├── target_role_id → WorkforceRole
├── report_date, generated_by
├── total_required_skills, covered_skills, coverage_percent
├── skill_coverage_details [{ skill_id, proficiency, coverage_status, gaps }]

SkillGap
├── id, tenant_id, request_id
├── coverage_report_id → SkillCoverageReport
├── skill_id → WorkforceSkill
├── required_proficiency, actual_proficiency
├── severity (critical, high, medium, low)
├── affected_roles [role_ids]
├── recommended_action, recommended_content_type
├── evidence_of_gap
```

### 2.6 Recommendations & Draft Materials (EXTENDS EXISTING)

**Gap:** Recommendation model missing; draft versioning needs enhancement.

**Required entities:**
```
Recommendation
├── id, tenant_id, request_id
├── course_id | lesson_id
├── skill_id | gap_id (what this addresses)
├── recommendation_type (new_objective, new_activity, new_assessment, update_content)
├── description, rationale
├── evidence_references [evidence_ids]
├── affected_sections (JSON: course locations)
├── estimated_effort, impact_assessment
├── status (proposed, approved, rejected, implemented)
├── approved_by, approved_at
├── created_at, updated_at

ContentDraft
├── id, tenant_id, request_id
├── course_id | lesson_id | activity_id
├── parent_version (approved version being updated)
├── draft_version_number
├── content_changes (JSON: diff or full content)
├── generated_by, generated_at
├── edited_by, edit_history
├── status (draft, ready_for_review, approved, rejected)
├── approval_required_by, approved_by, approved_at
```

### 2.7 Accessibility Workflow (EXTENDS EXISTING)

**Gap:** `AccessibilityAudit` exists but automated checks and remediation workflow missing.

**Required extensions:**
```
AccessibilityCheck
├── id, audit_id
├── check_type (heading_hierarchy, alt_text, color_contrast, caption_present, link_text, etc.)
├── resource_type (PDF, DOCX, IMSCC, HTML)
├── status (pass, fail, warning, unable_to_check)
├── finding (null if pass)

AccessibilityFinding
├── id, audit_id
├── check_type, severity (critical, major, minor)
├── location (page, element, description)
├── description, remediation_proposal
├── addressed_by_id (remediation_id if remediated)

AccessibilityRemediation
├── id, finding_id
├── description, applied_by, applied_at
├── recheck_result (pass/fail/needs_revision)
├── recheck_date
```

### 2.8 Package Validation & Export (NOT YET IMPLEMENTED)

**Gap:** No package validation for formats like Common Cartridge; no export workflow.

**Required entities:**
```
PackageValidator
├── id, package_id
├── format (imscc, zip, pdf, docx)
├── profile (e.g., "1EdTech Common Cartridge 1.3")
├── validation_rules (JSON: rule set version)
├── validation_result (JSON: issues, warnings)
├── validated_at, validated_by

ExportJob
├── id, tenant_id, request_id
├── source_course_id | curriculum_id
├── target_format (imscc, zip, pdf)
├── target_profile
├── status (pending, validating, generating, complete, failed)
├── output_file_id, file_size, checksum
├── validation_errors, validation_warnings
├── created_by, created_at, completed_at
```

### 2.9 Workflow Execution & Checkpoints (EXTENDS EXISTING)

**Gap:** `WorkflowExecution` model exists but lacks checkpoint/resume, human-interrupt, and detailed state tracking.

**Required extensions:**
```
WorkflowExecution (extended)
├── ... existing fields ...
├── graph_version (LangGraph version)
├── checkpoint_state (serialized graph state JSON)
├── last_node_executed, next_node
├── interrupted_at, interrupt_reason
├── human_decision_pending, pending_decision_type
├── human_decision, decided_by, decided_at, decision_notes
├── retry_count, max_retries
├── model_calls_count, token_usage, cost_estimate

WorkflowCheckpointState
├── id, execution_id
├── node_name, state_data (JSON, serialized)
├── timestamp, checkpoint_number
├── can_resume (boolean)
```

---

## PART 3: REUSABLE PLATFORM COMPONENTS

### 3.1 Can Reuse Directly

| Component | Usage | Notes |
|-----------|-------|-------|
| **Tenant/Organization/User** | Workflow scope and authorization | Extend user roles |
| **Curriculum/Unit/Lesson/Activity** | Course structure and content | Add source anchors |
| **StandardFramework/Standard** | Skills framework mapping | Add SkillFramework parallel |
| **Alignment** model (partially) | Skill-to-course mappings | Extend with SkillAlignment |
| **ContentEmbedding/ChromaDB** | Vector retrieval for RAG | Extend for package content |
| **AIArtifact** | Track generated content | Use for recommendations/drafts |
| **AccessibilityAudit** | Accessibility tracking | Enhance with automated checks |
| **AuditLog** | Workflow audit trail | Add workflow-specific event types |
| **Content** model | Source materials | Extend with package metadata |
| **FastAPI/SQLAlchemy** | API and ORM | No changes needed |
| **React/Next.js/TailwindCSS** | Frontend framework | Add workflow UI components |
| **Vector store (ChromaDB)** | Semantic search for requirements/skills | Reuse as-is |

### 3.2 Need Extension

| Component | Extension | Notes |
|-----------|-----------|-------|
| **User.role** | Add workflow roles | program_owner, curriculum_reviewer, accessibility_reviewer, approver |
| **WorkflowExecution** | Add checkpoint/resume, human-interrupt | Support LangGraph state persistence |
| **Lesson.content** | Add schema validation | Structured learning objective, activity, assessment templates |
| **Content** | Add source_anchor fields | Track original location in package |
| **Standard** | Add SkillFramework parallel | Separate job-skills from academic standards |

### 3.3 Need to Build

| Component | Purpose | Effort |
|-----------|---------|--------|
| **Workforce Role & Skill model** | Job role requirements | 2-3 days |
| **RequirementsProfile** | Capture & review institution requirements | 3-4 days |
| **CoursePackage & ingestion** | Import IMSCC/ZIP, validate, normalize | 5-7 days |
| **SkillAlignment** | Map skills to course content | 3-4 days |
| **CoverageReport/GapAnalysis** | Analyze coverage and identify gaps | 3-4 days |
| **Recommendation & ContentDraft** | Generate and track edits | 4-5 days |
| **Accessibility automation** | Implement checks per format | 5-7 days |
| **Package validators** | Validate Common Cartridge, ZIP, PDF, DOCX | 4-5 days |
| **LangGraph workflows** | Orchestrate 8 specialist nodes | 10-12 days |
| **Frontend components** | Workflow UI, progress, forms, dashboards | 8-10 days |

---

## PART 4: LANGGRAPH WORKFLOW DESIGN

### 4.1 Workflow Orchestration Architecture

**Approach:**
- **LangGraph composable graph** with typed state (Pydantic models)
- **Durable checkpoints** persisted to database (`WorkflowExecution.checkpoint_state`)
- **Human interrupts** at 6 key checkpoints (requirements, structure, mapping, recommendations, accessibility, approval)
- **Modular nodes** implementing domain services + LangChain model calls
- **Bounded retries, error handling, and observability**

### 4.2 Graph State Definition (Pydantic)

```python
class WorkflowState(BaseModel):
    # Context
    tenant_id: str
    request_id: str
    initiating_user_id: str
    
    # Program & course scope
    program_id: str
    program_name: str
    course_ids: List[str]
    
    # Input assets (immutable)
    input_package_id: str
    input_standards_framework_id: str
    input_style_guide_id: Optional[str]
    
    # Extracted requirements (after node 3)
    requirements_profile_id: Optional[str]
    target_role_ids: List[str]
    required_skill_ids: List[str]
    
    # Confirmed requirements (after human checkpoint 1)
    requirements_confirmed: bool
    confirmed_requirements_profile_id: Optional[str]
    
    # Course structure (after node 4)
    course_structure_extracted: bool
    extraction_errors: List[str]
    
    # Skill mappings (after node 6)
    candidate_skill_alignments: List[Dict]
    coverage_report_id: Optional[str]
    gap_analysis_id: Optional[str]
    
    # Recommendations (after node 7)
    recommendations: List[Dict]
    approved_recommendations: List[str]
    
    # Draft materials (after node 8)
    draft_artifact_ids: List[str]
    
    # Accessibility (after node 9)
    accessibility_audit_id: Optional[str]
    accessibility_findings: List[Dict]
    accessibility_remediated: bool
    
    # Export & approval (after node 10)
    export_format: str
    export_validation_passed: bool
    final_approval: bool
    approved_by: Optional[str]
    
    # Tracking
    workflow_status: str  # pending, requirements, ingestion, analysis, recommendations, generation, accessibility, approval, completed, failed
    current_node: str
    human_interrupt_reason: Optional[str]
    human_decision: Optional[Dict]
    
    # Versions & metadata
    graph_version: str
    model_name: str
    prompt_versions: Dict[str, str]
    retrieval_sources: List[Dict]
    
    # Error & retry
    error_message: Optional[str]
    retry_count: int
    last_node_error: Optional[str]
```

### 4.3 Workflow Node Outline

```
START
├── validate_request_and_access
│   └── Check tenant, user permissions, input assets
│
├── inspect_package_contents
│   └── Validate format, manifest, file inventory
│
├── extract_requirements (LangChain + Requirements Understanding Agent)
│   ├── Parse institution goals, job roles, skill requirements
│   ├── Extract constraints and guidelines
│   └── Return structured requirements profile
│
├── INTERRUPT_1: confirm_requirements_checkpoint
│   └── Human reviews extracted requirements, edits, confirms
│
├── ingest_and_normalize_course_materials (Content Intelligence Node)
│   ├── Inspect package contents, extract hierarchy
│   ├── Preserve source anchors
│   ├── Extract objectives, assessments, readings
│   └── Create embeddings
│
├── INTERRUPT_2: validate_course_structure_checkpoint
│   └── Human reviews extracted structure, objectives, metadata
│
├── retrieve_authorized_context (Knowledge & Retrieval Node)
│   ├── Fetch confirmed requirements
│   ├── Fetch skill frameworks and proficiency rubrics
│   ├── Fetch approved examples and style guides
│   └── Vector search for similar courses (optional)
│
├── map_workforce_skills (Workforce Skills Mapping Node)
│   ├── Link skills to course objectives/content
│   ├── Apply proficiency rubric
│   ├── Score and rank mappings
│   └── Create skill alignments
│
├── calculate_coverage_and_gaps (Coverage Analysis Service)
│   ├── Aggregate skill mappings by proficiency
│   ├── Identify coverage vs. gaps
│   ├── Assess severity
│   └── Generate recommendations
│
├── INTERRUPT_3: review_mapping_and_gaps_checkpoint
│   └── Human accepts/edits/rejects mappings and gaps
│
├── draft_recommendations (Recommendations Node)
│   ├── Prioritize gap-remediation recommendations
│   ├── Generate content suggestions (new objective, activity, assessment)
│   ├── Explain evidence and rationale
│   └── List affected sections
│
├── INTERRUPT_4: approve_recommendations_checkpoint
│   └── Human selects which recommendations to draft
│
├── generate_selected_course_updates (Content Studio Node)
│   ├── Generate approved section drafts
│   ├── Apply style guides and accessibility guidelines
│   ├── Preserve comparison with approved version
│   └── Validate content schema
│
├── accessibility_check_and_remediation (Accessibility Workflow)
│   ├── Run automated checks (format-specific)
│   ├── Report findings
│   └── Support remediation loop
│
├── INTERRUPT_5: accessibility_review_checkpoint
│   └── Human reviews findings, approves remediations
│
├── validate_export_package (Package Validator)
│   ├── Validate selected format/profile
│   ├── Report unsupported content
│   └── Prepare export
│
├── INTERRUPT_6: final_approval_checkpoint
│   └── Human approves publication/export
│
├── persist_approved_artifacts
│   ├── Save approved course version
│   ├── Save reports and audit trail
│   └── Finalize export
│
├── emit_audit_events
│   └── Record workflow completion and all decisions
│
└── END
```

---

## PART 5: IMPLEMENTATION PLAN BY PHASE

### Phase 1: Foundation & Domain Model (Weeks 1-3)

**Goal:** Build workforce role/skill domain, extend models, set up LangGraph infrastructure.

**Tasks:**
1. **Add workforce role/skill domain models** (2 days)
   - `WorkforceRole`, `WorkforceSkill`, `SkillFramework`, `SkillProficiencyRubric`
   - `RoleSkillRequirement`, `SkillAlignment`, `SkillCoverageReport`, `SkillGap`
   - Migrations

2. **Add requirements profile & editing model** (2 days)
   - `RequirementsProfile`, `RequirementEdit`
   - API endpoints for CRUD

3. **Extend workflow execution model** (1 day)
   - Add checkpoint/resume fields to `WorkflowExecution`
   - Add `WorkflowCheckpointState` for state persistence

4. **Set up LangGraph infrastructure** (2 days)
   - Choose checkpoint backend (database or LangSmith)
   - Implement WorkflowState Pydantic model
   - Create base node and graph scaffolding
   - Integration tests

5. **Extend frontend for workflow** (1 day)
   - Add workflow progress component
   - Add workflow status page

**Deliverables:**
- Database migrations (5-6 new tables)
- 10 new API endpoints
- LangGraph graph skeleton
- Phase 1 test suite

**Assumptions:**
- Using Claude as LLM for all nodes
- Checkpoint storage in database (SQLAlchemy)
- IMSCC Common Cartridge 1.3 as initial export format

---

### Phase 2: Requirements & Course Ingestion (Weeks 4-6)

**Goal:** Build requirements extraction, course package ingestion, and first two workflow checkpoints.

**Tasks:**
1. **Build Requirements Understanding node** (3 days)
   - LangChain prompt for extracting goals, roles, skills, constraints
   - Structured output (RequirementsProfile)
   - Uncertainty handling and clarification questions
   - Service layer for validation

2. **Build course package ingestion** (4 days)
   - Package validation (manifest, format, file inventory)
   - IMSCC/ZIP inspection and normalization
   - Course hierarchy extraction (module → lesson → activity)
   - Source anchor tracking
   - ContentSourceAnchor model and persistence
   - Integration with existing Content/Lesson models

3. **Build checkpoint UIs** (2 days)
   - Requirements review & confirmation UI
   - Course structure review UI
   - Edit/override capabilities

4. **Integration & testing** (2 days)
   - End-to-end test from package upload to confirmed structure

**Deliverables:**
- `extract_requirements` and `ingest_course_materials` nodes
- Package ingestion service
- 8 new API endpoints
- 2 checkpoint UI components
- Phase 2 test suite

**Assumptions:**
- IMSCC support only (ZIP can follow)
- 100 MB package size limit
- Malware scanning via YARA/ClamAV (placeholder)

---

### Phase 3: Skills Mapping & Recommendations (Weeks 7-10)

**Goal:** Build skill mapping, coverage analysis, recommendations, and draft content generation.

**Tasks:**
1. **Build Workforce Skills Mapping node** (3 days)
   - Link course objectives/content to required skills
   - Apply proficiency rubric
   - Score alignments
   - SkillAlignment service and persistence
   - Evidence reference tracking

2. **Build Coverage & Gap Analysis service** (2 days)
   - Aggregate alignments by skill
   - Calculate coverage percent
   - Identify gaps and severity
   - GapAnalysis and CoverageReport persistence

3. **Build Recommendations node** (3 days)
   - Prioritize gap-remediation recommendations
   - LangChain prompt for recommendation generation
   - Evidence-based rationale
   - Recommendation entity and persistence

4. **Build Content Draft Generation node** (3 days)
   - Generate learning objectives, activities, assessments for approved recommendations
   - Apply style guides
   - Link to original approved content
   - ContentDraft entity and edit history

5. **Build skill mapping & gap review UI** (2 days)
   - Skill alignment review interface
   - Gap analysis dashboard
   - Recommendation approval interface

6. **Integration & testing** (2 days)

**Deliverables:**
- `map_workforce_skills`, `calculate_coverage_and_gaps`, `draft_recommendations`, `generate_selected_course_updates` nodes
- SkillAlignment, Recommendation, ContentDraft services
- 6 new API endpoints
- 3 checkpoint UI components
- Phase 3 test suite

**Assumptions:**
- Proficiency rubrics are human-defined (not AI-generated)
- Recommendations are proposed, not auto-applied
- Draft content supports sections only (whole-lesson regeneration follows)

---

### Phase 4: Accessibility, Export & Approval (Weeks 11-16)

**Goal:** Build accessibility workflow, package validation, export, and final approval.

**Tasks:**
1. **Build Accessibility Workflow node** (4 days)
   - Format-specific check rules (PDF, DOCX, IMSCC, HTML)
   - Implement checks: headings, links, captions, alt-text, color contrast
   - AccessibilityFinding and AccessibilityRemediation entities
   - Remediation proposal generation
   - Recheck after remediation

2. **Build Package Validators** (2 days)
   - Common Cartridge 1.3 validator
   - Manifest validation
   - Unsupported-content reporting

3. **Build Export & Package Generation** (3 days)
   - Serialize course to IMSCC format
   - Embed approved content, assessments, objectives
   - Include accessibility report
   - ExportJob entity and status tracking

4. **Build Final Approval & Publication** (2 days)
   - Final approval checkpoint UI
   - Package metadata review
   - Approval audit trail
   - Publication to export destination

5. **Build Reports & Audit Trail** (2 days)
   - Skill alignment report (PDF/HTML)
   - Gap analysis report
   - Accessibility report
   - Workflow audit log (structured JSON)
   - Provenance tracking (model versions, prompt versions, retrieval sources)

6. **Build Frontend for accessibility & export** (2 days)
   - Accessibility review UI
   - Remediation UI
   - Export options & status
   - Reports download

7. **Integration, testing, and production readiness** (3 days)
   - Full workflow end-to-end test
   - Performance optimization
   - Tenant isolation audit
   - Rollout plan

**Deliverables:**
- `accessibility_check_and_remediation`, `validate_export_package`, `persist_approved_artifacts`, `emit_audit_events` nodes
- Package validators and exporters
- 8 new API endpoints
- 2 checkpoint UI components
- Full reports suite
- Complete workflow test coverage
- Production readiness checklist

**Assumptions:**
- IMSCC 1.3 is primary export (others follow)
- Accessibility assumes WCAG 2.2 Level AA target
- Reports are JSON+PDF (not interactive dashboards initially)
- Workflow is single-course per execution (batch workflows follow)

---

## PART 6: NEW API ENDPOINTS (PREVIEW)

```
POST   /api/v1/workforce-alignment/workflows
       Create a new alignment workflow (start)

GET    /api/v1/workforce-alignment/workflows/{workflow_id}
       Get workflow status and progress

POST   /api/v1/workforce-alignment/workflows/{workflow_id}/checkpoint/{checkpoint_name}/confirm
       Human confirms and provides decision at checkpoint

GET    /api/v1/workforce-alignment/workflows/{workflow_id}/requirements
       Get extracted requirements

PUT    /api/v1/workforce-alignment/workflows/{workflow_id}/requirements
       Update confirmed requirements

GET    /api/v1/workforce-alignment/workflows/{workflow_id}/course-structure
       Get extracted course structure

GET    /api/v1/workforce-alignment/workflows/{workflow_id}/skill-alignments
       Get proposed skill mappings

PUT    /api/v1/workforce-alignment/workflows/{workflow_id}/skill-alignments
       Accept/reject/edit skill mappings

GET    /api/v1/workforce-alignment/workflows/{workflow_id}/gap-analysis
       Get gap analysis report

POST   /api/v1/workforce-alignment/workflows/{workflow_id}/recommendations/{rec_id}/approve
       Approve a recommendation for drafting

GET    /api/v1/workforce-alignment/workflows/{workflow_id}/drafts
       Get draft materials

PUT    /api/v1/workforce-alignment/workflows/{workflow_id}/drafts/{draft_id}
       Edit a draft

GET    /api/v1/workforce-alignment/workflows/{workflow_id}/accessibility
       Get accessibility findings

PUT    /api/v1/workforce-alignment/workflows/{workflow_id}/accessibility/{finding_id}/remediate
       Record remediation for a finding

POST   /api/v1/workforce-alignment/workflows/{workflow_id}/approve-for-export
       Final approval and export

GET    /api/v1/workforce-alignment/workflows/{workflow_id}/reports
       Get all reports (requirements, gaps, accessibility, audit)

# Workforce role/skill management
GET    /api/v1/workforce-roles
       List workforce roles

POST   /api/v1/workforce-roles
       Create workforce role

GET    /api/v1/workforce-skills
       List skills in a framework

POST   /api/v1/skill-frameworks
       Create/import skill framework
```

---

## PART 7: DATA MODEL DIAGRAM (SUMMARY)

```
EXISTING (REUSED):
  Tenant ──┬─→ Organization ──→ User (+ roles)
           └─→ StandardFramework ──→ Standard
           └─→ Curriculum ──→ Unit ──→ Lesson ──→ Activity
           └─→ Assessment ──→ AssessmentItem
           └─→ Content ──→ ContentEmbedding (ChromaDB)

NEW (TO BUILD):
  WorkforceRole ──→ RoleSkillRequirement ──→ WorkforceSkill ──→ SkillProficiencyRubric
  
  RequirementsProfile ──→ [goal, role_ids, skill_ids, constraints]
  
  CoursePackage ──→ CoursePackageVersion ──→ Content + ContentSourceAnchor
  
  SkillAlignment ──→ [course location, skill, proficiency, evidence, status]
  
  SkillCoverageReport ──→ SkillGap
  
  Recommendation ──→ [what to change, why, where, approval]
  
  ContentDraft ──→ [changes from approved, edit history, approval]
  
  WorkflowExecution ──→ [LangGraph checkpoint state, human decisions]
  
  AccessibilityAudit ──→ AccessibilityFinding ──→ AccessibilityRemediation
  
  ExportJob ──→ [format, validation, output file]

EXTENDED:
  User.role + Workflow-specific roles
  WorkflowExecution + checkpoint/resume + human_decision fields
  AuditLog + workflow-specific event types
```

---

## PART 8: STANDARDS & INTEGRATIONS

### 8.1 Standards to Implement (in order)

1. **1EdTech Common Cartridge 1.3** (Phase 4)
   - IMS Cartridge format for course exchange
   - Focus: learning outcomes, content files, assessments
   - Validation against published XSD

2. **1EdTech CASE** (Phase 5 / future)
   - Competency and academic standards exchange
   - For importing/exporting skill frameworks
   - Versioned standards and rubrics

3. **1EdTech QTI 2.2** (Phase 5 / future)
   - Question and test interchange
   - For assessment item exchange
   - Supports multiple question types

4. **WCAG 2.2 Level AA** (Phase 4)
   - Accessibility standard
   - Target for content and UIs

### 8.2 Third-party Integrations (Optional, Future)

- **O*NET API** for job/skill data
- **LinkedIn Skills Graph** for current job requirements
- **ACE CREDIT** competency framework
- **SCORM player** for learning object delivery

---

## PART 9: RISKS & ASSUMPTIONS

### Risks

1. **LangGraph checkpoint backend** — Database checkpoints may have serialization edge cases; consider LangSmith or Redis as alternative
2. **Package ingestion complexity** — IMSCC parsing, ZIP handling, and malware detection have security implications; thorough testing required
3. **Skill mapping quality** — Workforce skill alignment depends on prompt quality and LLM consistency; offline evaluation essential
4. **Scale & concurrency** — Workflow state serialization and resumption at scale; test under load
5. **Accessibility automation** — Some checks require human judgment; over-reliance on automated checks risks false positives/negatives
6. **Standards compliance** — Common Cartridge compliance testing; consider third-party validation

### Assumptions

1. **Claude API** for all LLM calls (configurable via LangChain)
2. **Workforce roles** are human-curated, not AI-generated
3. **Skill proficiency rubrics** are institution-defined (e.g., by program owner)
4. **Package format is IMSCC** initially (ZIP, PDF, DOCX follow)
5. **Single-course workflows** per execution (batch workflows in Phase 5+)
6. **Batch size limit: 100 MB** per package
7. **No learner-outcome data** in this workflow (future enhancement)
8. **Synchronous API calls** for interactive nodes; async jobs for long-running tasks (analysis, generation, export)
9. **Durable checkpoints** required for human interrupts; database-backed

---

## PART 10: SUCCESS CRITERIA (DEFINITION OF DONE)

### Phase 1
- [ ] Workforce role/skill models created and migrated
- [ ] LangGraph graph framework operational
- [ ] Checkpoint persist/resume working
- [ ] Workflow context and authorization tests pass

### Phase 2
- [ ] Requirements extraction node operational
- [ ] Course package ingestion (IMSCC) working
- [ ] Course structure extraction accurate (>90% on test set)
- [ ] Checkpoint review UIs functional
- [ ] End-to-end test from upload to confirmed structure passes

### Phase 3
- [ ] Skill mapping node produces valid mappings (evaluated by domain expert)
- [ ] Coverage and gap analysis reports accurate
- [ ] Recommendations generated with evidence citations
- [ ] Draft content generation preserves style/structure
- [ ] Checkpoint review and approval UIs working

### Phase 4
- [ ] Accessibility checks identify known issues (sensitivity >80%)
- [ ] Common Cartridge export passes validation
- [ ] Final approval workflow complete
- [ ] Reports (requirements, gaps, accessibility, audit) generated
- [ ] Full workflow end-to-end test passes
- [ ] Tenant isolation audit clean
- [ ] Performance: workflow completes in <30 min for typical course

---

## PART 11: TEAM & TIMELINE

**Estimated effort: 12-16 weeks, 1 FTE (full-time engineer)**

**Phase breakdown:**
- Phase 1 (Foundation): 3 weeks
- Phase 2 (Ingestion & Requirements): 3 weeks
- Phase 3 (Mapping & Recommendations): 4 weeks
- Phase 4 (Accessibility, Export, Approval): 6 weeks

**With concurrent work (frontend, testing, docs): 3-4 FTE equivalent**

---

## CONCLUSION

The Education Intelligence & Content Orchestration Platform has **strong fundamentals** for workforce alignment:

✅ Multi-tenant architecture ready
✅ Curriculum and lesson models in place
✅ Standards frameworks integrated
✅ Alignment workspace functional
✅ Vector search infrastructure (ChromaDB)
✅ FastAPI/React stack proven
✅ Audit logging in place

**What's needed:**
1. Workforce role/skill domain model
2. LangGraph workflow orchestration with human checkpoints
3. Course package ingestion and source anchor tracking
4. Skill mapping and coverage analysis services
5. Content recommendation and draft generation
6. Accessibility automation and remediation workflow
7. Package validators and export
8. Workflow UI components

**Next step:** Approve this plan, then begin Phase 1 (Foundation & Domain Model) with:
- Create database migrations for workforce role/skill model
- Set up LangGraph infrastructure
- Build first workflow checkpoint framework

---

**Document prepared:** September 25, 2026
**Ready for:** Architecture review, team planning, and Phase 1 kickoff

