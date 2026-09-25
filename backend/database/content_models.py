"""Content Development Module Database Models

This module defines models for the AI-Powered Course & Content Development system.
Includes courses, units, lessons, learning objects, assessments, standards, and alignment tracking.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Table, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

# Import shared Base from models
from database.models import Base


class ContentStatus(str, enum.Enum):
    """Status enum for content workflow"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AlignmentStatus(str, enum.Enum):
    """Status enum for content-standard alignment"""
    AI_SUGGESTED = "ai_suggested"
    HUMAN_REVIEWED = "human_reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


# ==================== COURSE HIERARCHY ====================

class Program(Base):
    """Top-level organizational container for courses"""
    __tablename__ = "programs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    organization_id = Column(String(36), nullable=True)
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default="active")  # active, archived

    # Relationships
    courses = relationship("Course", back_populates="program", cascade="all, delete-orphan")


class Course(Base):
    """Main unit of instruction - contains units, lessons, and assessments"""
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    program_id = Column(String(36), ForeignKey("programs.id"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Course metadata
    grade_level = Column(String(50))  # K, 1-8, 9-12, College, etc.
    subject = Column(String(100))  # Math, ELA, Science, Social Studies, etc.
    state_jurisdiction = Column(String(100))  # State/country standards context
    duration_hours = Column(Integer)  # Total course duration
    target_learner = Column(Text)  # Description of target student population

    # Course structure
    learning_goals = Column(Text)  # High-level course goals
    prerequisites = Column(Text)  # Required prior knowledge
    instructional_model = Column(String(100))  # Lecture, PBL, Blended, etc.
    assessment_approach = Column(String(100))  # Formative, Summative, Performance-based, etc.

    # Creator and versions
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default="draft")  # draft, in_review, approved, published
    version = Column(Integer, default=1)

    # Relationships
    program = relationship("Program", back_populates="courses")
    units = relationship("Unit", back_populates="course", cascade="all, delete-orphan")
    learning_objectives = relationship("LearningObjective", back_populates="course", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="course", cascade="all, delete-orphan")
    alignments = relationship("ContentAlignment", foreign_keys="ContentAlignment.source_id",
                            primaryjoin="Course.id == ContentAlignment.source_id")


class Unit(Base):
    """Organized group of lessons within a course"""
    __tablename__ = "units"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)  # Order within course
    name = Column(String(255), nullable=False)
    description = Column(Text)
    duration_hours = Column(Integer)

    # Standards and objectives for this unit
    learning_objective_ids = Column(JSON, default=[])  # List of UUID strings
    standard_ids = Column(JSON, default=[])  # List of standard IDs

    # Metadata
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default="draft")
    version = Column(Integer, default=1)

    # Relationships
    course = relationship("Course", back_populates="units")
    topics = relationship("Topic", back_populates="unit", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="unit", cascade="all, delete-orphan")


class Topic(Base):
    """Subtopic within a unit (optional organizational level)"""
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_id = Column(String(36), ForeignKey("units.id"), nullable=False, index=True)
    sequence_number = Column(Integer)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="draft")

    # Relationships
    unit = relationship("Unit", back_populates="topics")
    lessons = relationship("Lesson", back_populates="topic")


class Lesson(Base):
    """Individual instructional unit with learning objectives and content"""
    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_id = Column(String(36), ForeignKey("units.id"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id"), nullable=True)
    sequence_number = Column(Integer)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer)
    grade_level = Column(String(50))

    # Learning and standards alignment
    learning_objective_ids = Column(JSON, default=[])
    standard_ids = Column(JSON, default=[])

    # Instructional content
    instructional_strategy = Column(String(100))  # Direct instruction, PBL, Discovery, etc.
    prior_knowledge = Column(Text)  # What students should know before this lesson
    materials = Column(Text)  # Required materials and resources
    preparation = Column(Text)  # Teacher preparation steps
    teaching_sequence = Column(Text)  # Structured lesson sequence
    common_misconceptions = Column(Text)  # Expected student misconceptions
    extension_activities = Column(Text)  # Beyond-grade-level activities

    # Metadata
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default="draft")
    version = Column(Integer, default=1)

    # AI tracking
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)

    # Relationships
    unit = relationship("Unit", back_populates="lessons")
    topic = relationship("Topic", back_populates="lessons")
    learning_objects = relationship("LearningObject", back_populates="lesson", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="lesson", cascade="all, delete-orphan")


