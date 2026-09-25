from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Table, Float, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()


# ==================== MULTI-TENANCY FOUNDATION ====================

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(String(50), default="school")  # school, district, publisher, organization
    status = Column(String(50), default="active")  # active, suspended, archived
    configuration = Column(JSON, default={})
    subscription_tier = Column(String(50), default="professional")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organizations = relationship("Organization", back_populates="tenant", cascade="all, delete-orphan")
    users = relationship("User", back_populates="tenant")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # department, school, group
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('tenant_id', 'name', name='uq_tenant_org_name'),)

    tenant = relationship("Tenant", back_populates="organizations")
    users = relationship("User", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    username = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, editor, viewer, user
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('tenant_id', 'email', name='uq_tenant_email'),
                      UniqueConstraint('tenant_id', 'username', name='uq_tenant_username'),)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    organization = relationship("Organization", back_populates="users")
    projects = relationship("Project", back_populates="creator", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    creator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")  # active, archived, draft
    primary_action = Column(String(100), nullable=True)  # content-generation, multi-format-production, etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('tenant_id', 'name', name='uq_tenant_project_name'),)

    creator = relationship("User", back_populates="projects")
    contents = relationship("Content", back_populates="project", cascade="all, delete-orphan")


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    creator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    definition = Column(JSON)  # Workflow DAG/definition
    status = Column(String(50), default="draft")  # draft, active, archived
    is_template = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('tenant_id', 'name', name='uq_tenant_workflow_name'),)

    creator = relationship("User", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)

    workflow = relationship("Workflow", back_populates="executions")
    agent_runs = relationship("AgentRun", back_populates="execution")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("workflow_executions.id"), nullable=False)
    agent_name = Column(String(255), nullable=False)
    agent_type = Column(String(100))  # content_studio, workforce_skills, etc.
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)

    execution = relationship("WorkflowExecution", back_populates="agent_runs")


class Content(Base):
    __tablename__ = "content"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content_type = Column(String(50))  # document, presentation, audio, video, web, structured_data, image
    source = Column(String(255))
    raw_content = Column(Text)
    content_metadata = Column(JSON)
    status = Column(String(50), default="pending")  # pending, ingested, indexed, archived
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    embeddings = relationship("ContentEmbedding", back_populates="content", cascade="all, delete-orphan")
    project = relationship("Project", back_populates="contents")


class ContentEmbedding(Base):
    __tablename__ = "content_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    content_id = Column(String(36), ForeignKey("content.id"), nullable=False)
    chunk_index = Column(Integer)
    text_chunk = Column(Text)
    embedding = Column(JSON)  # Store as JSON array
    embedding_model = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    content = relationship("Content", back_populates="embeddings")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100))
    proficiency_level = Column(String(50))  # beginner, intermediate, advanced, expert
    standards = Column(JSON)  # Associated standards
    competency_framework = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('tenant_id', 'name', name='uq_tenant_skill_name'),)


class AccessibilityAudit(Base):
    __tablename__ = "accessibility_audits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    content_id = Column(String(36), ForeignKey("content.id"), nullable=False)
    audit_date = Column(DateTime, default=datetime.utcnow)
    wcag_level = Column(String(20))  # A, AA, AAA
    issues = Column(JSON)  # List of accessibility issues
    recommendations = Column(JSON)
    status = Column(String(50), default="pending")  # pending, reviewed, remediated
    remediation_notes = Column(Text)


class KnowledgeContext(Base):
    __tablename__ = "knowledge_context"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(255), unique=True, index=True, nullable=False)
    value = Column(JSON)
    context_metadata = Column(JSON)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(36))
    details = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")


class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_type = Column(String(100), index=True)  # agent_execution_time, api_response_time, etc.
    metric_value = Column(Float)
    metric_metadata = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    email_notifications = Column(JSON, default={
        "workflow_started": True,
        "workflow_completed": True,
        "workflow_failed": True,
        "weekly_digest": True,
        "product_updates": False
    })
    notification_frequency = Column(String(50), default="immediate")  # immediate, daily, weekly
    theme = Column(String(50), default="system")  # light, dark, system
    language = Column(String(10), default="en")
    timezone = Column(String(100), default="UTC")
    marketing_emails = Column(Boolean, default=False)
    analytics_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")

    def to_dict(self):
        return {
            "id": self.id,
            "email_notifications": self.email_notifications,
            "notification_frequency": self.notification_frequency,
            "theme": self.theme,
            "language": self.language,
            "timezone": self.timezone,
            "marketing_emails": self.marketing_emails,
            "analytics_enabled": self.analytics_enabled
        }


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    permissions = Column(JSON, default=["read"])  # read, write, delete
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="api_keys")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True)
    device_info = Column(JSON)  # browser, OS, device type
    ip_address = Column(String(45))
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="sessions")


