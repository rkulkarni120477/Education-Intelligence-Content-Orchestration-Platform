"""
Base agent class and interfaces for LangChain/LangGraph integration.

All agents inherit from BaseAgent and implement the standard interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid
import logging
import time

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_INPUT = "waiting_input"
    REQUIRES_REVIEW = "requires_review"


class AgentInput(BaseModel):
    """Standard input format for all agents."""
    task: str
    context: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    source_data: Optional[Dict[str, Any]] = None
    tenant_id: str
    user_id: str
    workflow_id: Optional[str] = None
    checkpoint_id: Optional[str] = None


class AgentOutput(BaseModel):
    """Standard output format for all agents."""
    agent_name: str
    status: AgentStatus
    result: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    execution_time_ms: float
    tokens_used: Optional[Dict[str, int]] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    requires_review: bool = False
    review_reason: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all agents.

    Each agent must implement:
    - name: Unique agent identifier
    - description: What this agent does
    - _execute: Main execution logic
    """

    def __init__(self, db=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize agent.

        Args:
            db: SQLAlchemy session for database access
            config: Agent-specific configuration
        """
        self.db = db
        self.config = config or {}
        self.agent_id = str(uuid.uuid4())
        self.execution_log: List[Dict[str, Any]] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """What this agent does."""
        pass

    @property
    def tools(self) -> List[str]:
        """List of tool names this agent can use."""
        return []

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """
        Process input and return output.

        This is the main execution method. Subclasses implement logic here.
        """
        start_time = time.time()

        try:
            # Validate input
            self._validate_input(agent_input)

            # Execute agent logic
            result = await self._execute(agent_input)

            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000

            # Create output
            output = AgentOutput(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                execution_time_ms=execution_time,
                confidence=self._calculate_confidence(result)
            )

            self._log_execution(agent_input, output)
            return output

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Agent {self.name} failed: {str(e)}", exc_info=True)

            output = AgentOutput(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                errors=[str(e)],
                execution_time_ms=execution_time
            )

            self._log_execution(agent_input, output)
            return output

    @abstractmethod
    async def _execute(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute agent logic. Subclasses override this.

        Args:
            agent_input: Structured input

        Returns:
            Result dictionary
        """
        pass

    def _validate_input(self, agent_input: AgentInput) -> None:
        """Validate input has required fields."""
        if not agent_input.tenant_id:
            raise ValueError("tenant_id is required")
        if not agent_input.user_id:
            raise ValueError("user_id is required")
        if not agent_input.task:
            raise ValueError("task is required")

    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate confidence score for result.
        Subclasses can override for custom logic.
        """
        if "confidence" in result:
            return result["confidence"]
        return 0.5

    def _log_execution(self, input_: AgentInput, output: AgentOutput) -> None:
        """Log agent execution for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "task": input_.task,
            "status": output.status.value,
            "execution_time_ms": output.execution_time_ms,
            "confidence": output.confidence,
            "errors": output.errors,
            "warnings": output.warnings
        }
        self.execution_log.append(log_entry)
        logger.info(f"Agent execution: {self.name} - {output.status.value}")

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get execution history for this agent."""
        return self.execution_log.copy()

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM. Subclasses can override."""
        return f"""You are a {self.name} agent in the Academian Education Intelligence Platform.

Your responsibilities:
- Process structured inputs efficiently
- Provide accurate and actionable outputs
- Flag issues requiring human review
- Maintain audit trail of all actions
- Follow tenant policies and guidelines

Always return structured, actionable outputs."""


class AgentFactory:
    """Factory for creating and managing agents."""

    _agents: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, agent_class: type) -> None:
        """Register an agent class."""
        cls._agents[name] = agent_class
        logger.info(f"Registered agent: {name}")

    @classmethod
    def create(cls, name: str, db=None, config: Optional[Dict[str, Any]] = None) -> BaseAgent:
        """Create an agent instance by name."""
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' not registered. Available: {list(cls._agents.keys())}")

        agent_class = cls._agents[name]
        return agent_class(db=db, config=config)

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agents."""
        return list(cls._agents.keys())

    @classmethod
    def get_agent_info(cls, name: str) -> Dict[str, Any]:
        """Get information about an agent."""
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' not registered")

        agent_class = cls._agents[name]
        # Create temporary instance to get metadata
        temp = agent_class()
        return {
            "name": temp.name,
            "description": temp.description,
            "tools": temp.tools
        }