class LearningObject(Base):
    """Reusable, self-contained instructional unit (reading, example, diagram, video script, etc.)"""
    __tablename__ = "learning_objects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String(36), ForeignKey("lessons.id"), nullable=True)

    # Classification
    type = Column(String(100), nullable=False)  # reading, explanation, example, diagram, image_brief,
                                                 # video_script, interactive_activity, simulation, case_study,
                                                 # primary_source_activity, practice_exercise, discussion_prompt

    # Metadata
    title = Column(String(255), nullable=False)
    description = Column(Text)
    grade_level = Column(String(50))
    subject = Column(String(100))

    # Learning alignment
    learning_objective_ids = Column(JSON, default=[])
    standard_ids = Column(JSON, default=[])
    prerequisites = Column(JSON, default=[])  # Prerequisite skills/knowledge

    # Content
    content = Column(Text, nullable=False)  # Actual instructional content

    # Assessment of learning
    difficulty = Column(String(50))  # Easy, Medium, Hard
    cognitive_demand = Column(String(50))  # Remember, Understand, Apply, Analyze, Evaluate, Create
    duration_minutes = Column(Integer)

    # Accessibility
    accessibility_metadata = Column(JSON, default={})  # Alt text, captions, reading level, etc.

    # Versioning
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default="draft")
    version = Column(Integer, default=1)

    # AI tracking
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)

    # Relationships
    lesson = relationship("Lesson", back_populates="learning_objects")


class Activity(Base):
    """Interactive learning experience (practice, simulation, discussion, project)"""
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String(36), ForeignKey("lessons.id"), nullable=False, index=True)
    learning_object_id = Column(String(36), ForeignKey("learning_objects.id"), nullable=True)
    sequence_number = Column(Integer)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    activity_type = Column(String(100))  # practice, simulation, discussion, project, debate, peer_review
    duration_minutes = Column(Integer)

    # Content
    instructions = Column(Text, nullable=False)
    student_facing_content = Column(Text)
    teacher_notes = Column(Text)

    # Alignment
    learning_objective_ids = Column(JSON, default=[])

    # Metadata
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50), default="draft")
    version = Column(Integer, default=1)

    # Relationships
    lesson = relationship("Lesson", back_populates="activities")


# ==================== ASSESSMENTS ====================

class Assessment(Base):
    """Collection of assessment items (formative or summative)"""
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String(36), ForeignKey("lessons.id"), nullable=True)
    unit_id = Column(String(36), ForeignKey("units.id"), nullable=True)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=True)

    # Classification
    assessment_type = Column(String(100))  # formative, summative, pre-assessment, exit-ticket
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Alignment
    learning_objective_ids = Column(JSON, default=[])
    standard_ids = Column(JSON, default=[])

    # Cognitive and difficulty
    cognitive_demand = Column(String(50))
    duration_minutes = Column(Integer)

    # Metadata
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50), default="draft")
    version = Column(Integer, default=1)

    # AI tracking
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)

    # Relationships
    lesson = relationship("Lesson")
    unit = relationship("Unit")
    course = relationship("Course", back_populates="assessments")
    items = relationship("AssessmentItem", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentItem(Base):
    """Individual assessment question or task"""
    __tablename__ = "assessment_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False, index=True)
    sequence_number = Column(Integer)

    # Question type and content
    question_type = Column(String(100), nullable=False)  # mc, multiple_select, short_answer, essay, matching, scenario
    question_text = Column(Text, nullable=False)
    stimulus = Column(Text, nullable=True)  # Supporting material (passage, image description, etc.)

    # Answer information
    options = Column(JSON, nullable=True)  # For multiple choice questions
    correct_answer = Column(String(500), nullable=True)
    distractors = Column(JSON, nullable=True)  # Common wrong answers (for analysis)
    explanation = Column(Text, nullable=True)  # Explanation of correct answer

    # Alignment
    standard_id = Column(String(255), nullable=True)
    learning_objective_id = Column(String(36), nullable=True)
    cognitive_demand = Column(String(50))  # Aligned with Bloom's taxonomy
    difficulty = Column(String(50))  # Easy, Medium, Hard

    # Scoring
    rubric = Column(JSON, nullable=True)  # Scoring rubric for constructed responses
    alignment_rationale = Column(Text)  # Why this item aligns to the objective

    # Metadata
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50), default="draft")
    version = Column(Integer, default=1)

    # Relationships
    assessment = relationship("Assessment", back_populates="items")


