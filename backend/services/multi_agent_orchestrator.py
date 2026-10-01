"""Dispatch and execute registered multi-agent workflow graphs."""

from dataclasses import dataclass
import logging
from typing import Any, Callable, Dict, List, Optional

from workflows.workforce_alignment_graph import create_workforce_alignment_graph
from workflows.workforce_alignment_state import WorkforceAlignmentState
from services.workflow_agent_registry import AGENT_REGISTRY, WORKFORCE_ALIGNMENT_AGENT_IDS


GraphBuilder = Callable[[], Any]
AgentEventCallback = Callable[[str, str, Dict[str, Any]], None]
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorkflowPlan:
    id: str
    name: str
    description: str
    agent_ids: tuple[str, ...]
    graph_builder: GraphBuilder


WORKFLOW_REGISTRY: Dict[str, WorkflowPlan] = {
    "workforce_alignment": WorkflowPlan(
        id="workforce_alignment",
        name="Workforce Alignment",
        description="Requirements, ingestion, skill mapping, recommendations, governance, and export validation.",
        agent_ids=WORKFORCE_ALIGNMENT_AGENT_IDS,
        graph_builder=create_workforce_alignment_graph,
    ),
}


class UnsupportedWorkflowError(ValueError):
    """Raised when a workflow type has no registered orchestration graph."""


class MultiAgentOrchestrator:
    """Run registered specialist agents through their workflow graph."""

    @staticmethod
    def _record_agent_events(
        snapshot: Dict[str, Any],
        on_agent_event: AgentEventCallback,
        completed_counts: Dict[str, int],
        failed_nodes: set,
    ) -> None:
        node_id = snapshot.get("current_node")
        if node_id not in AGENT_REGISTRY:
            return

        completed = snapshot.get("completed_nodes", [])
        completion_count = completed.count(node_id)
        prior_count = completed_counts.get(node_id, 0)
        if snapshot.get("workflow_status") == "failed" and node_id not in failed_nodes:
            failed_nodes.add(node_id)
            try:
                on_agent_event(node_id, "failed", snapshot)
            except Exception:
                logger.exception("Failed to record failed agent run for %s", node_id)
            completed_counts[node_id] = max(prior_count, completion_count)
            return

        for _ in range(max(0, completion_count - prior_count)):
            try:
                on_agent_event(node_id, "completed", snapshot)
            except Exception:
                logger.exception("Failed to record completed agent run for %s", node_id)
        completed_counts[node_id] = max(prior_count, completion_count)

    @staticmethod
    def _get_plan_and_graph(workflow_type: str):
        plan = WORKFLOW_REGISTRY.get(workflow_type)
        if plan is None:
            raise UnsupportedWorkflowError(f"Workflow type '{workflow_type}' is not registered")
        graph = plan.graph_builder()
        missing_agents = [agent_id for agent_id in plan.agent_ids if agent_id not in graph.nodes]
        if missing_agents:
            raise RuntimeError(f"Workflow '{workflow_type}' references unregistered agents: {missing_agents}")
        return graph

    @staticmethod
    def list_workflows() -> List[Dict[str, Any]]:
        return [
            {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "agent_ids": list(plan.agent_ids),
            }
            for plan in WORKFLOW_REGISTRY.values()
        ]

    @staticmethod
    def execute(
        workflow_type: str,
        state: WorkforceAlignmentState,
        on_agent_event: Optional[AgentEventCallback] = None,
    ) -> Dict[str, Any]:
        graph = MultiAgentOrchestrator._get_plan_and_graph(workflow_type)

        if on_agent_event is None:
            return graph.invoke(state)

        latest_state: Dict[str, Any] = {}
        completed_counts: Dict[str, int] = {}
        failed_nodes = set()
        for snapshot in graph.stream(state, stream_mode="values"):
            latest_state = snapshot
            MultiAgentOrchestrator._record_agent_events(
                snapshot, on_agent_event, completed_counts, failed_nodes
            )

        return latest_state

    @staticmethod
    async def execute_async(
        workflow_type: str,
        state: WorkforceAlignmentState,
        on_agent_event: Optional[AgentEventCallback] = None,
    ) -> Dict[str, Any]:
        """Asynchronously execute a registered workflow and report agent events."""
        graph = MultiAgentOrchestrator._get_plan_and_graph(workflow_type)
        if on_agent_event is None:
            return await graph.ainvoke(state)

        latest_state: Dict[str, Any] = {}
        completed_counts: Dict[str, int] = {}
        failed_nodes = set()
        async for snapshot in graph.astream(state, stream_mode="values"):
            latest_state = snapshot
            MultiAgentOrchestrator._record_agent_events(
                snapshot, on_agent_event, completed_counts, failed_nodes
            )
        return latest_state