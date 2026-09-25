"""
Assessment Agent - Creates and manages assessments and items.

Responsible for:
- Generating assessments
- Creating assessment items (questions)
- Validating assessments
- Managing assessment blueprints
"""

from agents.base_agent import BaseAgent, AgentInput
from services.lesson_service import AssessmentService
from auth.tenant_context import TenantContext
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AssessmentAgent(BaseAgent):
    """Assessment generation and management agent."""

    @property
    def name(self) -> str:
        return "assessment"

    @property
    def description(self) -> str:
        return "Creates and manages assessments and assessment items"

    @property
    def tools(self) -> List[str]:
        return [
            "create_assessment",
            "add_item",
            "update_blueprint",
            "validate_assessment",
            "publish_assessment"
        ]

    async def _execute(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute assessment operations.

        Tasks:
        - create_assessment: Create new assessment
        - add_item: Add item (question) to assessment
        - update_blueprint: Update assessment blueprint
        - validate_assessment: Validate assessment completeness
        - publish_assessment: Publish assessment
        """
        logger.info(f"Assessment agent executing: {agent_input.task}")

        # Set tenant context
        TenantContext.set_tenant(agent_input.tenant_id)

        try:
            task = agent_input.task
            params = agent_input.parameters

            if task == "create_assessment":
                return await self._create_assessment(params)
            elif task == "add_item":
                return await self._add_item(params)
            elif task == "update_blueprint":
                return await self._update_blueprint(params)
            elif task == "validate_assessment":
                return await self._validate_assessment(params)
            elif task == "publish_assessment":
                return await self._publish_assessment(params)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown task: {task}",
                    "confidence": 0.0
                }

        except Exception as e:
            logger.error(f"Assessment agent error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
        finally:
            TenantContext.clear_tenant()

    async def _create_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new assessment."""
        title = params.get("title")
        assessment_type = params.get("assessment_type")

        if not title or not assessment_type:
            return {
                "status": "error",
                "error": "title and assessment_type required",
                "confidence": 0.0
            }

        try:
            service = AssessmentService()
            assessment = service.create_assessment(
                self.db,
                title,
                assessment_type,
                description=params.get("description"),
                blueprint=params.get("blueprint", {})
            )

            return {
                "status": "success",
                "assessment_id": assessment.id,
                "title": assessment.title,
                "type": assessment.assessment_type,
                "status": assessment.status,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _add_item(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add an item to an assessment."""
        assessment_id = params.get("assessment_id")
        item_type = params.get("type")
        question = params.get("question")

        if not assessment_id or not item_type or not question:
            return {
                "status": "error",
                "error": "assessment_id, type, and question required",
                "confidence": 0.0
            }

        try:
            service = AssessmentService()
            item = service.add_item_to_assessment(
                self.db,
                assessment_id,
                item_type,
                question,
                answer_key=params.get("answer_key"),
                cognitive_level=params.get("cognitive_level"),
                distractors=params.get("distractors"),
                rationale=params.get("rationale"),
                sequence=params.get("sequence")
            )

            return {
                "status": "success",
                "item_id": item.id,
                "type": item.type,
                "sequence": item.sequence,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _update_blueprint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update assessment blueprint."""
        assessment_id = params.get("assessment_id")
        blueprint = params.get("blueprint")

        if not assessment_id or not blueprint:
            return {
                "status": "error",
                "error": "assessment_id and blueprint required",
                "confidence": 0.0
            }

        try:
            service = AssessmentService()
            assessment = service.update_blueprint(
                self.db,
                assessment_id,
                blueprint
            )

            return {
                "status": "success",
                "assessment_id": assessment.id,
                "blueprint_updated": True,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _validate_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an assessment."""
        assessment_id = params.get("assessment_id")

        if not assessment_id:
            return {"status": "error", "error": "assessment_id required", "confidence": 0.0}

        try:
            service = AssessmentService()
            validation = service.validate_assessment(self.db, assessment_id)

            return {
                "status": "success",
                "assessment_id": assessment_id,
                "is_valid": validation["is_valid"],
                "item_count": validation["item_count"],
                "issues": validation["issues"],
                "warnings": validation["warnings"],
                "cognitive_level_coverage": validation["cognitive_level_coverage"],
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _publish_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Publish an assessment."""
        assessment_id = params.get("assessment_id")

        if not assessment_id:
            return {"status": "error", "error": "assessment_id required", "confidence": 0.0}

        try:
            service = AssessmentService()
            assessment = service.publish_assessment(self.db, assessment_id)

            return {
                "status": "success",
                "assessment_id": assessment.id,
                "assessment_status": assessment.status,
                "published_at": assessment.updated_at.isoformat() if assessment.updated_at else None,
                "item_count": len(assessment.items),
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}
