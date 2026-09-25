"""
Workforce Skills Agent using LangChain
Analyzes workforce skills requirements and identifies curriculum gaps.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
import json

logger = logging.getLogger(__name__)


class WorkRoleCategory(str, Enum):
    """NIST NICE Framework work role categories"""
    SECURELY_PROVISION = "Securely Provision"
    OPERATE_MAINTAIN = "Operate and Maintain"
    PROTECT_DEFEND = "Protect and Defend"
    INVESTIGATE = "Investigate"
    COLLECT_OPERATE = "Collect and Operate"


class NISTCompetency(BaseModel):
    """NIST NICE Framework competency"""
    id: str
    name: str
    category: WorkRoleCategory
    description: str
    proficiency_levels: List[str] = ["Foundation", "Intermediate", "Advanced"]


class SkillGap(BaseModel):
    """Identified skill gap"""
    competency: NISTCompetency
    required_by_roles: List[str]
    current_coverage: float  # 0-100%
    gap_severity: str  # "Critical", "High", "Medium", "Low"
    recommended_action: str


class WorkforceSKillsAgentLangChain:
    """
    LangChain-based Workforce Skills Agent

    Responsibilities:
    - Extract required skills for target job roles (NIST NICE Framework)
    - Map curriculum to competencies
    - Identify gaps and coverage percentage
    - Recommend curriculum updates
    """

    # NIST NICE Framework competencies (simplified)
    NICE_COMPETENCIES = {
        "IT Security": NISTCompetency(
            id="comp_001",
            name="IT Security",
            category=WorkRoleCategory.PROTECT_DEFEND,
            description="Knowledge of IT security principles and practices"
        ),
        "Network Security": NISTCompetency(
            id="comp_002",
            name="Network Security",
            category=WorkRoleCategory.PROTECT_DEFEND,
            description="Understanding of network architecture and security"
        ),
        "Cloud Security": NISTCompetency(
            id="comp_003",
            name="Cloud Security",
            category=WorkRoleCategory.PROTECT_DEFEND,
            description="Security of cloud computing platforms and services"
        ),
        "Incident Response": NISTCompetency(
            id="comp_004",
            name="Incident Response",
            category=WorkRoleCategory.INVESTIGATE,
            description="Ability to respond to and manage security incidents"
        ),
        "Forensics": NISTCompetency(
            id="comp_005",
            name="Digital Forensics",
            category=WorkRoleCategory.INVESTIGATE,
            description="Collecting and analyzing digital evidence"
        ),
        "Access Control": NISTCompetency(
            id="comp_006",
            name="Access Control",
            category=WorkRoleCategory.PROTECT_DEFEND,
            description="Identity and access management principles"
        ),
        "Encryption": NISTCompetency(
            id="comp_007",
            name="Encryption",
            category=WorkRoleCategory.PROTECT_DEFEND,
            description="Cryptography and encryption technologies"
        ),
        "Vulnerability Assessment": NISTCompetency(
            id="comp_008",
            name="Vulnerability Assessment",
            category=WorkRoleCategory.PROTECT_DEFEND,
            description="Identifying and assessing security vulnerabilities"
        ),
        "Compliance": NISTCompetency(
            id="comp_009",
            name="Regulatory Compliance",
            category=WorkRoleCategory.PROTECT_DEFEND,
            description="Understanding security regulations and standards"
        ),
        "Risk Management": NISTCompetency(
            id="comp_010",
            name="Risk Management",
            category=WorkRoleCategory.PROTECT_DEFEND,
            description="Assessing and managing security risks"
        ),
        "Systems Administration": NISTCompetency(
            id="comp_011",
            name="Systems Administration",
            category=WorkRoleCategory.OPERATE_MAINTAIN,
            description="Managing IT systems and infrastructure"
        ),
        "Networking": NISTCompetency(
            id="comp_012",
            name="Networking Fundamentals",
            category=WorkRoleCategory.OPERATE_MAINTAIN,
            description="TCP/IP, network protocols, and architecture"
        ),
    }

    # Job role requirements (maps roles to required competencies)
    JOB_ROLE_REQUIREMENTS = {
        "SOC Analyst I": {
            "competencies": [
                "IT Security",
                "Network Security",
                "Incident Response",
                "Vulnerability Assessment",
                "Systems Administration",
                "Networking Fundamentals"
            ],
            "experience_level": "Entry",
            "certifications": ["CompTIA Security+", "CEH"]
        },
        "Cloud Security Associate": {
            "competencies": [
                "Cloud Security",
                "IT Security",
                "Access Control",
                "Encryption",
                "Compliance",
                "Risk Management"
            ],
            "experience_level": "Associate",
            "certifications": ["AWS Security Specialty", "Azure Security Engineer"]
        },
        "Incident Response Technician": {
            "competencies": [
                "Incident Response",
                "Forensics",
                "Networking Fundamentals",
                "IT Security",
                "Systems Administration",
                "Vulnerability Assessment"
            ],
            "experience_level": "Intermediate",
            "certifications": ["GCIH", "GIAC Certified Incident Handler"]
        },
        "Security Systems Administrator": {
            "competencies": [
                "Systems Administration",
                "Access Control",
                "Networking Fundamentals",
                "Compliance",
                "IT Security",
                "Risk Management"
            ],
            "experience_level": "Intermediate",
            "certifications": ["CISSP", "CompTIA Security+"]
        },
        "Penetration Tester": {
            "competencies": [
                "Vulnerability Assessment",
                "IT Security",
                "Networking Fundamentals",
                "Systems Administration",
                "Encryption",
                "Incident Response"
            ],
            "experience_level": "Advanced",
            "certifications": ["OSCP", "CEH"]
        }
    }

    def __init__(self, db=None):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def analyze_curriculum_gaps(
        self,
        target_roles: List[str],
        curriculum_content: Dict[str, Any],
        knowledge_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze curriculum against target job roles.

        Args:
            target_roles: List of target job roles
            curriculum_content: Parsed curriculum content
            knowledge_chunks: Content chunks from Knowledge Intelligence Agent

        Returns:
            Gap analysis with coverage percentages
        """
        self.logger.info(f"Analyzing curriculum gaps for roles: {target_roles}")

        try:
            # Step 1: Get required competencies for target roles
            required_competencies = self._get_required_competencies(target_roles)

            # Step 2: Extract curriculum competencies
            covered_competencies = self._extract_covered_competencies(
                curriculum_content,
                knowledge_chunks
            )

            # Step 3: Identify gaps
            gaps = self._identify_gaps(required_competencies, covered_competencies)

            # Step 4: Calculate coverage metrics
            coverage_metrics = self._calculate_coverage(
                required_competencies,
                covered_competencies,
                target_roles
            )

            return {
                "status": "completed",
                "target_roles": target_roles,
                "required_competencies": len(required_competencies),
                "covered_competencies": len(covered_competencies),
                "coverage_percentage": coverage_metrics["overall_coverage"],
                "coverage_by_role": coverage_metrics["by_role"],
                "gaps": [
                    {
                        "competency": gap.competency.name,
                        "required_by_roles": gap.required_by_roles,
                        "gap_severity": gap.gap_severity,
                        "recommended_action": gap.recommended_action
                    }
                    for gap in gaps
                ],
                "competency_framework": "NIST NICE",
                "gap_count_by_severity": self._count_gaps_by_severity(gaps)
            }

        except Exception as e:
            self.logger.error(f"Error analyzing curriculum gaps: {str(e)}")
            raise

    def _get_required_competencies(self, target_roles: List[str]) -> Dict[str, NISTCompetency]:
        """Get all required competencies for target roles"""
        required = {}

        for role in target_roles:
            if role in self.JOB_ROLE_REQUIREMENTS:
                role_reqs = self.JOB_ROLE_REQUIREMENTS[role]
                for comp_name in role_reqs["competencies"]:
                    if comp_name in self.NICE_COMPETENCIES:
                        comp = self.NICE_COMPETENCIES[comp_name]
                        required[comp.id] = comp

        return required

    def _extract_covered_competencies(
        self,
        curriculum_content: Dict[str, Any],
        knowledge_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, NISTCompetency]:
        """Extract competencies covered by curriculum"""
        covered = {}

        # Extract from curriculum modules and learning outcomes
        modules = curriculum_content.get('modules', [])

        for module in modules:
            module_title = module.get('title', '').lower()
            outcomes = module.get('learning_outcomes', [])

            # Map module titles to competencies
            for comp_name, competency in self.NICE_COMPETENCIES.items():
                if self._matches_competency(module_title, comp_name.lower()):
                    covered[competency.id] = competency
                    continue

                # Check learning outcomes
                for outcome in outcomes:
                    if self._matches_competency(outcome.lower(), comp_name.lower()):
                        covered[competency.id] = competency
                        break

        return covered

    def _matches_competency(self, text: str, competency_name: str) -> bool:
        """Check if text mentions competency"""
        # Simple keyword matching
        keywords = competency_name.split()
        return any(keyword in text for keyword in keywords)

    def _identify_gaps(
        self,
        required: Dict[str, NISTCompetency],
        covered: Dict[str, NISTCompetency]
    ) -> List[SkillGap]:
        """Identify competency gaps"""
        gaps = []

        for comp_id, competency in required.items():
            if comp_id not in covered:
                # Find which roles need this competency
                roles_needing = []
                for role, reqs in self.JOB_ROLE_REQUIREMENTS.items():
                    if competency.name in reqs["competencies"]:
                        roles_needing.append(role)

                # Determine gap severity
                severity = "High" if len(roles_needing) > 2 else "Medium"

                gap = SkillGap(
                    competency=competency,
                    required_by_roles=roles_needing,
                    current_coverage=0.0,
                    gap_severity=severity,
                    recommended_action=f"Add content for {competency.name} covering {', '.join(reqs.get('competencies', [])[:2])}"
                )
                gaps.append(gap)

        return gaps

    def _calculate_coverage(
        self,
        required: Dict[str, NISTCompetency],
        covered: Dict[str, NISTCompetency],
        target_roles: List[str]
    ) -> Dict[str, Any]:
        """Calculate coverage metrics"""

        # Overall coverage
        total_required = len(required)
        total_covered = len(covered)
        overall_coverage = (total_covered / total_required * 100) if total_required > 0 else 0

        # Coverage by role
        by_role = {}
        for role in target_roles:
            if role in self.JOB_ROLE_REQUIREMENTS:
                role_comps = self.JOB_ROLE_REQUIREMENTS[role]["competencies"]
                role_covered = 0

                for comp_name in role_comps:
                    if comp_name in self.NICE_COMPETENCIES:
                        comp = self.NICE_COMPETENCIES[comp_name]
                        if comp.id in covered:
                            role_covered += 1

                coverage_pct = (role_covered / len(role_comps) * 100) if role_comps else 0
                by_role[role] = {
                    "covered": role_covered,
                    "total": len(role_comps),
                    "coverage_percentage": coverage_pct
                }

        return {
            "overall_coverage": overall_coverage,
            "by_role": by_role
        }

    def _count_gaps_by_severity(self, gaps: List[SkillGap]) -> Dict[str, int]:
        """Count gaps by severity"""
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for gap in gaps:
            counts[gap.gap_severity] = counts.get(gap.gap_severity, 0) + 1
        return counts

    def get_recommendations(self, gaps: List[SkillGap]) -> List[Dict[str, Any]]:
        """Generate content recommendations based on gaps"""
        recommendations = []

        for gap in gaps:
            recommendations.append({
                "competency": gap.competency.name,
                "gap_severity": gap.gap_severity,
                "recommended_modules": [
                    f"Module: Introduction to {gap.competency.name}",
                    f"Module: {gap.competency.name} Fundamentals",
                    f"Module: {gap.competency.name} Advanced Topics",
                    f"Assessment: {gap.competency.name} Quiz",
                    f"Assessment: {gap.competency.name} Hands-on Lab"
                ],
                "estimated_hours": 30,
                "priority": "High" if gap.gap_severity in ["Critical", "High"] else "Medium"
            })

        return recommendations
