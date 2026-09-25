from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, Optional, List
import logging
from sqlalchemy.orm import Session
from database.models import Skill, KnowledgeContext
from knowledge.context import KnowledgeContextManager

logger = logging.getLogger(__name__)


class StandardsIntelligenceAgent(BaseAgent):
    """Skills & Standards Intelligence Agent - Standards and frameworks management"""

    def __init__(self, db: Session):
        super().__init__("standards_intelligence", db)

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process standards and frameworks tasks"""
        try:
            action = agent_input.data.get("action", "retrieve_standards")

            if action == "retrieve_standards":
                return await self._retrieve_standards(agent_input)
            elif action == "map_to_framework":
                return await self._map_to_framework(agent_input)
            elif action == "validate_compliance":
                return await self._validate_compliance(agent_input)
            elif action == "create_framework":
                return await self._create_framework(agent_input)
            elif action == "align_content":
                return await self._align_content(agent_input)
            else:
                return AgentOutput(
                    status="failed",
                    data={},
                    errors=[f"Unknown action: {action}"]
                )
        except Exception as e:
            logger.error(f"Standards Intelligence Agent error: {e}")
            return AgentOutput(
                status="failed",
                data={},
                errors=[str(e)]
            )

    async def _retrieve_standards(self, agent_input: AgentInput) -> AgentOutput:
        """Retrieve standards and competency frameworks"""
        framework_type = agent_input.data.get("framework_type", "general")
        industry = agent_input.data.get("industry")

        # Query standards from knowledge context
        standards = KnowledgeContextManager.get_context(
            self.db,
            f"standards:{framework_type}"
        )

        if not standards:
            standards = self._get_default_standards(framework_type, industry)

        return AgentOutput(
            status="success",
            data={
                "framework_type": framework_type,
                "industry": industry,
                "standards": standards,
                "count": len(standards) if isinstance(standards, list) else len(standards.get("items", []))
            }
        )

    async def _map_to_framework(self, agent_input: AgentInput) -> AgentOutput:
        """Map skills/content to competency framework"""
        content_id = agent_input.data.get("content_id")
        framework = agent_input.data.get("framework", "DigComp")

        skills = self.db.query(Skill).all()

        mapped_content = {
            "content_id": content_id,
            "framework": framework,
            "alignments": []
        }

        for skill in skills:
            alignment = {
                "skill": skill.name,
                "level": skill.proficiency_level,
                "framework_level": self._map_proficiency_to_framework(skill.proficiency_level, framework),
                "standards": skill.standards or []
            }
            mapped_content["alignments"].append(alignment)

        return AgentOutput(
            status="success",
            data=mapped_content
        )

    async def _validate_compliance(self, agent_input: AgentInput) -> AgentOutput:
        """Validate content compliance with standards"""
        content_id = agent_input.data.get("content_id")
        required_standards = agent_input.data.get("required_standards", [])

        # Query content standards
        from database.models import Content
        content = self.db.query(Content).filter(Content.id == content_id).first()

        if not content:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Content not found: {content_id}"]
            )

        content_standards = content.metadata.get("standards", []) if content.metadata else []

        compliance_report = {
            "content_id": content_id,
            "required_standards": required_standards,
            "content_standards": content_standards,
            "compliant": all(s in content_standards for s in required_standards),
            "missing_standards": [s for s in required_standards if s not in content_standards]
        }

        if not compliance_report["compliant"]:
            compliance_report["requires_human_review"] = True

        return AgentOutput(
            status="success" if compliance_report["compliant"] else "requires_review",
            data=compliance_report,
            requires_human_review=not compliance_report["compliant"],
            review_reason="Standards compliance failed" if not compliance_report["compliant"] else None
        )

    async def _create_framework(self, agent_input: AgentInput) -> AgentOutput:
        """Create or update competency framework"""
        framework_name = agent_input.data.get("name")
        framework_description = agent_input.data.get("description")
        levels = agent_input.data.get("levels", [])
        competencies = agent_input.data.get("competencies", [])

        if not framework_name:
            return AgentOutput(
                status="failed",
                data={},
                errors=["Framework name is required"]
            )

        framework_data = {
            "name": framework_name,
            "description": framework_description,
            "levels": levels,
            "competencies": competencies,
            "total_competencies": len(competencies)
        }

        KnowledgeContextManager.set_context(
            self.db,
            f"standards:frameworks:{framework_name}",
            framework_data
        )

        return AgentOutput(
            status="success",
            data={
                "framework_name": framework_name,
                "competencies_count": len(competencies),
                "levels_count": len(levels),
                "message": f"Framework '{framework_name}' created successfully"
            }
        )

    async def _align_content(self, agent_input: AgentInput) -> AgentOutput:
        """Align content to standards and learning outcomes"""
        content_id = agent_input.data.get("content_id")
        learning_outcomes = agent_input.data.get("learning_outcomes", [])

        from database.models import Content
        content = self.db.query(Content).filter(Content.id == content_id).first()

        if not content:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Content not found: {content_id}"]
            )

        # Update content metadata with alignment
        if not content.metadata:
            content.metadata = {}

        content.metadata["learning_outcomes"] = learning_outcomes
        content.metadata["aligned_standards"] = True
        self.db.commit()

        return AgentOutput(
            status="success",
            data={
                "content_id": content_id,
                "learning_outcomes_aligned": len(learning_outcomes),
                "message": "Content aligned with standards successfully"
            }
        )

    def _map_proficiency_to_framework(self, proficiency_level: str, framework: str) -> str:
        """Map proficiency levels to framework levels"""
        mappings = {
            "DigComp": {
                "beginner": "Foundation",
                "intermediate": "Intermediate",
                "advanced": "Proficient",
                "expert": "Specialist"
            },
            "ESCO": {
                "beginner": "Level 1",
                "intermediate": "Level 2",
                "advanced": "Level 3",
                "expert": "Level 4"
            }
        }

        return mappings.get(framework, {}).get(proficiency_level, proficiency_level)

    def _get_default_standards(self, framework_type: str, industry: Optional[str]) -> Dict[str, Any]:
        """Get default standards for framework type"""
        defaults = {
            "general": {
                "items": [
                    "Communication", "Collaboration", "Critical Thinking",
                    "Problem Solving", "Adaptability", "Creativity"
                ]
            },
            "digital": {
                "items": [
                    "Digital Literacy", "Data Management", "Cloud Computing",
                    "Cybersecurity", "AI/ML Basics", "Automation"
                ]
            },
            "technical": {
                "items": [
                    "Programming", "Database Management", "DevOps",
                    "System Design", "Architecture", "Testing"
                ]
            }
        }

        return defaults.get(framework_type, defaults["general"])
