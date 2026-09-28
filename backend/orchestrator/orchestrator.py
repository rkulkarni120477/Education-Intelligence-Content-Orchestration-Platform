from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import logging
from sqlalchemy.orm import Session
from database.models import WorkflowExecution, AgentRun
from agents.base_agent import AgentFactory, AgentInput, AgentOutput
from datetime import datetime
import uuid
from services.agent_execution_service import (
    start_agent_execution,
    update_agent_progress,
    complete_agent_execution,
)

logger = logging.getLogger(__name__)


class WorkflowState(BaseModel):
    """State management for workflow execution"""
    execution_id: str
    workflow_id: str
    tenant_id: str
    status: str = "pending"
    current_agent: Optional[str] = None
    context: Dict[str, Any] = {}
    results: Dict[str, AgentOutput] = {}
    errors: List[str] = []
    agent_runs: List[str] = []
    started_at: datetime = None
    completed_at: Optional[datetime] = None


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows using LangGraph"""

    def __init__(self, db: Session):
        self.db = db
        self.graph = None

    def build_workflow(self, workflow_definition: Dict[str, Any]) -> StateGraph:
        """Build workflow graph from definition"""
        graph = StateGraph(WorkflowState)

        # Add nodes for each agent in workflow
        agents = workflow_definition.get("agents", [])
        for agent_config in agents:
            agent_name = agent_config.get("name")
            agent_type = agent_config.get("type")

            # Create node for agent
            async def agent_node(state: WorkflowState, agent_name=agent_name, agent_type=agent_type):
                return await self._execute_agent_node(state, agent_name, agent_type)

            graph.add_node(agent_name, agent_node)

        # Add edges based on workflow definition
        edges = workflow_definition.get("edges", [])
        for edge in edges:
            source = edge.get("from")
            target = edge.get("to")
            condition = edge.get("condition")

            if condition:
                graph.add_conditional_edges(source, lambda s: condition, {True: target, False: END})
            else:
                graph.add_edge(source, target)

        # Set entry point
        entry_point = workflow_definition.get("entry_point", agents[0]["name"] if agents else None)
        if entry_point:
            graph.set_entry_point(entry_point)

        # Set finish point
        graph.set_finish_point(END)

        self.graph = graph.compile()
        return self.graph

    async def execute_workflow(self, execution_id: str, workflow_id: str, workflow_definition: Dict, input_data: Dict, tenant_id: str) -> WorkflowState:
        """Execute a complete workflow"""
        state = WorkflowState(
            execution_id=execution_id,
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            context=input_data,
            started_at=datetime.utcnow()
        )

        # Build workflow if not already built
        if not self.graph:
            self.build_workflow(workflow_definition)

        try:
            # Execute workflow
            result = await self.graph.ainvoke(state)
            result.status = "completed"
            result.completed_at = datetime.utcnow()

            # Save to database
            self._save_execution(result)

            return result
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            state.status = "failed"
            state.errors.append(str(e))
            state.completed_at = datetime.utcnow()

            self._save_execution(state)
            return state

    async def _execute_agent_node(self, state: WorkflowState, agent_name: str, agent_type: str) -> Dict:
        """Execute a single agent node"""
        agent_run_id = str(uuid.uuid4())
        started_at = datetime.utcnow()

        try:
            state.current_agent = agent_name

            # Track agent execution for UI
            start_agent_execution(agent_name, state.execution_id)
            update_agent_progress(10)

            # Create agent
            agent = AgentFactory.create(agent_type, self.db)

            # Prepare input
            agent_input = AgentInput(
                data=state.context,
                context=state.context,
                user_id=state.context.get("user_id")
            )

            # Execute agent
            update_agent_progress(30)
            output = await agent.process(agent_input)
            update_agent_progress(80)

            # Store result
            state.results[agent_name] = output

            # Update context with output
            state.context.update(output.data)

            # Create AgentRun record
            agent_status = "completed" if output.status == "success" else output.status
            self._create_agent_run(
                agent_run_id=agent_run_id,
                tenant_id=state.tenant_id,
                execution_id=state.execution_id,
                agent_name=agent_name,
                agent_type=agent_type,
                status=agent_status,
                input_data=agent_input.dict(),
                output_data=output.dict(),
                started_at=started_at,
                completed_at=datetime.utcnow()
            )
            state.agent_runs.append(agent_run_id)

            # Complete agent execution tracking
            update_agent_progress(100)
            complete_agent_execution()

            # Check for failures
            if output.status == "failed":
                state.errors.extend(output.errors or [])
                state.status = "failed"
            elif output.status == "requires_review":
                state.context["requires_review"] = True
                state.context["review_reason"] = output.review_reason

            return state.dict()
        except Exception as e:
            logger.error(f"Agent {agent_name} execution failed: {e}")
            state.errors.append(f"Agent {agent_name} failed: {str(e)}")

            # Create AgentRun record for failure
            self._create_agent_run(
                agent_run_id=agent_run_id,
                tenant_id=state.tenant_id,
                execution_id=state.execution_id,
                agent_name=agent_name,
                agent_type=agent_type,
                status="failed",
                input_data={},
                output_data={},
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow()
            )
            state.agent_runs.append(agent_run_id)
            state.status = "failed"

            # Stop agent execution tracking
            complete_agent_execution()

            return state.dict()

    def _create_agent_run(
        self,
        agent_run_id: str,
        tenant_id: str,
        execution_id: str,
        agent_name: str,
        agent_type: str,
        status: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        started_at: datetime,
        completed_at: datetime,
        error_message: Optional[str] = None
    ):
        """Create an AgentRun record for tracking agent execution"""
        try:
            agent_run = AgentRun(
                id=agent_run_id,
                tenant_id=tenant_id,
                execution_id=execution_id,
                agent_name=agent_name,
                agent_type=agent_type,
                status=status,
                input_data=input_data,
                output_data=output_data,
                error_message=error_message,
                started_at=started_at,
                completed_at=completed_at
            )
            self.db.add(agent_run)
            self.db.commit()
            logger.info(f"✓ Created AgentRun {agent_run_id} for agent {agent_name}")
        except Exception as e:
            logger.error(f"Error creating AgentRun: {str(e)}")
            self.db.rollback()

    def _save_execution(self, state: WorkflowState):
        """Save workflow execution to database"""
        execution = WorkflowExecution(
            id=state.execution_id,
            workflow_id=state.workflow_id,
            tenant_id=state.tenant_id,
            status=state.status,
            input_data=state.context,
            output_data={
                "results": {k: v.dict() for k, v in state.results.items()},
                "errors": state.errors
            },
            started_at=state.started_at,
            completed_at=state.completed_at
        )

        self.db.add(execution)
        self.db.commit()

    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self.db.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id
        ).first()


class WorkflowBuilder:
    """Builder for creating workflow definitions"""

    def __init__(self):
        self.agents = []
        self.edges = []
        self.entry_point = None

    def add_agent(self, name: str, agent_type: str, config: Optional[Dict] = None) -> "WorkflowBuilder":
        """Add an agent to the workflow"""
        self.agents.append({
            "name": name,
            "type": agent_type,
            "config": config or {}
        })

        if not self.entry_point:
            self.entry_point = name

        return self

    def add_edge(self, from_agent: str, to_agent: str, condition: Optional[str] = None) -> "WorkflowBuilder":
        """Add an edge between agents"""
        self.edges.append({
            "from": from_agent,
            "to": to_agent,
            "condition": condition
        })
        return self

    def build(self) -> Dict[str, Any]:
        """Build the workflow definition"""
        return {
            "agents": self.agents,
            "edges": self.edges,
            "entry_point": self.entry_point
        }