class CurriculumWorkflow(Base):
    """Stores curriculum alignment workflow executions"""
    __tablename__ = "curriculum_workflows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_id = Column(String(255), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Workflow status and progress
    status = Column(String(50), default="pending")  # pending, running, paused, completed, failed
    current_stage = Column(String(50), default="requirements")  # requirements, knowledge_intelligence, workforce_skills, content_studio, accessibility, completed
    progress_percentage = Column(Float, default=0.0)

    # Target information
    target_roles = Column(JSON)  # List of target job roles
    imscc_files = Column(JSON)  # List of uploaded IMSCC files

    # Results and outputs
    requirement_analysis = Column(JSON)  # Output from Requirement Understanding Agent
    knowledge_graph = Column(JSON)  # Output from Knowledge Intelligence Agent
    gap_analysis = Column(JSON)  # Output from Workforce Skills Agent
    generated_content = Column(JSON)  # Output from Content Studio Agent
    accessibility_report = Column(JSON)  # Output from Accessibility Agent

    # Execution tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    __table_args__ = (UniqueConstraint('tenant_id', 'workflow_id', name='uq_tenant_workflow_id'),)

    # Relationships
    project = relationship("Project")
    user = relationship("User")
    checkpoints = relationship("WorkflowCheckpoint", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowCheckpoint(Base):
    """Stores human-in-the-loop checkpoint approvals"""
    __tablename__ = "workflow_checkpoints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_id = Column(String(36), ForeignKey("curriculum_workflows.id"), nullable=False, index=True)

    checkpoint_number = Column(Integer, nullable=False)
    stage = Column(String(50), nullable=False)  # Stage name
    status = Column(String(50), default="pending")  # pending, approved, rejected, needs_revision

    description = Column(Text)
    required_reviewer = Column(String(255))  # Role required to approve

    # Review data
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)

    # Stage outputs for review
    stage_output = Column(JSON)  # Data from the completed stage
    findings = Column(JSON)  # Findings/recommendations for this stage

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflow = relationship("CurriculumWorkflow", back_populates="checkpoints")
    reviewer = relationship("User")


class ContentChunk(Base):
    """Stores extracted and chunked curriculum content"""
    __tablename__ = "content_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_id = Column(String(36), ForeignKey("curriculum_workflows.id"), nullable=False, index=True)

    chunk_id = Column(String(255), nullable=False)
    source_module = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    chunk_type = Column(String(50))  # learning_objective, reading, assessment, etc.
    bloom_level = Column(String(50))  # Bloom's taxonomy level
    tags = Column(JSON)  # List of tags/topics

    embedded = Column(Boolean, default=False)  # Whether embeddings have been created
    embedding_vector = Column(JSON, nullable=True)  # Vector embedding (simplified storage)

    created_at = Column(DateTime, default=datetime.utcnow)


class SkillGapRecord(Base):
    """Stores identified skill gaps"""
    __tablename__ = "skill_gaps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_id = Column(String(36), ForeignKey("curriculum_workflows.id"), nullable=False, index=True)

    competency_name = Column(String(255), nullable=False)
    competency_id = Column(String(255), nullable=False)

    required_by_roles = Column(JSON)  # List of roles that require this skill
    current_coverage = Column(Float, default=0.0)  # Coverage percentage
    gap_severity = Column(String(50))  # Critical, High, Medium, Low

    recommended_action = Column(Text)
    recommended_modules = Column(JSON)  # List of recommended modules to add
    estimated_hours = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)


class GeneratedContent(Base):
    """Stores AI-generated content from Content Studio Agent"""
    __tablename__ = "generated_content"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_id = Column(String(36), ForeignKey("curriculum_workflows.id"), nullable=False, index=True)

    content_type = Column(String(100))  # module, lesson, assessment, reading, etc.
    title = Column(String(255), nullable=False)
    content = Column(Text)

    generated_for_gap = Column(String(255), nullable=True)  # Which gap this addresses
    target_module = Column(String(255), nullable=True)  # Module this should be added to

    status = Column(String(50), default="draft")  # draft, ready_for_review, approved, integrated

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== CORE DOMAIN MODELS ====================

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    subject = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('tenant_id', 'name', name='uq_tenant_concept_name'),)


class StandardFramework(Base):
    __tablename__ = "standard_frameworks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    authority = Column(String(255))  # e.g., "Common Core", "State DOE"
    jurisdiction = Column(String(255))
    version = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    standards = relationship("Standard", back_populates="framework", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('tenant_id', 'name', 'version', name='uq_tenant_framework'),)


class Standard(Base):
    __tablename__ = "standards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    framework_id = Column(String(36), ForeignKey("standard_frameworks.id"), nullable=False)
    parent_id = Column(String(36), ForeignKey("standards.id"), nullable=True)
    code = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    grade = Column(String(50))
    subject = Column(String(100))
    domain = Column(String(255))
    strand = Column(String(255))
    version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    framework = relationship("StandardFramework", back_populates="standards")
    parent = relationship("Standard", remote_side=[id], backref="children")
    alignments = relationship("Alignment", back_populates="standard")

    __table_args__ = (UniqueConstraint('tenant_id', 'framework_id', 'code', name='uq_tenant_standard_code'),)