# ==================== STANDARDS & OBJECTIVES ====================

class StandardsFramework(Base):
    """Framework for educational standards (Common Core, NGSS, state standards, etc.)"""
    __tablename__ = "standards_frameworks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)  # Common Core, NGSS, CA Standards, etc.
    state_jurisdiction = Column(String(100), nullable=True)  # State/country code
    subject = Column(String(100), nullable=True)
    grade_levels = Column(JSON, default=[])  # List of grades covered
    version = Column(String(50))  # Framework version (e.g., 2010, 2021)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    standards = relationship("Standard", back_populates="framework", cascade="all, delete-orphan")


class Standard(Base):
    """Individual educational standard"""
    __tablename__ = "standards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    framework_id = Column(String(36), ForeignKey("standards_frameworks.id"), nullable=False, index=True)

    # Standard identification
    standard_code = Column(String(255), nullable=False, index=True)  # e.g., 4.NF.A.1, RL.9-10.1
    grade_level = Column(String(50), nullable=True)
    subject = Column(String(100), nullable=True)

    # Standard structure (hierarchical)
    domain = Column(String(255), nullable=True)  # Math domain, ELA strand, etc.
    strand = Column(String(255), nullable=True)  # Sub-category

    # Content
    description = Column(Text, nullable=False)
    skills = Column(JSON, default=[])  # List of skills required
    concepts = Column(JSON, default=[])  # List of concepts involved
    prerequisites = Column(JSON, default=[])  # Prerequisite standards

    # Cognitive demand
    cognitive_demand = Column(String(50), nullable=True)  # Remember, Understand, Apply, etc.

    # Hierarchy
    parent_standard_id = Column(String(36), nullable=True)  # Parent standard if hierarchical
    child_standard_ids = Column(JSON, default=[])  # Child standards

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    framework = relationship("StandardsFramework", back_populates="standards")


class LearningObjective(Base):
    """Specific learning outcome (SMART goal for a lesson/unit)"""
    __tablename__ = "learning_objectives"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Association with content structure
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=True)
    unit_id = Column(String(36), ForeignKey("units.id"), nullable=True)

    # Objective content
    objective_text = Column(Text, nullable=False)  # "Students will be able to..."
    bloom_level = Column(String(50))  # remember, understand, apply, analyze, evaluate, create

    # Alignment
    standard_ids = Column(JSON, default=[])  # Associated standards
    prerequisite_objectives = Column(JSON, default=[])  # Previous objectives required

    # Assessment and success
    success_criteria = Column(Text)  # How we know students achieved this
    assessment_methods = Column(JSON, default=[])  # How to assess (observation, quiz, project, etc.)

    # Metadata
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default="draft")

    # Relationships
    course = relationship("Course", back_populates="learning_objectives")


# ==================== ALIGNMENT TRACKING ====================

class ContentAlignment(Base):
    """Explicit mapping between content and standards/objectives"""
    __tablename__ = "content_alignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Source content
    source_type = Column(String(100), nullable=False)  # lesson, activity, assessment_item, learning_object
    source_id = Column(String(36), nullable=False, index=True)  # UUID of the content

    # Target (standard or objective)
    target_type = Column(String(100), nullable=False)  # standard, learning_objective
    target_id = Column(String(255), nullable=False, index=True)  # Standard code or objective ID

    # Alignment quality
    alignment_type = Column(String(50))  # strong, partial, weak
    confidence = Column(Float, default=0.5)  # 0.0 to 1.0 confidence score
    evidence = Column(Text)  # Why they align
    alignment_rationale = Column(Text)  # AI's explanation of alignment

    # Workflow status
    ai_suggested = Column(Boolean, default=True)
    status = Column(String(50), default="ai_suggested")  # ai_suggested, human_reviewed, approved, rejected

    # Review tracking
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Note: relationships handled via foreign_keys parameter in model definitions


# ==================== AI GENERATION TRACKING ====================

