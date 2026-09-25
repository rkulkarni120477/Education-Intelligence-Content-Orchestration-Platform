"""
Workforce Alignment Workflow - LangGraph Graph Definition.

Constructs the LangGraph for the workforce alignment workflow with nodes,
edges, checkpoints, and human interrupts.
"""

from langgraph.graph import StateGraph, END
from workflows.workforce_alignment_state import WorkforceAlignmentState
from workflows.nodes import (
    validate_request_and_access,
    inspect_package_contents,
    extract_requirements,
    ingest_and_normalize_course_materials,
    retrieve_authorized_context,
    map_workforce_skills,
    calculate_coverage_and_gaps,
)
import logging

logger = logging.getLogger(__name__)


def create_workforce_alignment_graph():
    """
    Create the workforce alignment workflow graph.

    Returns:
        Compiled StateGraph ready for execution
    """

    # Create state graph
    workflow = StateGraph(WorkforceAlignmentState)

    # ===== ADD NODES =====

    # Validation and setup
    workflow.add_node("validate_request_and_access", validate_request_and_access)
    workflow.add_node("inspect_package_contents", inspect_package_contents)

    # Phase 1: Requirements
    workflow.add_node("extract_requirements", extract_requirements)
    workflow.add_node("requirements_confirmation_interrupt", requirements_confirmation_interrupt)

    # Phase 2: Ingestion
    workflow.add_node("ingest_and_normalize_course_materials", ingest_and_normalize_course_materials)
    workflow.add_node("course_structure_review_interrupt", course_structure_review_interrupt)

    # Phase 3: Retrieval & Analysis
    workflow.add_node("retrieve_authorized_context", retrieve_authorized_context)
    workflow.add_node("map_workforce_skills", map_workforce_skills)
    workflow.add_node("calculate_coverage_and_gaps", calculate_coverage_and_gaps)
    workflow.add_node("mapping_review_interrupt", mapping_review_interrupt)

    # Placeholder nodes for later phases
    workflow.add_node("draft_recommendations", lambda state: state)
    workflow.add_node("recommendations_approval_interrupt", lambda state: state)
    workflow.add_node("generate_course_updates", lambda state: state)
    workflow.add_node("accessibility_check", lambda state: state)
    workflow.add_node("accessibility_review_interrupt", lambda state: state)
    workflow.add_node("validate_export_package", lambda state: state)
    workflow.add_node("final_approval_interrupt", lambda state: state)
    workflow.add_node("persist_artifacts", lambda state: state)
    workflow.add_node("emit_audit_events", lambda state: state)

    # ===== ADD EDGES =====

    # Start → Validation
    workflow.set_entry_point("validate_request_and_access")

    # Validation flow
    workflow.add_edge("validate_request_and_access", "inspect_package_contents")
    workflow.add_edge("inspect_package_contents", "extract_requirements")

    # Requirements extraction → human checkpoint
    workflow.add_edge("extract_requirements", "requirements_confirmation_interrupt")

    # Checkpoint → decision flow
    workflow.add_conditional_edges(
        "requirements_confirmation_interrupt",
        requirements_confirmation_decision,
        {
            "confirmed": "ingest_and_normalize_course_materials",
            "rejected": END,
            "retry_extraction": "extract_requirements",
        }
    )

    # Ingestion flow
    workflow.add_edge("ingest_and_normalize_course_materials", "course_structure_review_interrupt")

    workflow.add_conditional_edges(
        "course_structure_review_interrupt",
        course_structure_decision,
        {
            "approved": "retrieve_authorized_context",
            "retry_ingestion": "ingest_and_normalize_course_materials",
            "abort": END,
        }
    )

    # Analysis flow
    workflow.add_edge("retrieve_authorized_context", "map_workforce_skills")
    workflow.add_edge("map_workforce_skills", "calculate_coverage_and_gaps")
    workflow.add_edge("calculate_coverage_and_gaps", "mapping_review_interrupt")

    workflow.add_conditional_edges(
        "mapping_review_interrupt",
        mapping_decision,
        {
            "approved": "draft_recommendations",
            "revise_mappings": "map_workforce_skills",
            "abort": END,
        }
    )

    # Recommendations & drafts (placeholder flow)
    workflow.add_edge("draft_recommendations", "recommendations_approval_interrupt")
    workflow.add_edge("recommendations_approval_interrupt", "generate_course_updates")

    # Accessibility
    workflow.add_edge("generate_course_updates", "accessibility_check")
    workflow.add_edge("accessibility_check", "accessibility_review_interrupt")
    workflow.add_edge("accessibility_review_interrupt", "validate_export_package")

    # Export & approval
    workflow.add_edge("validate_export_package", "final_approval_interrupt")
    workflow.add_edge("final_approval_interrupt", "persist_artifacts")

    # Finalization
    workflow.add_edge("persist_artifacts", "emit_audit_events")
    workflow.add_edge("emit_audit_events", END)

    # Compile the graph
    graph = workflow.compile()

    logger.info("✓ Workforce alignment workflow graph created and compiled")
    return graph


# ===== CHECKPOINT INTERRUPT & DECISION NODES =====

def requirements_confirmation_interrupt(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Interrupt for human requirements confirmation."""
    state.human_interrupt_pending = True
    state.human_interrupt_reason = "requirements_confirmation"
    state.current_checkpoint = "requirements_confirmation"
    state.workflow_status = "requirements"
    return state


def requirements_confirmation_decision(state: WorkforceAlignmentState) -> str:
    """Decide next node based on requirements confirmation."""
    if not state.human_decision:
        return "requirements_confirmation_interrupt"

    decision = state.human_decision.get("decision", "confirm")
    if decision == "confirmed":
        state.requirements_confirmed = True
        return "confirmed"
    elif decision == "retry":
        return "retry_extraction"
    else:
        return "rejected"


def course_structure_review_interrupt(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Interrupt for human course structure review."""
    state.human_interrupt_pending = True
    state.human_interrupt_reason = "course_structure_review"
    state.current_checkpoint = "course_structure_review"
    state.workflow_status = "ingestion"
    return state


def course_structure_decision(state: WorkforceAlignmentState) -> str:
    """Decide next node based on course structure review."""
    if not state.human_decision:
        return "course_structure_review_interrupt"

    decision = state.human_decision.get("decision", "approve")
    if decision == "approved":
        state.course_structure_extracted = True
        return "approved"
    elif decision == "retry":
        return "retry_ingestion"
    else:
        return "abort"


def mapping_review_interrupt(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Interrupt for human skill mapping and gap review."""
    state.human_interrupt_pending = True
    state.human_interrupt_reason = "mapping_review"
    state.current_checkpoint = "mapping_review"
    state.workflow_status = "analysis"
    return state


def mapping_decision(state: WorkforceAlignmentState) -> str:
    """Decide next node based on mapping review."""
    if not state.human_decision:
        return "mapping_review_interrupt"

    decision = state.human_decision.get("decision", "approve")
    if decision == "approved":
        return "approved"
    elif decision == "revise":
        return "revise_mappings"
    else:
        return "abort"
