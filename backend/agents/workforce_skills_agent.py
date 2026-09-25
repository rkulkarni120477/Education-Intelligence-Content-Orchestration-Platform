from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from database.models import Skill

logger = logging.getLogger(__name__)


class WorkforceSkillsAgent(BaseAgent):
    """Workforce Skills Agent - Skills mapping and intelligence"""

    def __init__(self, db: Session):
        super().__init__("workforce_skills", db)

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process workforce skills and competency tasks"""
        try:
            action = agent_input.data.get("action", "analyze")

            if action == "analyze":
                return await self._analyze_skills(agent_input)
            elif action == "map_skills":
                return await self._map_skills(agent_input)
            elif action == "identify_gaps":
                return await self._identify_gaps(agent_input)
            elif action == "create_skill":
                return await self._create_skill(agent_input)
            else:
                return AgentOutput(
                    status="failed",
                    data={},
                    errors=[f"Unknown action: {action}"]
                )
        except Exception as e:
            logger.error(f"Workforce Skills Agent error: {e}")
            return AgentOutput(
                status="failed",
                data={},
                errors=[str(e)]
            )

    async def _analyze_skills(self, agent_input: AgentInput) -> AgentOutput:
        """Analyze workforce skills"""
        job_role = agent_input.data.get("job_role")
        industry = agent_input.data.get("industry")

        # Query relevant skills
        skills = self.db.query(Skill).filter(
            Skill.category == industry if industry else True
        ).all()

        analysis = {
            "job_role": job_role,
            "industry": industry,
            "total_skills_found": len(skills),
            "skills": [
                {
                    "id": s.id,
                    "name": s.name,
                    "proficiency_level": s.proficiency_level,
                    "category": s.category
                }
                for s in skills[:10]
            ]
        }

        return AgentOutput(
            status="success",
            data=analysis
        )

    async def _map_skills(self, agent_input: AgentInput) -> AgentOutput:
        """Map skills to standards and frameworks"""
        skills_list = agent_input.data.get("skills", [])
        framework = agent_input.data.get("framework", "DigComp")

        mapped_skills = []
        for skill_name in skills_list:
            skill = self.db.query(Skill).filter(
                Skill.name.ilike(f"%{skill_name}%")
            ).first()

            if skill:
                mapped_skills.append({
                    "skill": skill.name,
                    "proficiency_level": skill.proficiency_level,
                    "framework": framework,
                    "standards": skill.standards or []
                })

        return AgentOutput(
            status="success",
            data={
                "framework": framework,
                "mapped_skills": mapped_skills,
                "total_mapped": len(mapped_skills)
            }
        )

    async def _identify_gaps(self, agent_input: AgentInput) -> AgentOutput:
        """Identify skill gaps in workforce"""
        current_skills = agent_input.data.get("current_skills", [])
        required_skills = agent_input.data.get("required_skills", [])

        current_set = set(current_skills)
        required_set = set(required_skills)

        gaps = list(required_set - current_set)
        proficient = list(required_set & current_set)

        gap_analysis = {
            "current_skills_count": len(current_set),
            "required_skills_count": len(required_set),
            "skill_gaps": gaps,
            "gap_count": len(gaps),
            "proficient_skills": proficient,
            "proficiency_percentage": (len(proficient) / len(required_set) * 100) if required_set else 0
        }

        if len(gaps) > 0:
            gap_analysis["requires_training"] = True

        return AgentOutput(
            status="success",
            data=gap_analysis
        )

    async def _create_skill(self, agent_input: AgentInput) -> AgentOutput:
        """Create new skill in knowledge base"""
        skill_name = agent_input.data.get("name")
        description = agent_input.data.get("description")
        category = agent_input.data.get("category")
        proficiency_level = agent_input.data.get("proficiency_level", "intermediate")
        standards = agent_input.data.get("standards", [])

        if not skill_name:
            return AgentOutput(
                status="failed",
                data={},
                errors=["Skill name is required"]
            )

        # Check for duplicate
        existing = self.db.query(Skill).filter(Skill.name == skill_name).first()
        if existing:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Skill '{skill_name}' already exists"]
            )

        skill = Skill(
            name=skill_name,
            description=description,
            category=category,
            proficiency_level=proficiency_level,
            standards=standards
        )
        self.db.add(skill)
        self.db.commit()

        return AgentOutput(
            status="success",
            data={
                "skill_id": skill.id,
                "name": skill.name,
                "category": skill.category,
                "message": f"Skill '{skill_name}' created successfully"
            }
        )
