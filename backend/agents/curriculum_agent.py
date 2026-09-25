"""
Curriculum Agent - Manages curriculum structures and analysis.

Responsible for:
- Creating and managing curricula
- Building curriculum structures (units, objectives)
- Analyzing curriculum coverage
- Identifying gaps
"""

from agents.base_agent import BaseAgent, AgentInput
from services.curriculum_service import CurriculumService
from auth.tenant_context import TenantContext
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CurriculumAgent(BaseAgent):
    """Curriculum management and analysis agent."""

    @property
    def name(self) -> str:
        return "curriculum"

    @property
    def description(self) -> str:
        return "Manages curriculum structures and analyzes coverage"

    @property
    def tools(self) -> List[str]:
        return [
            "create_curriculum",
            "get_structure",
            "add_unit",
            "add_objective",
            "analyze_coverage"
        ]

    async def _execute(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute curriculum operations.

        Tasks:
        - create_curriculum: Create new curriculum
        - get_structure: Get full curriculum structure
        - add_unit: Add unit to curriculum
        - add_objective: Add objective to unit
        - analyze_coverage: Analyze standards coverage
        """
        logger.info(f"Curriculum agent executing: {agent_input.task}")

        # Set tenant context
        TenantContext.set_tenant(agent_input.tenant_id)

        try:
            task = agent_input.task
            params = agent_input.parameters

            if task == "create_curriculum":
                return await self._create_curriculum(params)
            elif task == "get_structure":
                return await self._get_structure(params)
            elif task == "add_unit":
                return await self._add_unit(params)
            elif task == "add_objective":
                return await self._add_objective(params)
            elif task == "analyze_coverage":
                return await self._analyze_coverage(params)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown task: {task}",
                    "confidence": 0.0
                }

        except Exception as e:
            logger.error(f"Curriculum agent error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
        finally:
            TenantContext.clear_tenant()

    async def _create_curriculum(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new curriculum."""
        name = params.get("name")
        grade = params.get("grade")
        subject = params.get("subject")

        if not name:
            return {"status": "error", "error": "name required", "confidence": 0.0}

        try:
            service = CurriculumService()
            curriculum = service.create_curriculum(
                self.db,
                name=name,
                grade=grade,
                subject=subject,
                description=params.get("description"),
                version=params.get("version", "1.0")
            )

            return {
                "status": "success",
                "curriculum_id": curriculum.id,
                "name": curriculum.name,
                "version": curriculum.version,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _get_structure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get full curriculum structure."""
        curriculum_id = params.get("curriculum_id")
        if not curriculum_id:
            return {"status": "error", "error": "curriculum_id required", "confidence": 0.0}

        try:
            service = CurriculumService()
            structure = service.get_curriculum_structure(self.db, curriculum_id)

            # Convert to serializable format
            def unit_to_dict(unit_struct):
                return {
                    "unit": {
                        "id": unit_struct["unit"].id,
                        "title": unit_struct["unit"].title,
                        "sequence": unit_struct["unit"].sequence
                    },
                    "objectives": [
                        {"id": o.id, "objective": o.objective}
                        for o in unit_struct["objectives"]
                    ],
                    "children": [unit_to_dict(child) for child in unit_struct["children"]]
                }

            return {
                "status": "success",
                "curriculum": {
                    "id": structure["curriculum"].id,
                    "name": structure["curriculum"].name,
                    "version": structure["curriculum"].version
                },
                "units": [unit_to_dict(u) for u in structure["units"]],
                "unit_count": len(structure["units"]),
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _add_unit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a unit to curriculum."""
        curriculum_id = params.get("curriculum_id")
        title = params.get("title")

        if not curriculum_id or not title:
            return {
                "status": "error",
                "error": "curriculum_id and title required",
                "confidence": 0.0
            }

        try:
            service = CurriculumService()
            unit = service.create_unit(
                self.db,
                curriculum_id,
                title,
                description=params.get("description"),
                sequence=params.get("sequence"),
                parent_id=params.get("parent_id")
            )

            return {
                "status": "success",
                "unit_id": unit.id,
                "title": unit.title,
                "sequence": unit.sequence,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _add_objective(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add an objective to a unit."""
        unit_id = params.get("unit_id")
        objective = params.get("objective")

        if not unit_id or not objective:
            return {
                "status": "error",
                "error": "unit_id and objective required",
                "confidence": 0.0
            }

        try:
            service = CurriculumService()
            obj = service.create_objective(
                self.db,
                unit_id,
                objective,
                cognitive_level=params.get("cognitive_level")
            )

            return {
                "status": "success",
                "objective_id": obj.id,
                "objective": obj.objective,
                "cognitive_level": obj.cognitive_level,
                "confidence": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _analyze_coverage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze curriculum coverage against standards framework."""
        curriculum_id = params.get("curriculum_id")
        framework_id = params.get("framework_id")

        if not curriculum_id or not framework_id:
            return {
                "status": "error",
                "error": "curriculum_id and framework_id required",
                "confidence": 0.0
            }

        try:
            service = CurriculumService()
            coverage = service.analyze_curriculum_coverage(
                self.db,
                curriculum_id,
                framework_id
            )

            return {
                "status": "success",
                "curriculum_id": curriculum_id,
                "framework_id": framework_id,
                "coverage_analysis": {
                    "total_standards": coverage["total_standards"],
                    "covered_count": coverage["covered_count"],
                    "uncovered_count": coverage["uncovered_count"],
                    "coverage_percentage": coverage["coverage_percentage"]
                },
                "covered_standards_count": len(coverage["covered_standards"]),
                "uncovered_standards_count": len(coverage["uncovered_standards"]),
                "confidence": 0.92
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}
