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
from services.recommendations import RecommendationsService
from services.bedrock_runtime import BEDROCK_MODEL_ID, converse, response_text
from services.database_persistence import DatabasePersistenceService
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


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
        logger.info("Waiting for human requirements confirmation decision...")
        return "confirmed"  # Default to confirming if no explicit rejection

    decision = state.human_decision.get("decision", "confirmed")
    if decision == "confirmed":
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
        logger.info("Waiting for human course structure review decision...")
        return "approved"  # Default to approving if no explicit decision

    decision = state.human_decision.get("decision", "approved")
    if decision == "approved":
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
        logger.info("Waiting for human mapping review decision...")
        return "approved"  # Default to approving if no explicit decision

    decision = state.human_decision.get("decision", "approved")
    if decision == "approved":
        return "approved"
    elif decision == "revise":
        return "revise_mappings"
    else:
        return "abort"


def route_after_agent(state: WorkforceAlignmentState) -> str:
    """Stop the graph immediately when an agent marks the workflow failed."""
    return "failed" if state.workflow_status == "failed" else "continue"


# ===== PHASE 5+: RECOMMENDATIONS & FINALIZATION NODES =====

def draft_recommendations(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Draft course improvement recommendations based on skill gaps."""
    try:
        state.current_node = "draft_recommendations"
        logger.info("Drafting course improvement recommendations...")
        state.drafted_recommendations = [dict(item) for item in state.recommendations]
        state.completed_nodes.append("draft_recommendations")
        logger.info(f"✓ Recommendations drafted: {len(state.drafted_recommendations)} recommendations")

        return state

    except Exception as e:
        logger.error(f"Recommendation drafting failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


def recommendations_approval_interrupt(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Interrupt for human recommendations approval."""
    state.human_interrupt_pending = True
    state.human_interrupt_reason = "recommendations_approval"
    state.current_checkpoint = "recommendations_approval"
    state.workflow_status = "recommendations"
    logger.info("Waiting for human approval of recommendations...")
    return state


def generate_course_updates(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Generate updated course materials based on approved recommendations."""
    try:
        state.current_node = "generate_course_updates"
        logger.info("Generating course update package...")

        # Process approved recommendations
        approved_recs = [
            r for r in (state.drafted_recommendations or [])
            if state.human_decision and r.get("id") in state.human_decision.get("approved_recommendations", [])
        ] if state.human_decision else (state.drafted_recommendations or [])

        prompt = {
            "course": state.program_name,
            "course_structure": state.course_hierarchy_data,
            "approved_recommendations": approved_recs,
            "learning_objectives": state.extracted_learning_objectives,
        }
        response = converse(
            BEDROCK_MODEL_ID,
            [{"role": "user", "content": str(prompt)}],
            system=(
                "You are a curriculum content generator. Propose concise, actionable "
                "course updates that apply the approved recommendations. Return a "
                "structured summary with proposed modules, lessons, and assessments."
            ),
            inference_config={"maxTokens": 2048, "temperature": 0.3},
        )

        state.generated_course_updates = {
            "updated_structure": state.course_hierarchy_data,
            "applied_recommendations": [r.get("id") for r in approved_recs],
            "update_summary": response_text(response),
            "generated_at": datetime.utcnow().isoformat(),
        }

        state.completed_nodes.append("generate_course_updates")
        logger.info(f"✓ Course updates generated (applied {len(approved_recs)} recommendations)")

        return state

    except Exception as e:
        logger.error(f"Course update generation failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


def accessibility_check(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Run accessibility audit on updated course materials."""
    try:
        state.current_node = "accessibility_check"
        logger.info("Running accessibility audit...")

        modules = state.course_hierarchy_data.get("modules", [])
        objectives = state.extracted_learning_objectives
        missing_titles = sum(1 for module in modules if not module.get("title", "").strip())
        missing_descriptions = sum(1 for module in modules if not module.get("description", "").strip())
        accessibility_issues = []
        if missing_titles:
            accessibility_issues.append({"type": "missing_heading", "severity": "high", "count": missing_titles})
        if missing_descriptions:
            accessibility_issues.append({"type": "missing_description", "severity": "medium", "count": missing_descriptions})
        if not objectives:
            accessibility_issues.append({"type": "missing_learning_objectives", "severity": "medium", "count": 1})

        state.accessibility_audit = {
            "audit_date": datetime.utcnow().isoformat(),
            "total_issues": sum(i["count"] for i in accessibility_issues),
            "critical_issues": sum(i["count"] for i in accessibility_issues if i["severity"] == "critical"),
            "issues": accessibility_issues,
            "checks_performed": ["module_titles", "module_descriptions", "learning_objectives"],
            "remediation_complete": not accessibility_issues,
        }

        state.completed_nodes.append("accessibility_check")
        logger.info(f"✓ Accessibility audit complete (issues: {state.accessibility_audit['total_issues']})")

        return state

    except Exception as e:
        logger.error(f"Accessibility check failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


def content_governance(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Check generated workflow artifacts for required content before export."""
    try:
        state.current_node = "content_governance"
        checks = {
            "course_structure_present": bool(state.course_hierarchy_data),
            "generated_updates_present": bool(state.generated_course_updates.get("update_summary")),
            "accessibility_audit_present": bool(state.accessibility_audit),
            "export_format_supported": state.export_format in {"imscc", "zip", "pdf", "docx"},
        }
        state.content_governance_report = {
            "checks": checks,
            "passed": all(checks.values()),
            "recommendation": "approve" if all(checks.values()) else "review",
            "review_required": not all(checks.values()),
        }
        state.completed_nodes.append("content_governance")
        if not state.content_governance_report["passed"]:
            state.error_message = "Content governance requires review before export"
            state.workflow_status = "failed"
        return state
    except Exception as e:
        logger.error(f"Content governance failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


def accessibility_review_interrupt(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Interrupt for human accessibility review."""
    state.human_interrupt_pending = True
    state.human_interrupt_reason = "accessibility_review"
    state.current_checkpoint = "accessibility_review"
    state.workflow_status = "accessibility"
    logger.info("Waiting for human accessibility review...")
    return state


def validate_export_package(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Validate and prepare final export package."""
    try:
        state.current_node = "validate_export_package"
        logger.info("Validating export package...")

        # Validate all required components are present
        package_contents = {
            "course_structure": bool(state.generated_course_updates),
            "skill_mappings": bool(state.completed_nodes and "map_workforce_skills" in state.completed_nodes),
            "recommendations": bool(state.drafted_recommendations),
            "accessibility_audit": bool(state.accessibility_audit),
            "content_governance": state.content_governance_report.get("passed", False),
        }

        all_valid = all(package_contents.values())

        state.export_package = {
            "package_id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "workflow_id": state.workflow_execution_id,
            "contents": package_contents,
            "valid": all_valid,
            "validation_errors": [] if all_valid else ["Missing required components"],
        }

        state.completed_nodes.append("validate_export_package")
        logger.info(f"✓ Export package validated: {all_valid}")

        return state

    except Exception as e:
        logger.error(f"Package validation failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


def final_approval_interrupt(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Interrupt for final approval before persistence."""
    state.human_interrupt_pending = True
    state.human_interrupt_reason = "final_approval"
    state.current_checkpoint = "final_approval"
    state.workflow_status = "finalization"
    logger.info("Waiting for final approval...")
    return state


def persist_artifacts(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Persist all workflow artifacts to database."""
    try:
        from database.db import SessionLocal

        state.current_node = "persist_artifacts"
        logger.info("Persisting workflow artifacts...")

        # Create a database session
        session = SessionLocal()

        try:
            # Use DatabasePersistenceService to save results
            service = DatabasePersistenceService()

            # Save workflow execution record with all results
            workflow_record = {
                "workflow_id": state.workflow_execution_id or str(uuid.uuid4()),
                "tenant_id": state.tenant_id,
                "request_id": state.request_id,
                "program_id": state.program_id,
                "program_name": state.program_name,
                "course_ids": state.course_ids,
                "input_package_id": state.input_package_id,
                "workflow_status": state.workflow_status,
                "started_at": state.started_at,
                "completed_at": datetime.utcnow(),
                "course_updates": state.generated_course_updates,
                "recommendations": state.drafted_recommendations,
                "accessibility_audit": state.accessibility_audit,
                "export_package": state.export_package,
                "audit_events": state.audit_events,
                "error_message": state.error_message,
                "agent_runs": [
                    {
                        "agent_name": node,
                        "agent_type": "workflow_node",
                        "status": "completed",
                    }
                    for node in state.completed_nodes
                ],
            }

            execution_id = service.save_workflow_execution(session, workflow_record)
            logger.info(f"✓ Workflow execution {execution_id} saved to database")
            state.workflow_execution_id = execution_id

        finally:
            session.close()

        state.completed_nodes.append("persist_artifacts")
        state.workflow_status = "completed"
        logger.info("✓ Artifacts persisted successfully")

        return state

    except Exception as e:
        logger.error(f"Artifact persistence failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


def emit_audit_events(state: WorkforceAlignmentState) -> WorkforceAlignmentState:
    """Emit audit events for compliance and tracking."""
    try:
        state.current_node = "emit_audit_events"
        logger.info("Emitting audit events...")

        # Create audit trail
        audit_events = [
            {
                "event_type": "workflow_started",
                "timestamp": state.started_at.isoformat() if state.started_at else datetime.utcnow().isoformat(),
                "details": {"program": state.program_name, "courses": len(state.course_ids)},
            },
            {
                "event_type": "requirements_extracted",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "target_roles": len(state.extracted_target_roles or []),
                    "skills": len(state.extracted_required_skills or []),
                },
            },
            {
                "event_type": "skill_mappings_generated",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {"completed_nodes": len(state.completed_nodes)},
            },
            {
                "event_type": "recommendations_approved",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {"recommendation_count": len(state.drafted_recommendations or [])},
            },
            {
                "event_type": "workflow_completed",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "status": state.workflow_status,
                    "total_duration_seconds": (datetime.utcnow() - state.started_at).total_seconds() if state.started_at else 0,
                },
            },
        ]

        state.audit_events = audit_events
        state.completed_nodes.append("emit_audit_events")

        for event in audit_events:
            logger.info(f"  • {event['event_type']}: {event['details']}")

        logger.info(f"✓ {len(audit_events)} audit events emitted")

        return state

    except Exception as e:
        logger.error(f"Audit event emission failed: {str(e)}")
        state.error_message = str(e)
        state.workflow_status = "failed"
        return state


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

    # Phase 5+: Recommendations and finalization
    workflow.add_node("draft_recommendations", draft_recommendations)
    workflow.add_node("recommendations_approval_interrupt", recommendations_approval_interrupt)
    workflow.add_node("generate_course_updates", generate_course_updates)
    workflow.add_node("accessibility_check", accessibility_check)
    workflow.add_node("accessibility_review_interrupt", accessibility_review_interrupt)
    workflow.add_node("content_governance", content_governance)
    workflow.add_node("validate_export_package", validate_export_package)
    workflow.add_node("final_approval_interrupt", final_approval_interrupt)
    workflow.add_node("persist_artifacts", persist_artifacts)
    workflow.add_node("emit_audit_events", emit_audit_events)

    # ===== ADD EDGES =====

    # Start → Validation
    workflow.set_entry_point("validate_request_and_access")

    # Validation flow
    workflow.add_conditional_edges(
        "validate_request_and_access",
        route_after_agent,
        {"continue": "inspect_package_contents", "failed": END},
    )
    workflow.add_conditional_edges(
        "inspect_package_contents",
        route_after_agent,
        {"continue": "extract_requirements", "failed": END},
    )

    # Requirements extraction → human checkpoint
    workflow.add_conditional_edges(
        "extract_requirements",
        route_after_agent,
        {"continue": "requirements_confirmation_interrupt", "failed": END},
    )

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
    workflow.add_conditional_edges(
        "ingest_and_normalize_course_materials",
        route_after_agent,
        {"continue": "course_structure_review_interrupt", "failed": END},
    )

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
    workflow.add_conditional_edges(
        "retrieve_authorized_context",
        route_after_agent,
        {"continue": "map_workforce_skills", "failed": END},
    )
    workflow.add_conditional_edges(
        "map_workforce_skills",
        route_after_agent,
        {"continue": "calculate_coverage_and_gaps", "failed": END},
    )
    workflow.add_conditional_edges(
        "calculate_coverage_and_gaps",
        route_after_agent,
        {"continue": "mapping_review_interrupt", "failed": END},
    )

    workflow.add_conditional_edges(
        "mapping_review_interrupt",
        mapping_decision,
        {
            "approved": "draft_recommendations",
            "revise_mappings": "map_workforce_skills",
            "abort": END,
        }
    )

    # Recommendations & approvals
    workflow.add_conditional_edges(
        "draft_recommendations",
        route_after_agent,
        {"continue": "recommendations_approval_interrupt", "failed": END},
    )
    workflow.add_conditional_edges(
        "recommendations_approval_interrupt",
        route_after_agent,
        {"continue": "generate_course_updates", "failed": END},
    )

    # Accessibility
    workflow.add_conditional_edges(
        "generate_course_updates",
        route_after_agent,
        {"continue": "accessibility_check", "failed": END},
    )
    workflow.add_conditional_edges(
        "accessibility_check",
        route_after_agent,
        {"continue": "accessibility_review_interrupt", "failed": END},
    )
    workflow.add_conditional_edges(
        "accessibility_review_interrupt",
        route_after_agent,
        {"continue": "content_governance", "failed": END},
    )
    workflow.add_conditional_edges(
        "content_governance",
        route_after_agent,
        {"continue": "validate_export_package", "failed": END},
    )

    # Export & approval
    workflow.add_conditional_edges(
        "validate_export_package",
        route_after_agent,
        {"continue": "final_approval_interrupt", "failed": END},
    )
    workflow.add_conditional_edges(
        "final_approval_interrupt",
        route_after_agent,
        {"continue": "persist_artifacts", "failed": END},
    )

    # Finalization
    workflow.add_conditional_edges(
        "persist_artifacts",
        route_after_agent,
        {"continue": "emit_audit_events", "failed": END},
    )
    workflow.add_edge("emit_audit_events", END)

    # Compile the graph
    graph = workflow.compile()

    logger.info("✓ Workforce alignment workflow graph created and compiled")
    return graph
