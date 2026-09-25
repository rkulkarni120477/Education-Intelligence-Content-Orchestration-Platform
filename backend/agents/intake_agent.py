"""
Intake Agent - Parses requirements and initializes workflow context.

Responsible for:
- Understanding user requirements
- Extracting key parameters
- Setting up workflow context
- Validating inputs
"""

from agents.base_agent import BaseAgent, AgentInput, AgentStatus
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class IntakeAgent(BaseAgent):
    """Intake agent for requirement understanding and context setup."""

    @property
    def name(self) -> str:
        return "intake"

    @property
    def description(self) -> str:
        return "Parses user requirements and initializes workflow context"

    @property
    def tools(self) -> list[str]:
        return ["extract_requirements", "validate_inputs", "setup_context"]

    async def _execute(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute intake process.

        Extracts:
        - Content type and source
        - Target standards and curriculum
        - Grade and subject
        - Output requirements
        """
        logger.info(f"Intake agent processing: {agent_input.task}")

        # Extract requirements from context
        requirements = agent_input.context.get("requirements", {})

        # Parse key parameters
        extracted = {
            "content_type": requirements.get("content_type"),
            "grade": requirements.get("grade"),
            "subject": requirements.get("subject"),
            "standards_framework": requirements.get("standards_framework"),
            "curriculum": requirements.get("curriculum"),
            "output_format": requirements.get("output_format", "structured"),
            "quality_threshold": requirements.get("quality_threshold", 0.7),
            "include_evidence": requirements.get("include_evidence", True)
        }

        # Validate required fields
        validation_errors = []
        if not extracted["grade"]:
            validation_errors.append("Grade level is required")
        if not extracted["subject"]:
            validation_errors.append("Subject is required")
        if not extracted["standards_framework"]:
            validation_errors.append("Standards framework is required")

        if validation_errors:
            return {
                "status": "validation_failed",
                "errors": validation_errors,
                "confidence": 0.0
            }

        # Setup workflow context
        workflow_context = {
            "grade": extracted["grade"],
            "subject": extracted["subject"],
            "standards_framework": extracted["standards_framework"],
            "curriculum": extracted["curriculum"],
            "quality_threshold": extracted["quality_threshold"],
            "requirements_validated": True,
            "next_step": "retrieve_standards"
        }

        return {
            "status": "success",
            "requirements": extracted,
            "workflow_context": workflow_context,
            "confidence": 0.95,
            "warnings": []
        }
