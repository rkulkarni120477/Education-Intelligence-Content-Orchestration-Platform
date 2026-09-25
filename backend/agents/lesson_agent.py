"""
Lesson Agent - Creates and manages lessons and activities.

Responsible for:
- Generating lesson plans
- Creating lesson activities
- Managing lesson content
- Publishing lessons
"""

from agents.base_agent import BaseAgent, AgentInput
from services.lesson_service import LessonService
from auth.tenant_context import TenantContext
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class LessonAgent(BaseAgent):
    """Lesson generation and management agent."""

    @property
    def name(self) -> str:
        return "lesson"

    @property
    def description(self) -> str:
        return "Creates and manages lessons and activities"

    @property
    def tools(self) -> List[str]:
        return [
            "create_lesson",
            "add_activity",
            "update_content",
            "publish_lesson",
            "get_lesson"
        ]

    async def _execute(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute lesson operations.

        Tasks:
        - create_lesson: Create new lesson
        - add_activity: Add activity to lesson
        - update_content: Update lesson content
        - publish_lesson: Publish lesson
        - get_lesson: Retrieve lesson details
        """
        logger.info(f"Lesson agent executing: {agent_input.task}")

        # Set tenant context
        TenantContext.set_tenant(agent_input.tenant_id)

        try:
            task = agent_input.task
            params = agent_input.parameters

            if task == "create_lesson":
                return await self._create_lesson(params)
            elif task == "add_activity":
                return await self._add_activity(params)
            elif task == "update_content":
                return await self._update_content(params)
            elif task == "publish_lesson":
                return await self._publish_lesson(params)
            elif task == "get_lesson":
                return await self._get_lesson(params)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown task: {task}",
                    "confidence": 0.0
                }

        except Exception as e:
            logger.error(f"Lesson agent error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
        finally:
            TenantContext.clear_tenant()

    async def _create_lesson(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lesson."""
        curriculum_id = params.get("curriculum_id")
        title = params.get("title")

        if not curriculum_id or not title:
            return {
                "status": "error",
                "error": "curriculum_id and title required",
                "confidence": 0.0
            }

        try:
            service = LessonService()
            lesson = service.create_lesson(
                self.db,
                curriculum_id,
                title,
                grade=params.get("grade"),
                subject=params.get("subject"),
                duration_minutes=params.get("duration_minutes"),
                description=params.get("description"),
                content=params.get("content", {})
            )

            return {
                "status": "success",
                "lesson_id": lesson.id,
                "title": lesson.title,
                "status": lesson.status,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _add_activity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add an activity to a lesson."""
        lesson_id = params.get("lesson_id")
        activity_type = params.get("type")
        title = params.get("title")

        if not lesson_id or not activity_type or not title:
            return {
                "status": "error",
                "error": "lesson_id, type, and title required",
                "confidence": 0.0
            }

        try:
            service = LessonService()
            activity = service.add_activity_to_lesson(
                self.db,
                lesson_id,
                activity_type,
                title,
                instructions=params.get("instructions"),
                duration_minutes=params.get("duration_minutes"),
                differentiation=params.get("differentiation", {})
            )

            return {
                "status": "success",
                "activity_id": activity.id,
                "type": activity.type,
                "title": activity.title,
                "status": activity.status,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _update_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update lesson content."""
        lesson_id = params.get("lesson_id")
        content = params.get("content")

        if not lesson_id or not content:
            return {
                "status": "error",
                "error": "lesson_id and content required",
                "confidence": 0.0
            }

        try:
            service = LessonService()
            lesson = service.update_lesson_content(
                self.db,
                lesson_id,
                content
            )

            return {
                "status": "success",
                "lesson_id": lesson.id,
                "title": lesson.title,
                "content_updated": True,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _publish_lesson(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a lesson."""
        lesson_id = params.get("lesson_id")

        if not lesson_id:
            return {"status": "error", "error": "lesson_id required", "confidence": 0.0}

        try:
            service = LessonService()
            lesson = service.publish_lesson(self.db, lesson_id)

            return {
                "status": "success",
                "lesson_id": lesson.id,
                "lesson_status": lesson.status,
                "published_at": lesson.updated_at.isoformat() if lesson.updated_at else None,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _get_lesson(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get lesson details."""
        lesson_id = params.get("lesson_id")

        if not lesson_id:
            return {"status": "error", "error": "lesson_id required", "confidence": 0.0}

        try:
            service = LessonService()
            lesson = service.get_lesson(self.db, lesson_id)

            return {
                "status": "success",
                "lesson": {
                    "id": lesson.id,
                    "title": lesson.title,
                    "grade": lesson.grade,
                    "subject": lesson.subject,
                    "duration_minutes": lesson.duration_minutes,
                    "status": lesson.status,
                    "activity_count": len(lesson.activities)
                },
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}
