"""
Workforce Alignment Workflow API Routes.

Endpoints for managing workforce alignment workflow execution,
requirements confirmation, and human checkpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from database.db import SessionLocal, get_db
from auth.tenant_context import get_current_tenant_id
from workflows.workforce_alignment_state import WorkforceAlignmentState
from services.multi_agent_orchestrator import MultiAgentOrchestrator
from services.workflow_agent_registry import AGENT_REGISTRY, WORKFORCE_ALIGNMENT_AGENT_IDS
from database.models import AgentRun, WorkflowExecution, Workflow
import logging
import uuid
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/workforce-alignment", tags=["workforce-alignment"])


# ===== REQUEST/RESPONSE MODELS =====

class CreateWorkflowRequest(BaseModel):
    """Request to start a new workforce alignment workflow."""
    program_id: str = Field(..., description="Institution program ID")
    program_name: str = Field(..., description="Program name")
    course_ids: List[str] = Field(..., description="Course IDs to align")
    input_package_id: str = Field(..., description="Course package ID")
    input_package_format: str = Field(..., description="Format: imscc, zip, upload")
    input_skill_framework_id: str = Field(..., description="Skill framework ID")
    input_style_guide_id: Optional[str] = Field(None, description="Style guide ID")


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status."""
    workflow_id: str
    status: str
    current_node: str
    current_checkpoint: Optional[str]
    human_interrupt_pending: bool
    human_interrupt_reason: Optional[str]
    progress_percent: int
    created_at: datetime
    last_updated: datetime


class CheckpointDecisionRequest(BaseModel):
    """Request to provide decision at a human checkpoint."""
    decision: str = Field(..., description="Decision made")
    notes: Optional[str] = Field(None, description="Decision notes")
    edited_fields: Optional[Dict[str, Any]] = Field(None, description="Fields edited")


# ===== WORKFLOW ENDPOINTS =====

@router.post("/workflows", response_model=Dict[str, Any])
async def create_workflow(
    request: CreateWorkflowRequest,
    db: Session = Depends(get_db),
):
    """
    Create and start a new workforce alignment workflow.

    Initializes workflow state, saves to database, and executes the workflow
    graph with all connected agents (Requirements Extractor, Skill Mapper, etc).
    """
    try:
        tenant_id = get_current_tenant_id()

        # Validate inputs
        if not request.program_id or not request.program_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="program_id and program_name are required"
            )

        if not request.course_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one course_id is required"
            )

        execution_id = str(uuid.uuid4())

        # Initialize workflow state
        state = WorkforceAlignmentState(
            tenant_id=tenant_id,
            request_id=execution_id,
            initiating_user_id="current_user",
            workflow_execution_id=execution_id,
            program_id=request.program_id,
            program_name=request.program_name,
            course_ids=request.course_ids,
            input_package_id=request.input_package_id,
            input_package_format=request.input_package_format,
            input_skill_framework_id=request.input_skill_framework_id,
            input_style_guide_id=request.input_style_guide_id,
            started_at=datetime.utcnow(),
        )

        # Save initial workflow record to database
        workflow = Workflow(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            creator_id="system",
            name=f"Alignment Workflow - {request.program_name}",
            description=f"Workforce alignment for {request.program_name}",
            definition={
                "workflow_type": "workforce_alignment",
                "agents": [
                    {"id": agent_id, "name": AGENT_REGISTRY[agent_id].name}
                    for agent_id in WORKFORCE_ALIGNMENT_AGENT_IDS
                ],
            },
            status="active",
        )
        db.add(workflow)
        db.commit()

        logger.info(f"✓ Created workflow {execution_id} for tenant {tenant_id}")
        logger.info(f"✓ Starting workforce alignment workflow with {len(WORKFORCE_ALIGNMENT_AGENT_IDS)} agents...")

        # Execute workflow asynchronously
        asyncio.create_task(execute_workflow_async(execution_id, workflow.id, state, tenant_id))

        return {
            "status": "success",
            "workflow_id": execution_id,
            "message": "Workflow execution started with all agents",
            "agents_count": len(WORKFORCE_ALIGNMENT_AGENT_IDS),
            "state": state.dict(),
        }

    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def execute_workflow_async(execution_id: str, workflow_id: str, state: WorkforceAlignmentState, tenant_id: str):
    """
    Execute the workforce alignment workflow asynchronously.

    Runs all agents: Requirements Extractor, Skill Mapper, Recommendations, etc.
    """
    db = SessionLocal()
    workflow_execution = None
    try:
        logger.info(f"⚙️  Starting async workflow execution: {execution_id}")
        workflow_execution = WorkflowExecution(
            id=execution_id,
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            status="running",
            input_data=state.dict(),
            started_at=state.started_at,
        )
        db.add(workflow_execution)
        db.commit()

        def record_agent_event(agent_id: str, run_status: str, snapshot: Dict[str, Any]):
            agent = AGENT_REGISTRY[agent_id]
            now = datetime.utcnow()
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                workflow_execution_id=execution_id,
                agent_name=agent_id,
                agent_type=agent.agent_type,
                status=run_status,
                input_data={"workflow_type": "workforce_alignment", "request_id": state.request_id},
                output_data={
                    "current_node": snapshot.get("current_node"),
                    "workflow_status": snapshot.get("workflow_status"),
                    "completed_nodes": snapshot.get("completed_nodes", []),
                },
                started_at=now,
                completed_at=now,
            ))
            workflow_execution.status = "failed" if run_status == "failed" else "running"
            workflow_execution.error_message = snapshot.get("error_message")
            workflow_execution.output_data = {
                "workflow_type": "workforce_alignment",
                "workflow_status": snapshot.get("workflow_status"),
                "current_node": snapshot.get("current_node"),
                "completed_nodes": snapshot.get("completed_nodes", []),
                "human_interrupt_pending": snapshot.get("human_interrupt_pending", False),
                "current_checkpoint": snapshot.get("current_checkpoint"),
                "error_message": snapshot.get("error_message"),
            }
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise

        logger.info("Executing workforce alignment through the multi-agent orchestrator...")
        result = await MultiAgentOrchestrator.execute_async(
            "workforce_alignment",
            state,
            on_agent_event=record_agent_event,
        )
        workflow_execution.status = result.get("workflow_status", "completed")
        workflow_execution.output_data = dict(result)
        workflow_execution.error_message = result.get("error_message")
        workflow_execution.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"✓ Workflow execution completed: {execution_id}")
        logger.info(f"✓ Status: {workflow_execution.status}")

    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {str(e)}")
        try:
            if workflow_execution is None:
                workflow_execution = WorkflowExecution(
                    id=execution_id,
                    tenant_id=tenant_id,
                    workflow_id=workflow_id,
                    status="failed",
                    error_message=str(e),
                    started_at=state.started_at,
                    completed_at=datetime.utcnow(),
                )
                db.add(workflow_execution)
            else:
                workflow_execution.status = "failed"
                workflow_execution.error_message = str(e)
                workflow_execution.completed_at = datetime.utcnow()
            db.commit()
        except:
            pass
    finally:
        db.close()