class Curriculum(Base):
    __tablename__ = "curricula"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), default="1.0")
    grade = Column(String(50))
    subject = Column(String(100))
    status = Column(String(50), default="draft")  # draft, active, archived
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    units = relationship("CurriculumUnit", back_populates="curriculum", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="curriculum")

    __table_args__ = (UniqueConstraint('tenant_id', 'name', 'version', name='uq_tenant_curriculum'),)


class CurriculumUnit(Base):
    __tablename__ = "curriculum_units"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    curriculum_id = Column(String(36), ForeignKey("curricula.id"), nullable=False)
    parent_id = Column(String(36), ForeignKey("curriculum_units.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    sequence = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    curriculum = relationship("Curriculum", back_populates="units")
    parent = relationship("CurriculumUnit", remote_side=[id], backref="children")
    objectives = relationship("LearningObjective", back_populates="unit", cascade="all, delete-orphan")


class LearningObjective(Base):
    __tablename__ = "learning_objectives"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    unit_id = Column(String(36), ForeignKey("curriculum_units.id"), nullable=False)
    objective = Column(Text, nullable=False)
    cognitive_level = Column(String(50))  # Bloom's taxonomy
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    unit = relationship("CurriculumUnit", back_populates="objectives")
    alignments = relationship("Alignment", back_populates="objective")


class Alignment(Base):
    __tablename__ = "alignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # content, objective, lesson, assessment
    source_id = Column(String(36), nullable=False)
    target_type = Column(String(50), nullable=False)  # standard, objective
    standard_id = Column(String(36), ForeignKey("standards.id"), nullable=True)
    objective_id = Column(String(36), ForeignKey("learning_objectives.id"), nullable=True)
    score = Column(Float, default=0.0)  # 0-1 alignment score
    confidence = Column(Float, default=0.0)  # 0-1 confidence
    evidence = Column(JSON, default=[])  # Retrieved sources supporting alignment
    status = Column(String(50), default="candidate")  # candidate, reviewed, approved, rejected
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    standard = relationship("Standard", back_populates="alignments")
    objective = relationship("LearningObjective", back_populates="alignments")

    __table_args__ = (UniqueConstraint('tenant_id', 'source_type', 'source_id', 'standard_id', name='uq_alignment'),)


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    curriculum_id = Column(String(36), ForeignKey("curricula.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer)
    grade = Column(String(50))
    subject = Column(String(100))
    status = Column(String(50), default="draft")  # draft, review, approved, published
    model = Column(String(100))  # LLM model used
    model_version = Column(String(50))
    prompt_version = Column(String(50))
    content = Column(JSON)  # Lesson structure: title, objectives, activities, etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    curriculum = relationship("Curriculum", back_populates="lessons")
    activities = relationship("Activity", back_populates="lesson")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    lesson_id = Column(String(36), ForeignKey("lessons.id"), nullable=False, index=True)
    type = Column(String(100))  # discussion, role_play, simulation, project, etc.
    title = Column(String(255), nullable=False)
    instructions = Column(Text)
    duration_minutes = Column(Integer)
    differentiation = Column(JSON)  # Adaptations for different learners
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="activities")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    assessment_type = Column(String(100))  # formative, summative, diagnostic, benchmark
    description = Column(Text)
    status = Column(String(50), default="draft")
    model = Column(String(100))
    model_version = Column(String(50))
    prompt_version = Column(String(50))
    blueprint = Column(JSON)  # Assessment structure/blueprint
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("AssessmentItem", back_populates="assessment", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('tenant_id', 'title', name='uq_tenant_assessment_title'),)


class AssessmentItem(Base):
    __tablename__ = "assessment_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False)
    type = Column(String(50))  # multiple_choice, short_answer, essay, etc.
    question = Column(Text, nullable=False)
    answer_key = Column(JSON)  # Answers and rubrics
    distractors = Column(JSON)  # For MC questions
    rationale = Column(Text)  # Why answer is correct
    cognitive_level = Column(String(50))  # Bloom's level
    sequence = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="items")


class AIArtifact(Base):
    __tablename__ = "ai_artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False)  # lesson, assessment, activity, alignment
    source_id = Column(String(36))  # Reference to source (content, standard, objective)
    source_workflow = Column(String(255))  # Workflow that generated this
    model = Column(String(100), nullable=False)
    model_version = Column(String(50))
    prompt_version = Column(String(50))
    evidence = Column(JSON, default=[])  # Retrieved sources used
    confidence = Column(Float, default=0.0)  # 0-1 confidence score
    status = Column(String(50), default="draft")  # draft, review, approved, published
    content = Column(JSON)  # The actual artifact
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    artifact_id = Column(String(36), nullable=False)  # Reference to artifact being reviewed
    artifact_type = Column(String(50), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    decision = Column(String(50), nullable=False)  # approved, rejected, needs_revision
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviewer = relationship("User")
