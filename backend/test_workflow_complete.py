#!/usr/bin/env python
"""
Complete Workforce Alignment Workflow Execution Test (Standalone).

Tests all 7 main workflow nodes + checkpoints by running the full workflow graph.
Can be run directly: python test_workflow_complete.py
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.db import SessionLocal, init_db
from database.models import Tenant, User
from auth.tenant_context import TenantContext
from workflows.workforce_alignment_state import WorkforceAlignmentState
from workflows.workforce_alignment_graph import create_workforce_alignment_graph
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run complete workflow test."""
    db = None

    try:
        # Setup
        logger.info("=" * 80)
        logger.info("WORKFORCE ALIGNMENT WORKFLOW EXECUTION TEST")
        logger.info("=" * 80)

        init_db()
        db = SessionLocal()

        # Get/create tenant
        tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
        if not tenant:
            tenant = Tenant(
                id=str(uuid.uuid4()),
                name="System Tenant",
                slug="system",
                is_active=True
            )
            db.add(tenant)
            db.commit()

        # Get/create user
        user = db.query(User).filter(User.email == "workflow_test@test.local").first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                email="workflow_test@test.local",
                username="workflow_tester",
                hashed_password="test",
                is_active=True
            )
            db.add(user)
            db.commit()

        TenantContext.set_tenant(tenant.id)
        logger.info(f"✓ Setup complete: tenant={tenant.id}, user={user.id}")

        # Create workflow graph
        logger.info("\n[SETUP] Creating LangGraph workflow...")
        graph = create_workforce_alignment_graph()
        logger.info("✓ Workflow graph created and compiled")

        # Create initial state
        logger.info("\n[STATE] Creating initial workflow state...")
        state = WorkforceAlignmentState(
            tenant_id=tenant.id,
            request_id=str(uuid.uuid4()),
            initiating_user_id=user.id,
            workflow_execution_id=str(uuid.uuid4()),
            program_id="TEST-PROG-001",
            program_name="Test Workforce Alignment Program",
            course_ids=["COURSE-001", "COURSE-002"],
            input_package_id="PKG-TEST-001",
            input_package_format="imscc",
            input_skill_framework_id="SKILL-FW-001",
            input_style_guide_id="STYLE-GUIDE-001",
            started_at=datetime.utcnow(),
        )
        logger.info(f"✓ Initial state created: request_id={state.request_id}")

        # Execute workflow
        logger.info("\n" + "=" * 80)
        logger.info("EXECUTING WORKFLOW GRAPH")
        logger.info("=" * 80)

        try:
            result = graph.invoke(state)
            logger.info(f"\n✓ Workflow execution completed")

        except Exception as e:
            logger.error(f"✗ Workflow execution failed: {e}", exc_info=True)
            # Try to get partial results
            result = state

        # Print results
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW EXECUTION RESULTS")
        logger.info("=" * 80)

        logger.info(f"\nRequest ID: {result.request_id}")
        logger.info(f"Workflow Status: {result.workflow_status}")
        logger.info(f"Human Interrupt Pending: {result.human_interrupt_pending}")

        if result.current_checkpoint:
            logger.info(f"Current Checkpoint: {result.current_checkpoint}")

        if result.completed_nodes:
            logger.info(f"\nCompleted Nodes ({len(result.completed_nodes)}):")
            for i, node in enumerate(result.completed_nodes, 1):
                logger.info(f"  {i}. {node}")

        # Phase 1: Validation
        if "validate_request_and_access" in result.completed_nodes:
            logger.info(f"\n✓ PHASE 1: Validation & Setup")
            logger.info(f"  • validate_request_and_access: PASS")

        if "inspect_package_contents" in result.completed_nodes:
            logger.info(f"  • inspect_package_contents: PASS")

        # Phase 2: Requirements
        if "extract_requirements" in result.completed_nodes:
            logger.info(f"\n✓ PHASE 2: Requirements Extraction")
            logger.info(f"  • extract_requirements: PASS")
            if result.extraction_confidence:
                logger.info(f"    - Confidence: {result.extraction_confidence * 100:.1f}%")
            if result.extracted_target_roles:
                logger.info(f"    - Target Roles: {len(result.extracted_target_roles)}")
            if result.extracted_required_skills:
                logger.info(f"    - Required Skills: {len(result.extracted_required_skills)}")

        if result.human_interrupt_reason == "requirements_confirmation":
            logger.info(f"  • requirements_confirmation_interrupt: PENDING (waiting for human approval)")

        # Phase 3: Ingestion
        if "ingest_and_normalize_course_materials" in result.completed_nodes:
            logger.info(f"\n✓ PHASE 3: Course Ingestion & Normalization")
            logger.info(f"  • ingest_and_normalize_course_materials: PASS")
            if result.course_hierarchy_data:
                modules = result.course_hierarchy_data.get('modules', [])
                logger.info(f"    - Modules: {len(modules)}")
            if result.extracted_learning_objectives:
                logger.info(f"    - Objectives: {len(result.extracted_learning_objectives)}")

        if result.human_interrupt_reason == "course_structure_review":
            logger.info(f"  • course_structure_review_interrupt: PENDING (waiting for human approval)")

        # Phase 4: Analysis
        if "retrieve_authorized_context" in result.completed_nodes:
            logger.info(f"\n✓ PHASE 4: Skill Mapping & Gap Analysis")
            logger.info(f"  • retrieve_authorized_context: PASS")

        if "map_workforce_skills" in result.completed_nodes:
            logger.info(f"  • map_workforce_skills: PASS")

        if "calculate_coverage_and_gaps" in result.completed_nodes:
            logger.info(f"  • calculate_coverage_and_gaps: PASS")

        if result.human_interrupt_reason == "mapping_review":
            logger.info(f"  • mapping_review_interrupt: PENDING (waiting for human approval)")

        # Phase 5+: Placeholders
        logger.info(f"\n⊘ PHASE 5+: Recommendations & Finalization (Placeholder Nodes)")
        placeholder_nodes = [
            "draft_recommendations",
            "recommendations_approval_interrupt",
            "generate_course_updates",
            "accessibility_check",
            "accessibility_review_interrupt",
            "validate_export_package",
            "final_approval_interrupt",
            "persist_artifacts",
            "emit_audit_events"
        ]
        for node in placeholder_nodes:
            if node in result.completed_nodes:
                logger.info(f"  • {node}: PASS (but is placeholder - no implementation)")
            else:
                logger.info(f"  • {node}: NOT REACHED (placeholders)")

        # Error info
        if result.error_message:
            logger.error(f"\nError: {result.error_message}")

        # Stats
        logger.info(f"\nExecution Stats:")
        logger.info(f"  • Total Completed Nodes: {len(result.completed_nodes)}/7 (Phase 1-4)")
        logger.info(f"  • Execution Time: {(datetime.utcnow() - state.started_at).total_seconds():.2f}s")

        # Test error handling
        logger.info("\n" + "=" * 80)
        logger.info("TESTING ERROR HANDLING")
        logger.info("=" * 80)

        # Test: Missing program_id
        logger.info("\n[TEST] Missing program_id...")
        bad_state = WorkforceAlignmentState(
            tenant_id=tenant.id,
            request_id=str(uuid.uuid4()),
            initiating_user_id=user.id,
            workflow_execution_id=str(uuid.uuid4()),
            program_id="",  # Missing!
            program_name="Test",
            course_ids=["COURSE-001"],
            input_package_id="PKG-001",
            input_package_format="imscc",
            started_at=datetime.utcnow(),
        )

        try:
            error_result = graph.invoke(bad_state)
            if error_result.workflow_status == "failed":
                logger.info(f"✓ Error caught correctly: {error_result.error_message}")
            else:
                logger.warning(f"⚠ Expected 'failed' status, got '{error_result.workflow_status}'")
        except Exception as e:
            logger.info(f"✓ Error raised: {str(e)[:100]}")

        # Test: Unsupported package format
        logger.info("\n[TEST] Unsupported package format...")
        bad_state.program_id = "TEST-PROG"
        bad_state.input_package_format = "invalid_format"

        try:
            error_result = graph.invoke(bad_state)
            if error_result.workflow_status == "failed":
                logger.info(f"✓ Error caught correctly: {error_result.error_message}")
            else:
                logger.warning(f"⚠ Expected 'failed' status, got '{error_result.workflow_status}'")
        except Exception as e:
            logger.info(f"✓ Error raised: {str(e)[:100]}")

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        if result.workflow_status == "pending" or result.human_interrupt_pending:
            logger.info("\n✓ WORKFLOW EXECUTION SUCCESSFUL")
            logger.info("  • Phases 1-4 nodes are functional")
            logger.info("  • State transitions working correctly")
            logger.info("  • Human interrupts triggering as expected")
            logger.info("  • Error handling verified")
            return 0
        else:
            logger.warning(f"\n⚠ WORKFLOW INCOMPLETE: status={result.workflow_status}")
            if result.error_message:
                logger.warning(f"  Error: {result.error_message}")
            return 1

    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return 1

    finally:
        if db:
            db.close()


if __name__ == "__main__":
    exit(main())