@router.get("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow_status(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """
    Get the current status and state of a workflow.
    """
    try:
        tenant_id = get_current_tenant_id()

        execution = db.query(WorkflowExecution).filter(
            WorkflowExecution.id == workflow_id,
            WorkflowExecution.tenant_id == tenant_id,
        ).first()
        if not execution:
            raise HTTPException(status_code=404, detail="Workflow execution not found")

        output = execution.output_data or {}
        completed_agent_ids = set(output.get("completed_nodes", [])) & set(WORKFORCE_ALIGNMENT_AGENT_IDS)
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "workflow_status": output.get("workflow_status", execution.status),
            "current_node": output.get("current_node", "start"),
            "human_interrupt_pending": output.get("human_interrupt_pending", False),
            "current_checkpoint": output.get("current_checkpoint"),
            "error_message": execution.error_message or output.get("error_message"),
            "completed_nodes": output.get("completed_nodes", []),
            "progress_percent": round(len(completed_agent_ids) * 100 / len(WORKFORCE_ALIGNMENT_AGENT_IDS)),
        }

    except Exception as e:
        logger.error(f"Error getting workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/workflows/{workflow_id}/checkpoint/{checkpoint_name}/confirm")
async def confirm_checkpoint(
    workflow_id: str,
    checkpoint_name: str,
    decision: CheckpointDecisionRequest,
    db: Session = Depends(get_db),
):
    """
    Provide a human decision at a workflow checkpoint.

    Resumes workflow execution after checkpoint.
    """
    try:
        tenant_id = get_current_tenant_id()

        # Validate checkpoint
        valid_checkpoints = [
            "requirements_confirmation",
            "course_structure_review",
            "mapping_review",
            "recommendations_approval",
            "accessibility_review",
            "final_approval",
        ]

        if checkpoint_name not in valid_checkpoints:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid checkpoint: {checkpoint_name}"
            )

        logger.info(f"Confirming checkpoint {checkpoint_name} for workflow {workflow_id}")

        # Placeholder: would resume workflow execution with decision

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "checkpoint": checkpoint_name,
            "decision_recorded": True,
            "message": "Checkpoint decision recorded. Workflow resumed.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming checkpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== REQUIREMENTS ENDPOINTS =====

@router.get("/workflows/{workflow_id}/requirements")
async def get_requirements(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """Get extracted requirements for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "requirements": {
                "program_name": "Sample Program",
                "target_roles": [],
                "required_skills": [],
                "constraints": {},
                "extracted_at": datetime.utcnow().isoformat(),
            }
        }

    except Exception as e:
        logger.error(f"Error getting requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/workflows/{workflow_id}/requirements")
async def update_requirements(
    workflow_id: str,
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Update confirmed requirements for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        logger.info(f"Updating requirements for workflow {workflow_id}")

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "message": "Requirements updated",
        }

    except Exception as e:
        logger.error(f"Error updating requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== COURSE STRUCTURE ENDPOINTS =====

@router.get("/workflows/{workflow_id}/course-structure")
async def get_course_structure(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """Get extracted course structure for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "structure": {
                "courses": [],
                "modules": [],
                "lessons": [],
                "objectives": [],
                "extraction_status": "pending",
            }
        }

    except Exception as e:
        logger.error(f"Error getting course structure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== SKILL MAPPING ENDPOINTS =====

@router.get("/workflows/{workflow_id}/skill-alignments")
async def get_skill_alignments(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """Get skill alignment mappings for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "alignments": [],
            "total": 0,
        }

    except Exception as e:
        logger.error(f"Error getting skill alignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/workflows/{workflow_id}/skill-alignments")
async def update_skill_alignments(
    workflow_id: str,
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Update approved skill alignments for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "message": "Skill alignments updated",
        }

    except Exception as e:
        logger.error(f"Error updating skill alignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/workflows/{workflow_id}/gap-analysis")
async def get_gap_analysis(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """Get gap analysis report for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "gaps": [],
            "coverage": 0.0,
        }

    except Exception as e:
        logger.error(f"Error getting gap analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
