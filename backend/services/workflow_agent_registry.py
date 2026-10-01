"""Executable registry for the workflow agents displayed by the API."""

from dataclasses import dataclass
from typing import Callable, Dict, Tuple

from workflows.workforce_alignment_state import WorkforceAlignmentState
from workflows.nodes import (
    calculate_coverage_and_gaps,
    extract_requirements,
    ingest_and_normalize_course_materials,
    inspect_package_contents,
    map_workforce_skills,
    retrieve_authorized_context,
    validate_request_and_access,
)
from workflows.workforce_alignment_graph import (
    accessibility_check,
    content_governance,
    draft_recommendations,
    emit_audit_events,
    generate_course_updates,
    persist_artifacts,
    validate_export_package,
)


AgentExecutor = Callable[[WorkforceAlignmentState], WorkforceAlignmentState]


@dataclass(frozen=True)
class WorkflowAgent:
    id: str
    name: str
    description: str
    agent_type: str
    workflow_type: str
    execute: AgentExecutor


def _agent(
    agent_id: str,
    name: str,
    description: str,
    agent_type: str,
    executor: AgentExecutor,
) -> WorkflowAgent:
    return WorkflowAgent(
        id=agent_id,
        name=name,
        description=description,
        agent_type=agent_type,
        workflow_type="workforce_alignment",
        execute=executor,
    )


AGENT_REGISTRY: Dict[str, WorkflowAgent] = {
    "validate_request_and_access": _agent(
        "validate_request_and_access", "Request Validator",
        "Validates required workflow inputs and establishes tenant context.",
        "validation", validate_request_and_access,
    ),
    "inspect_package_contents": _agent(
        "inspect_package_contents", "Package Inspector",
        "Validates the supported course package format.",
        "validation", inspect_package_contents,
    ),
    "extract_requirements": _agent(
        "extract_requirements", "Requirements Extractor",
        "Extracts institutional requirements using Amazon Bedrock.",
        "ai_powered", extract_requirements,
    ),
    "ingest_and_normalize_course_materials": _agent(
        "ingest_and_normalize_course_materials", "Course Ingestion Engine",
        "Extracts course structure, objectives, and embeddings.",
        "data_processing", ingest_and_normalize_course_materials,
    ),
    "retrieve_authorized_context": _agent(
        "retrieve_authorized_context", "Context Retriever",
        "Prepares authorized framework and course context for analysis.",
        "retrieval", retrieve_authorized_context,
    ),
    "map_workforce_skills": _agent(
        "map_workforce_skills", "Skill Mapper",
        "Maps workforce skills to course content using Amazon Bedrock.",
        "ai_powered", map_workforce_skills,
    ),
    "calculate_coverage_and_gaps": _agent(
        "calculate_coverage_and_gaps", "Gap Analyzer",
        "Calculates coverage and drafts prioritized recommendations.",
        "ai_powered", calculate_coverage_and_gaps,
    ),
    "draft_recommendations": _agent(
        "draft_recommendations", "Recommendation Engine",
        "Packages generated recommendations for review.",
        "analysis", draft_recommendations,
    ),
    "generate_course_updates": _agent(
        "generate_course_updates", "Content Generator",
        "Generates proposed course updates using Amazon Bedrock.",
        "ai_powered", generate_course_updates,
    ),
    "accessibility_check": _agent(
        "accessibility_check", "Accessibility Auditor",
        "Checks available course metadata for accessibility gaps.",
        "compliance", accessibility_check,
    ),
    "content_governance": _agent(
        "content_governance", "Content Governance Agent",
        "Checks required workflow artifacts before export.",
        "compliance", content_governance,
    ),
    "validate_export_package": _agent(
        "validate_export_package", "Export Validator",
        "Validates required artifacts and export readiness.",
        "validation", validate_export_package,
    ),
    "persist_artifacts": _agent(
        "persist_artifacts", "Data Persister",
        "Persists workflow results and generated artifacts.",
        "storage", persist_artifacts,
    ),
    "emit_audit_events": _agent(
        "emit_audit_events", "Audit Logger",
        "Records workflow lifecycle and audit events.",
        "compliance", emit_audit_events,
    ),
}

WORKFORCE_ALIGNMENT_AGENT_IDS: Tuple[str, ...] = tuple(AGENT_REGISTRY)


def list_workflow_agents():
    """Return public, non-secret metadata for all executable agents."""
    return [
        {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "agent_type": agent.agent_type,
            "status": "active",
            "workflow_type": agent.workflow_type,
        }
        for agent in AGENT_REGISTRY.values()
    ]