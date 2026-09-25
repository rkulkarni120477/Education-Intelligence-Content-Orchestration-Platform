"""
Standards Agent - Retrieves and manages standards for alignment.

Responsible for:
- Retrieving standards frameworks
- Filtering standards by grade/subject
- Searching for relevant standards
- Providing standards context
"""

from agents.base_agent import BaseAgent, AgentInput
from services.standards_service import StandardsService
from auth.tenant_context import TenantContext, get_current_tenant_id
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class StandardsAgent(BaseAgent):
    """Standards intelligence and retrieval agent."""

    @property
    def name(self) -> str:
        return "standards"

    @property
    def description(self) -> str:
        return "Retrieves and manages standards for curriculum alignment"

    @property
    def tools(self) -> List[str]:
        return [
            "get_framework",
            "list_standards",
            "search_standards",
            "get_standards_by_grade_subject",
            "get_standard_hierarchy"
        ]

    async def _execute(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute standards retrieval.

        Tasks:
        - get_framework: Retrieve a standards framework
        - list_standards: List standards with filtering
        - search_standards: Search standards by text
        - get_by_grade_subject: Get standards for grade/subject
        """
        logger.info(f"Standards agent executing: {agent_input.task}")

        # Set tenant context for service layer
        TenantContext.set_tenant(agent_input.tenant_id)

        try:
            task = agent_input.task
            params = agent_input.parameters

            if task == "get_framework":
                return await self._get_framework(params)
            elif task == "list_standards":
                return await self._list_standards(params)
            elif task == "search_standards":
                return await self._search_standards(params)
            elif task == "get_by_grade_subject":
                return await self._get_by_grade_subject(params)
            elif task == "get_hierarchy":
                return await self._get_hierarchy(params)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown task: {task}",
                    "confidence": 0.0
                }

        except Exception as e:
            logger.error(f"Standards agent error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
        finally:
            TenantContext.clear_tenant()

    async def _get_framework(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a standards framework by ID."""
        framework_id = params.get("framework_id")
        if not framework_id:
            return {"status": "error", "error": "framework_id required", "confidence": 0.0}

        try:
            service = StandardsService()
            framework = service.get_framework(self.db, framework_id)
            return {
                "status": "success",
                "framework": {
                    "id": framework.id,
                    "name": framework.name,
                    "authority": framework.authority,
                    "jurisdiction": framework.jurisdiction,
                    "version": framework.version
                },
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _list_standards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List standards with optional filtering."""
        framework_id = params.get("framework_id")
        grade = params.get("grade")
        subject = params.get("subject")
        skip = params.get("skip", 0)
        limit = params.get("limit", 50)

        try:
            service = StandardsService()
            standards, total = service.list_standards(
                self.db,
                framework_id=framework_id,
                grade=grade,
                subject=subject,
                skip=skip,
                limit=limit
            )

            return {
                "status": "success",
                "standards": [
                    {
                        "id": s.id,
                        "code": s.code,
                        "description": s.description,
                        "grade": s.grade,
                        "subject": s.subject,
                        "domain": s.domain
                    }
                    for s in standards
                ],
                "total": total,
                "returned": len(standards),
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _search_standards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search standards by text."""
        query_text = params.get("query")
        framework_id = params.get("framework_id")
        limit = params.get("limit", 20)

        if not query_text:
            return {"status": "error", "error": "query required", "confidence": 0.0}

        try:
            service = StandardsService()
            standards = service.search_standards(
                self.db,
                query_text,
                framework_id=framework_id,
                limit=limit
            )

            return {
                "status": "success",
                "standards": [
                    {
                        "id": s.id,
                        "code": s.code,
                        "description": s.description,
                        "grade": s.grade,
                        "subject": s.subject
                    }
                    for s in standards
                ],
                "returned": len(standards),
                "confidence": 0.90
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _get_by_grade_subject(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get standards for a specific grade and subject."""
        grade = params.get("grade")
        subject = params.get("subject")
        framework_id = params.get("framework_id")

        if not grade or not subject:
            return {"status": "error", "error": "grade and subject required", "confidence": 0.0}

        try:
            service = StandardsService()
            standards = service.get_standards_by_grade_subject(
                self.db,
                grade,
                subject,
                framework_id=framework_id
            )

            return {
                "status": "success",
                "grade": grade,
                "subject": subject,
                "standards": [
                    {
                        "id": s.id,
                        "code": s.code,
                        "description": s.description,
                        "domain": s.domain,
                        "strand": s.strand
                    }
                    for s in standards
                ],
                "total": len(standards),
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _get_hierarchy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get standard hierarchy (parents and children)."""
        standard_id = params.get("standard_id")
        if not standard_id:
            return {"status": "error", "error": "standard_id required", "confidence": 0.0}

        try:
            service = StandardsService()
            hierarchy = service.get_standard_hierarchy(self.db, standard_id)

            return {
                "status": "success",
                "standard": {
                    "id": hierarchy["standard"].id,
                    "code": hierarchy["standard"].code,
                    "description": hierarchy["standard"].description
                },
                "parents": [
                    {"id": p.id, "code": p.code}
                    for p in hierarchy["parents"]
                ],
                "children": [
                    {"id": c.id, "code": c.code}
                    for c in hierarchy["children"]
                ],
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}
