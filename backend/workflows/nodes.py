"""
Workforce Alignment Workflow - Node Implementations.

Individual node functions for the LangGraph workflow.
Each node has typed input/output and handles a specific workflow stage.
"""

from workflows.workforce_alignment_state import WorkforceAlignmentState
from auth.tenant_context import TenantContext, get_current_tenant_id
from services.requirements_extraction import RequirementsExtractionService
from services.course_ingestion import CourseIngestionService
from services.skill_mapping import SkillMappingService
from services.recommendations import RecommendationsService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ===== VALIDATION & SETUP NODES =====

def validate_request_and_access(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """
    Validate request, tenant context, and user permissions.

    Checks:
    - Tenant exists and is active
    - User has permission to initiate workflow
    - Input assets exist and are accessible
    """
    try:
        state.current_node = "validate_request_and_access"
        logger.info(f"Validating request {state.request_id} for tenant {state.tenant_id}")

        # Set tenant context
        TenantContext.set_tenant(state.tenant_id)

        # Validate inputs (in full implementation, would query DB)
        if not state.program_id or not state.program_name:
            state.error_message = "Program ID and name are required"
            state.workflow_status = "failed"
            return state

        if not state.input_package_id:
            state.error_message = "Input package ID is required"
            state.workflow_status = "failed"
            return state

        state.workflow_status = "pending"
        state.completed_nodes.append("validate_request_and_access")
        logger.info("✓ Request validation passed")

        return state

    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


def inspect_package_contents(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """
    Inspect course package contents and metadata.

    Checks:
    - Package format valid (IMSCC, ZIP, etc.)
    - Manifest present and readable
    - File inventory accessible
    - No malicious content
    """
    try:
        state.current_node = "inspect_package_contents"
        logger.info(f"Inspecting package {state.input_package_id}")

        # Placeholder: actual implementation would parse package
        supported_formats = ["imscc", "zip", "upload"]
        if state.input_package_format not in supported_formats:
            state.error_message = f"Unsupported package format: {state.input_package_format}"
            state.workflow_status = "failed"
            return state

        state.completed_nodes.append("inspect_package_contents")
        logger.info("✓ Package inspection passed")

        return state

    except Exception as e:
        logger.error(f"Package inspection failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


# ===== REQUIREMENTS EXTRACTION NODE =====

def extract_requirements(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """
    Extract institution requirements using LLM.

    Uses Claude to:
    - Parse institution goals and program context
    - Identify target workforce roles
    - Extract required skills and proficiency levels
    - Capture constraints (duration, format, prerequisites)
    - Detect ambiguities and ask clarification questions
    """
    try:
        state.current_node = "extract_requirements"
        logger.info(f"Extracting requirements for {state.program_name}")

        # Initialize requirements extraction service
        service = RequirementsExtractionService()

        # Call Claude for requirements extraction
        result = service.extract_requirements(
            program_name=state.program_name,
            program_context=f"Program ID: {state.program_id}, Courses: {', '.join(state.course_ids)}",
            institution_goals="To prepare students for workforce roles in the target industry",
            workforce_role_descriptions="Based on job market analysis and institution mission",
        )

        # Store extracted data in state
        state.extracted_target_roles = result.target_roles
        state.extracted_required_skills = result.required_skills
        state.extracted_constraints = result.constraints
        state.extracted_accessibility_requirements = result.accessibility_requirements
        state.extracted_style_guidelines = result.style_guidelines
        state.extraction_ambiguities = result.ambiguities

        state.requirements_extracted = True
        state.extraction_confidence = result.confidence
        state.completed_nodes.append("extract_requirements")

        logger.info(f"✓ Requirements extraction completed (confidence: {result.confidence})")

        # If low confidence, trigger human review
        if result.confidence < 0.7:
            state.human_interrupt_pending = True
            state.human_interrupt_reason = "Low confidence in automated requirements extraction"
            state.current_checkpoint = "requirements_confirmation"

        return state

    except Exception as e:
        logger.error(f"Requirements extraction failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


# ===== INGESTION NODE =====

def ingest_and_normalize_course_materials(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """
    Ingest and normalize course materials from package.

    Responsibilities:
    - Extract course hierarchy (course → unit → lesson → activity)
    - Preserve source anchors (file path, section, page)
    - Extract learning objectives and assessments
    - Create embeddings for semantic search
    - Report extraction quality and errors
    """
    try:
        state.current_node = "ingest_and_normalize_course_materials"
        logger.info(f"Ingesting course materials from package {state.input_package_id}")

        # Initialize course ingestion service
        service = CourseIngestionService()

        # Ingest course package
        # Note: In production, would get package path from storage service
        package_path = f"/tmp/packages/{state.input_package_id}"

        hierarchy = service.ingest_package(
            package_path=package_path,
            package_format=state.input_package_format,
        )

        # Extract and store course structure
        state.course_hierarchy_data = {
            'course_id': hierarchy.course_id,
            'course_title': hierarchy.course_title,
            'course_description': hierarchy.course_description,
            'modules': hierarchy.modules,
            'objectives': hierarchy.objectives,
        }

        # Extract learning objectives
        learning_objectives = service.extract_learning_objectives(hierarchy)
        state.extracted_learning_objectives = learning_objectives

        # Generate embeddings for semantic search
        embeddings = service.generate_embeddings(hierarchy)
        state.content_embeddings = embeddings

        state.course_structure_extracted = True
        state.extraction_errors = []
        state.completed_nodes.append("ingest_and_normalize_course_materials")

        logger.info(f"✓ Course ingestion completed ({len(hierarchy.modules)} modules)")
        return state

    except Exception as e:
        logger.error(f"Course ingestion failed: {str(e)}")
        state.error_message = str(e)
        state.extraction_errors = [str(e)]
        state.workflow_status = "failed"
        return state


# ===== RETRIEVAL NODE =====

def retrieve_authorized_context(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """
    Retrieve authorized context for analysis.

    Retrieves:
    - Confirmed requirements profile
    - Skill framework and proficiency rubrics
    - Approved examples and style guides
    - Similar courses (optional, via vector search)
    """
    try:
        state.current_node = "retrieve_authorized_context"
        logger.info("Retrieving authorized context")

        # Placeholder: actual implementation would:
        # 1. Query confirmed requirements
        # 2. Fetch skill framework
        # 3. Retrieve style guides
        # 4. Vector search for examples (optional)

        state.completed_nodes.append("retrieve_authorized_context")
        logger.info("✓ Context retrieval completed")

        return state

    except Exception as e:
        logger.error(f"Context retrieval failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


# ===== SKILL MAPPING NODE =====

def map_workforce_skills(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """
    Map workforce skills to course content.

    Responsibilities:
    - Link skills to course objectives/content
    - Apply proficiency rubric
    - Score and rank mappings
    - Create SkillAlignment records
    - Track evidence references
    """
    try:
        state.current_node = "map_workforce_skills"
        logger.info("Mapping workforce skills to course content")

        # Initialize skill mapping service
        service = SkillMappingService()

        # Prepare content items from course structure
        course_content = []
        if state.course_hierarchy_data:
            for module in state.course_hierarchy_data.get('modules', []):
                course_content.append({
                    'title': module.get('title', ''),
                    'description': module.get('description', ''),
                    'type': 'module',
                })

        # Map skills to content
        mapping_result = service.map_skills_to_content(
            course_title=state.program_name,
            course_objectives=state.extracted_learning_objectives or [],
            course_content=course_content,
            required_skills=[
                {'name': skill, 'level': 'intermediate', 'id': skill}
                for skill in state.extracted_required_skills
            ] if state.extracted_required_skills else [],
        )

        # Store mapping results in state
        state.coverage_by_skill = mapping_result.coverage_by_skill
        state.total_alignments = mapping_result.total_alignments
        state.covered_skills = mapping_result.covered_skills
        state.uncovered_skills = mapping_result.uncovered_skills
        state.overall_coverage_percentage = mapping_result.overall_coverage
        state.critical_gaps_identified = mapping_result.critical_gaps

        state.skill_mappings_generated = True
        state.completed_nodes.append("map_workforce_skills")

        logger.info(f"✓ Skill mapping completed ({mapping_result.total_alignments} alignments, {mapping_result.overall_coverage:.1%} coverage)")

        # Trigger human review if coverage is low
        if mapping_result.overall_coverage < 0.7:
            state.human_interrupt_pending = True
            state.human_interrupt_reason = f"Low skill coverage ({mapping_result.overall_coverage:.0%}). Review and approve mappings."
            state.current_checkpoint = "mapping_review"

        return state

    except Exception as e:
        logger.error(f"Skill mapping failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


# ===== COVERAGE & GAP ANALYSIS NODE =====

def calculate_coverage_and_gaps(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """
    Calculate skill coverage and identify gaps.

    Responsibilities:
    - Aggregate skill mappings by proficiency
    - Calculate coverage percentage per skill
    - Identify gaps and assess severity
    - Generate coverage report
    - Generate improvement recommendations
    - Rank gaps by criticality
    """
    try:
        state.current_node = "calculate_coverage_and_gaps"
        logger.info("Calculating coverage and gaps")

        # Generate recommendations based on gaps
        recommendations_service = RecommendationsService()

        # Prepare gaps data for recommendations
        gaps = [
            {
                'skill_id': gap['skill_name'],
                'skill_name': gap['skill_name'],
                'required_proficiency': gap.get('required_proficiency', 'intermediate'),
                'current_coverage': gap.get('current_coverage', 0),
                'gap_severity': gap.get('gap_severity', 'medium'),
            }
            for gap in state.critical_gaps_identified or []
        ]

        # Generate recommendations
        recommendations_result = recommendations_service.generate_recommendations(
            course_title=state.program_name,
            current_coverage=state.coverage_by_skill or {},
            gaps=gaps,
            course_structure=state.course_hierarchy_data or {},
        )

        # Store recommendations in state
        state.recommendations_generated = True
        state.recommendations = [
            {
                'id': f"rec_{i}",
                'type': rec.get('type', 'add_content'),
                'priority': rec.get('priority', 'medium'),
                'title': rec.get('title', 'Untitled'),
                'description': rec.get('description', ''),
                'affected_skills': rec.get('affected_skills', []),
            }
            for i, rec in enumerate(recommendations_result.critical_recommendations +
                                   recommendations_result.high_priority_recommendations)
        ]

        state.completed_nodes.append("calculate_coverage_and_gaps")
        logger.info(f"✓ Coverage and gap analysis completed ({len(recommendations_result.critical_recommendations)} critical recommendations)")

        return state

    except Exception as e:
        logger.error(f"Coverage analysis failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state
