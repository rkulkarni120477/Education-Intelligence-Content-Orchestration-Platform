"""Service for agents to execute workflows."""

from database.db import SessionLocal
from database.models import Workflow, WorkflowExecution, AgentRun, Tenant
from workflows.workforce_alignment_graph import create_workforce_alignment_graph
from workflows.workforce_alignment_state import WorkforceAlignmentState
from auth.tenant_context import TenantContext
import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AgentWorkflowExecutor:
    """Executes workflows on behalf of agents."""

    @staticmethod
    async def execute_workflow_for_agent(
        agent_id: str,
        workflow_id: str,
        tenant_id: str,
        workflow_input: dict,
        db: Session = None,
    ) -> dict:
        """
        Execute a workflow assigned to an agent.

        Args:
            agent_id: The agent executing the workflow
            workflow_id: The workflow to execute
            tenant_id: Tenant context
            workflow_input: Input data for workflow
            db: Database session

        Returns:
            Execution result with status and output
        """
        execution_id = str(uuid.uuid4())
        agent_run = None

        if not db:
            db = SessionLocal()

        try:
            # Set tenant context
            TenantContext.set_tenant(tenant_id)

            # Verify workflow exists and is active
            workflow = (
                db.query(Workflow)
                .filter(Workflow.id == workflow_id, Workflow.tenant_id == tenant_id)
                .first()
            )

            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")

            if workflow.status != "active":
                raise ValueError(
                    f"Workflow {workflow_id} is not active (status: {workflow.status})"
                )

            # Check if agent is assigned to this workflow
            assigned_agents = workflow.assigned_agents or []
            if agent_id not in assigned_agents:
                raise PermissionError(
                    f"Agent {agent_id} is not assigned to workflow {workflow_id}"
                )

            logger.info(
                f"🚀 Agent {agent_id} executing workflow {workflow_id} ({workflow.name})"
            )

            # Record workflow execution
            workflow_execution = WorkflowExecution(
                id=execution_id,
                tenant_id=tenant_id,
                workflow_id=workflow_id,
                status="running",
                input_data=workflow_input,
                started_at=datetime.utcnow(),
            )
            db.add(workflow_execution)
            db.commit()

            # Record agent run
            agent_run = AgentRun(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                workflow_execution_id=execution_id,
                agent_name=agent_id,
                status="running",
                started_at=datetime.utcnow(),
                input_data=workflow_input,
            )
            db.add(agent_run)
            db.commit()

            # Initialize workflow state from input
            state = WorkforceAlignmentState(
                tenant_id=tenant_id,
                request_id=execution_id,
                initiating_user_id=agent_id,  # Agent is initiator
                workflow_execution_id=execution_id,
                program_id=workflow_input.get("program_id", ""),
                program_name=workflow_input.get("program_name", ""),
                course_ids=workflow_input.get("course_ids", []),
                input_package_id=workflow_input.get("input_package_id", ""),
                input_package_format=workflow_input.get("input_package_format", "zip"),
                input_skill_framework_id=workflow_input.get("input_skill_framework_id", ""),
                input_style_guide_id=workflow_input.get("input_style_guide_id"),
                started_at=datetime.utcnow(),
            )

            # Execute the workflow graph
            logger.info(f"⚙️  Invoking workflow graph for execution {execution_id}")
            workflow_graph = create_workforce_alignment_graph()
            result = workflow_graph.invoke(state)

            # Extract result status
            workflow_status = (
                result.get("workflow_status", "completed")
                if isinstance(result, dict)
                else "completed"
            )

            # Save execution result
            workflow_execution.status = workflow_status
            workflow_execution.output_data = (
                result.dict() if hasattr(result, "dict") else result
            )
            workflow_execution.completed_at = datetime.utcnow()

            # Update agent run
            agent_run.status = "completed"
            agent_run.output_data = (
                result.dict() if hasattr(result, "dict") else result
            )
            agent_run.completed_at = datetime.utcnow()

            db.commit()

            logger.info(
                f"✓ Agent {agent_id} workflow execution completed: {execution_id}"
            )
            logger.info(f"  Final status: {workflow_status}")

            return {
                "status": "success",
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "workflow_name": workflow.name,
                "agent_id": agent_id,
                "result": result.dict() if hasattr(result, "dict") else result,
            }

        except PermissionError as e:
            logger.error(f"❌ Permission denied: {str(e)}")
            if agent_run:
                agent_run.status = "failed"
                agent_run.error_message = str(e)
                agent_run.completed_at = datetime.utcnow()
                db.commit()
            return {
                "status": "error",
                "error": str(e),
                "execution_id": execution_id,
            }
        except ValueError as e:
            logger.error(f"❌ Validation error: {str(e)}")
            if agent_run:
                agent_run.status = "failed"
                agent_run.error_message = str(e)
                agent_run.completed_at = datetime.utcnow()
                db.commit()
            return {
                "status": "error",
                "error": str(e),
                "execution_id": execution_id,
            }
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {str(e)}")
            logger.exception(f"Exception details: {e}")

            # Log failure
            if agent_run:
                agent_run.status = "failed"
                agent_run.error_message = str(e)
                agent_run.completed_at = datetime.utcnow()
                db.commit()

            return {
                "status": "error",
                "error": str(e),
                "execution_id": execution_id,
            }

    @staticmethod
    def get_agent_workflows(agent_id: str, tenant_id: str, db: Session) -> list:
        """Get all workflows assigned to an agent."""
        try:
            workflows = (
                db.query(Workflow)
                .filter(
                    Workflow.tenant_id == tenant_id,
                    Workflow.status == "active",
                )
                .all()
            )

            assigned_workflows = []
            for workflow in workflows:
                if workflow.assigned_agents and agent_id in workflow.assigned_agents:
                    assigned_workflows.append(
                        {
                            "workflow_id": workflow.id,
                            "workflow_name": workflow.name,
                            "description": workflow.description,
                            "agent_id": agent_id,
                            "is_automatable": workflow.is_automatable,
                            "execution_trigger": workflow.execution_trigger,
                        }
                    )

            logger.info(
                f"✓ Found {len(assigned_workflows)} workflows for agent {agent_id}"
            )
            return assigned_workflows

        except Exception as e:
            logger.error(f"Error getting agent workflows: {str(e)}")
            return []

    @staticmethod
    def assign_workflow_to_agent(
        agent_id: str, workflow_id: str, tenant_id: str, db: Session
    ) -> bool:
        """Assign a workflow to an agent."""
        try:
            workflow = (
                db.query(Workflow)
                .filter(Workflow.id == workflow_id, Workflow.tenant_id == tenant_id)
                .first()
            )

            if not workflow:
                logger.error(f"Workflow {workflow_id} not found")
                return False

            if workflow.assigned_agents is None:
                workflow.assigned_agents = []

            if agent_id not in workflow.assigned_agents:
                workflow.assigned_agents.append(agent_id)
                db.commit()
                logger.info(
                    f"✓ Assigned agent {agent_id} to workflow {workflow_id}"
                )
                return True

            logger.info(
                f"Agent {agent_id} already assigned to workflow {workflow_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error assigning workflow to agent: {str(e)}")
            return False

    @staticmethod
    def unassign_workflow_from_agent(
        agent_id: str, workflow_id: str, tenant_id: str, db: Session
    ) -> bool:
        """Remove a workflow assignment from an agent."""
        try:
            workflow = (
                db.query(Workflow)
                .filter(Workflow.id == workflow_id, Workflow.tenant_id == tenant_id)
                .first()
            )

            if not workflow:
                logger.error(f"Workflow {workflow_id} not found")
                return False

            if workflow.assigned_agents and agent_id in workflow.assigned_agents:
                workflow.assigned_agents.remove(agent_id)
                db.commit()
                logger.info(
                    f"✓ Unassigned agent {agent_id} from workflow {workflow_id}"
                )
                return True

            logger.info(
                f"Agent {agent_id} not assigned to workflow {workflow_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error unassigning workflow from agent: {str(e)}")
            return False