class AIPromptTemplate(Base):
    """Reusable AI prompt templates (version-controlled)"""
    __tablename__ = "ai_prompt_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)  # COURSE_GENERATOR, LESSON_GENERATOR, etc.
    version = Column(Integer, default=1)

    # Prompt content
    template = Column(Text, nullable=False)  # The actual prompt with placeholders
    description = Column(Text)  # Documentation
    use_case = Column(String(100), nullable=False)  # course_generation, lesson_generation, etc.

    # Parameters
    required_parameters = Column(JSON, default=[])  # List of parameter names

    # AI configuration
    model = Column(String(100), default="gpt-3.5-turbo")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, nullable=True)

    # Versioning
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class AIGenerationJob(Base):
    """Tracks asynchronous AI generation jobs"""
    __tablename__ = "ai_generation_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(100), nullable=False)  # generate_course, generate_lesson, analyze_alignment, etc.
    prompt_template_id = Column(String(36), ForeignKey("ai_prompt_templates.id"), nullable=True)

    # User and context
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Job inputs and outputs
    input_data = Column(JSON, nullable=False)  # The data passed to the AI
    output_data = Column(JSON, nullable=True)  # Generated content

    # Status
    status = Column(String(50), default="queued")  # queued, processing, completed, failed
    error_message = Column(Text, nullable=True)

    # AI tracking
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class AIGeneration(Base):
    """Record of each AI generation operation (for auditability)"""
    __tablename__ = "ai_generations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("ai_generation_jobs.id"), nullable=True)

    # What was generated
    content_type = Column(String(100), nullable=False)  # lesson, assessment, learning_objective, etc.
    content_id = Column(String(36), nullable=True)  # UUID of the generated content if saved

    # AI details
    prompt_template_id = Column(String(36), ForeignKey("ai_prompt_templates.id"), nullable=True)
    model = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, anthropic, local, etc.
    prompt_version = Column(Integer)
    temperature = Column(Float)

    # Inputs and outputs
    input_reference = Column(JSON)  # Summary of inputs used
    output_reference = Column(String(36), nullable=True)  # Where output was stored

    # User actions
    accepted_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    modifications = Column(JSON, nullable=True)  # Tracking changes user made

    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ==================== VERSIONING & REVIEWS ====================

class ContentVersion(Base):
    """Complete version history for any content object"""
    __tablename__ = "content_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_type = Column(String(100), nullable=False, index=True)  # lesson, course, assessment, etc.
    content_id = Column(String(36), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)

    # Change tracking
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    change_reason = Column(Text)  # Why was this version created
    change_summary = Column(Text)  # Summary of changes

    # Complete snapshot
    full_content = Column(JSON, nullable=False)  # Complete content snapshot

    # AI tracking
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)
    prompt_version = Column(Integer, nullable=True)

    # Workflow status
    review_status = Column(String(50))  # pending, approved, needs_revision
    approval_status = Column(String(50))  # pending, approved
    published_at = Column(DateTime, nullable=True)


class ContentReview(Base):
    """Review record for content in the approval workflow"""
    __tablename__ = "content_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Content being reviewed
    content_type = Column(String(100), nullable=False)
    content_id = Column(String(36), nullable=False, index=True)

    # Review stage
    review_stage = Column(String(100), nullable=False)  # author_review, sme_review, alignment_review, assessment_review, administrator_review

    # Workflow
    status = Column(String(50), default="pending")  # pending, in_progress, approved, rejected, needs_revision
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)

    # Review content
    reviewer_comments = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Version tracking
    previous_version_id = Column(String(36), nullable=True)
    next_version_id = Column(String(36), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== DIFFERENTIATION ====================

class DifferentiatedContent(Base):
    """Differentiated variants of content (scaffolds, enrichments, ELL support, etc.)"""
    __tablename__ = "differentiated_content"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Parent content
    parent_content_id = Column(String(36), nullable=False, index=True)
    parent_content_type = Column(String(100), nullable=False)  # lesson, activity, learning_object, etc.

    # Variant information
    variant_type = Column(String(100), nullable=False)  # scaffold, enrichment, els_support, alt_representation, simplified, advanced
    variant_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Content
    grade_level = Column(String(50), nullable=True)
    content = Column(Text, nullable=False)
    modifications = Column(Text)  # What was changed from parent

    # Alignment (usually same as parent unless explicitly changed)
    learning_objective_ids = Column(JSON, default=[])

    # Metadata
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50), default="draft")
    version = Column(Integer, default=1)
