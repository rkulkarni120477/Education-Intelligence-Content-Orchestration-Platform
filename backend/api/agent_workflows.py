"""API for managing agent-workflow assignments and execution."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from database.db import get_db
from database.models import Workflow
from auth.tenant_context import get_current_tenant_id
from services.agent_workflow_executor import AgentWorkflowExecutor
from services.multi_agent_orchestrator import MultiAgentOrchestrator
from services.workflow_agent_registry import AGENT_REGISTRY
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/agent-workflows", tags=["agent-workflows"])


# ===== REQUEST/RESPONSE MODELS =====


class AssignWorkflowRequest(BaseModel):
    """Request to assign a workflow to an agent."""

    agent_id: str = Field(..., description="Agent ID")
    workflow_id: str = Field(..., description="Workflow ID")
    auto_execute: bool = Field(
        False, description="Auto-execute when conditions met"
    )


class ExecuteWorkflowRequest(BaseModel):
    """Request for agent to execute a workflow."""

    agent_id: str = Field(..., description="Agent executing workflow")
    workflow_id: str = Field(..., description="Workflow to execute")
    input_data: Dict[str, Any] = Field(
        default_factory=dict, description="Workflow input parameters"
    )


class WorkflowAssignmentResponse(BaseModel):
    """Response for workflow assignment."""

    status: str
    message: str
    workflow_id: str
    agent_id: str


class AgentWorkflowResponse(BaseModel):
    """Information about a workflow assigned to an agent."""

    workflow_id: str
    workflow_name: str
    description: str
    agent_id: str
    is_automatable: bool
    execution_trigger: str


class ExecuteWorkflowResponse(BaseModel):
    """Response from workflow execution."""

    status: str
    execution_id: str
    workflow_id: str
    workflow_name: str
    agent_id: str
    result: Dict[str, Any] = None
    error: str = None


# ===== API ENDPOINTS =====


@router.get("/catalog", response_model=Dict[str, Any])
async def get_workflow_catalog():
    """List workflow plans and the executable agents in each plan."""
    return {"workflows": MultiAgentOrchestrator.list_workflows()}


@router.post("/assign", response_model=WorkflowAssignmentResponse)
async def assign_workflow_to_agent(
    request: AssignWorkflowRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Assign a workflow to an agent for execution."""
    try:
        if request.agent_id not in AGENT_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} is not registered")

        workflow = (
            db.query(Workflow)
            .filter(
                Workflow.id == request.workflow_id,
                Workflow.tenant_id == tenant_id,
            )
            .first()
        )

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {request.workflow_id} not found",
            )

        # Update workflow with assigned agents
        if workflow.assigned_agents is None:
            workflow.assigned_agents = []

        if request.agent_id not in workflow.assigned_agents:
            workflow.assigned_agents.append(request.agent_id)
            workflow.is_automatable = workflow.is_automatable or request.auto_execute
            db.commit()
            logger.info(
                f"✓ Assigned agent {request.agent_id} to workflow {request.workflow_id}"
            )
        else:
            logger.info(
                f"Agent {request.agent_id} already assigned to workflow {request.workflow_id}"
            )

        return WorkflowAssignmentResponse(
            status="success",
            message=f"Agent {request.agent_id} assigned to workflow",
            workflow_id=request.workflow_id,
            agent_id=request.agent_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/unassign", response_model=WorkflowAssignmentResponse)
async def unassign_workflow_from_agent(
    request: AssignWorkflowRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Unassign a workflow from an agent."""
    try:
        workflow = (
            db.query(Workflow)
            .filter(
                Workflow.id == request.workflow_id,
                Workflow.tenant_id == tenant_id,
            )
            .first()
        )

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {request.workflow_id} not found",
            )

        if workflow.assigned_agents and request.agent_id in workflow.assigned_agents:
            workflow.assigned_agents.remove(request.agent_id)
            db.commit()
            logger.info(
                f"✓ Unassigned agent {request.agent_id} from workflow {request.workflow_id}"
            )

        return WorkflowAssignmentResponse(
            status="success",
            message=f"Agent {request.agent_id} unassigned from workflow",
            workflow_id=request.workflow_id,
            agent_id=request.agent_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unassigning workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/{agent_id}/workflows", response_model=List[AgentWorkflowResponse])
async def get_agent_workflows(
    agent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get all workflows assigned to an agent."""
    try:
        workflows = AgentWorkflowExecutor.get_agent_workflows(
            agent_id=agent_id, tenant_id=tenant_id, db=db
        )

        return [AgentWorkflowResponse(**w) for w in workflows]

    except Exception as e:
        logger.error(f"Error getting agent workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/execute", response_model=ExecuteWorkflowResponse)
async def execute_workflow_as_agent(
    request: ExecuteWorkflowRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Execute a workflow as a specific agent."""
    try:
        if request.agent_id not in AGENT_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} is not registered")

        logger.info(
            f"🚀 Executing workflow {request.workflow_id} as agent {request.agent_id}"
        )

        result = await AgentWorkflowExecutor.execute_workflow_for_agent(
            agent_id=request.agent_id,
            workflow_id=request.workflow_id,
            tenant_id=tenant_id,
            workflow_input=request.input_data,
            db=db,
        )

        if result["status"] == "success":
            logger.info(
                f"✓ Workflow executed successfully: {result['execution_id']}"
            )
            return ExecuteWorkflowResponse(
                status=result["status"],
                execution_id=result["execution_id"],
                workflow_id=result["workflow_id"],
                workflow_name=result["workflow_name"],
                agent_id=result["agent_id"],
                result=result.get("result"),
            )
        else:
            logger.error(f"❌ Workflow execution failed: {result.get('error')}")
            return ExecuteWorkflowResponse(
                status=result["status"],
                execution_id=result["execution_id"],
                workflow_id=request.workflow_id,
                workflow_name="",
                agent_id=request.agent_id,
                error=result.get("error"),
            )

    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/{workflow_id}/agents", response_model=Dict[str, Any])
async def get_workflow_agents(
    workflow_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get all agents assigned to a workflow."""
    try:
        workflow = (
            db.query(Workflow)
            .filter(
                Workflow.id == workflow_id,
                Workflow.tenant_id == tenant_id,
            )
            .first()
        )

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found",
            )

        assigned_agents = workflow.assigned_agents or []

        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "assigned_agents": assigned_agents,
            "agent_count": len(assigned_agents),
            "is_automatable": workflow.is_automatable,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
