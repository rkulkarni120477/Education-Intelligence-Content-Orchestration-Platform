"""
Skill Mapping Service.

Maps workforce skills to course content using Claude, calculates coverage,
and identifies gaps. Creates alignment records with evidence tracking.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from dataclasses import dataclass
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class SkillAlignment:
    """A single skill-to-content alignment."""
    skill_name: str
    skill_id: str
    content_id: str
    content_title: str
    alignment_type: str  # covers, introduces, reinforces, assesses, etc.
    proficiency_level: str  # beginner, intermediate, advanced, expert
    confidence: float  # 0-1
    evidence: List[str]  # Direct quotes or references
    supporting_objectives: List[str]


@dataclass
class GapAnalysis:
    """Gap analysis for missing skills."""
    skill_name: str
    skill_id: str
    required_proficiency: str
    current_coverage: float  # 0-1
    gap_severity: str  # critical, high, medium, low
    gap_description: str
    recommendations: List[str]


class SkillMappingResult(BaseModel):
    """Results from skill mapping analysis."""
    total_skills: int
    total_content_items: int
    total_alignments: int
    coverage_by_skill: Dict[str, float]  # skill_id -> coverage percentage
    covered_skills: List[str]  # Skills with coverage >= threshold
    partially_covered_skills: List[str]  # Skills with some coverage
    uncovered_skills: List[str]  # Skills with no coverage
    overall_coverage: float  # Weighted average coverage
    critical_gaps: List[Dict[str, Any]]
    alignment_confidence: float  # Average confidence across alignments
    mapping_metadata: Dict[str, Any]


class SkillMappingService:
    """Service for mapping workforce skills to course content."""

    def __init__(self, model: str = "claude-opus-5-5"):
        """
        Initialize the skill mapping service.

        Args:
            model: Claude model to use
        """
        self.model = model
        self.client = ChatAnthropic(model=model)

    def map_skills_to_content(
        self,
        course_title: str,
        course_objectives: List[str],
        course_content: List[Dict[str, str]],  # {title, description, type}
        required_skills: List[Dict[str, str]],  # {name, level, id}
        proficiency_rubric: Optional[Dict[str, List[str]]] = None,
    ) -> SkillMappingResult:
        """
        Map workforce skills to course content.

        Args:
            course_title: Title of the course
            course_objectives: Learning objectives from course
            course_content: Content items (modules, lessons, activities)
            required_skills: Required workforce skills
            proficiency_rubric: Proficiency level descriptions

        Returns:
            SkillMappingResult with all alignments and gap analysis
        """
        try:
            logger.info(f"Mapping {len(required_skills)} skills to {len(course_content)} content items")

            # Call Claude to identify alignments
            alignments = self._identify_alignments_with_claude(
                course_title=course_title,
                course_objectives=course_objectives,
                course_content=course_content,
                required_skills=required_skills,
            )

            # Calculate coverage metrics
            coverage = self._calculate_coverage(alignments, required_skills)

            # Identify gaps
            gaps = self._identify_gaps(required_skills, coverage)

            # Build result
            result = SkillMappingResult(
                total_skills=len(required_skills),
                total_content_items=len(course_content),
                total_alignments=len(alignments),
                coverage_by_skill=coverage,
                covered_skills=self._get_covered_skills(coverage, threshold=0.8),
                partially_covered_skills=self._get_partial_skills(coverage, threshold=0.3),
                uncovered_skills=self._get_uncovered_skills(coverage, threshold=0.1),
                overall_coverage=self._calculate_overall_coverage(coverage),
                critical_gaps=[g for g in gaps if g['gap_severity'] == 'critical'],
                alignment_confidence=self._calculate_avg_confidence(alignments),
                mapping_metadata={
                    'model': self.model,
                    'proficiency_rubric': proficiency_rubric is not None,
                    'alignment_method': 'claude-api',
                }
            )

            logger.info(f"✓ Mapped {len(alignments)} alignments, overall coverage: {result.overall_coverage:.1%}")
            return result

        except Exception as e:
            logger.error(f"Skill mapping failed: {str(e)}")
            raise

    def _identify_alignments_with_claude(
        self,
        course_title: str,
        course_objectives: List[str],
        course_content: List[Dict[str, str]],
        required_skills: List[Dict[str, str]],
    ) -> List[SkillAlignment]:
        """Identify skill-to-content alignments using Claude."""

        # Build system prompt
        system_prompt = """You are an expert curriculum analyst. Your task is to identify
alignments between workforce skills and course content.

For each skill, identify:
1. Which course objectives and content items address it
2. At what proficiency level (beginner, intermediate, advanced, expert)
3. The type of alignment (introduces, reinforces, assesses, etc.)
4. Direct evidence from course materials

Format your response as JSON with this structure:
{
  "alignments": [
    {
      "skill_name": "...",
      "skill_id": "...",
      "content_title": "...",
      "content_id": "...",
      "alignment_type": "introduces|reinforces|assesses|covers",
      "proficiency_level": "beginner|intermediate|advanced|expert",
      "confidence": 0.85,
      "evidence": ["quote1", "quote2"],
      "supporting_objectives": ["objective1"]
    }
  ],
  "notes": "..."
}"""

        # Build user message
        content_summary = json.dumps(course_content[:5])  # Limit to first 5 for context
        skills_summary = json.dumps(required_skills)

        user_message = f"""Course: {course_title}

Objectives:
{json.dumps(course_objectives)}

Key Content Items:
{content_summary}

Required Skills:
{skills_summary}

Identify all skill-to-content alignments."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]

        try:
            response = self.client.invoke(messages)
            response_text = response.content

            # Parse JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")

            # Convert to SkillAlignment objects
            alignments = []
            for align_data in data.get('alignments', []):
                alignment = SkillAlignment(
                    skill_name=align_data.get('skill_name', ''),
                    skill_id=align_data.get('skill_id', ''),
                    content_id=align_data.get('content_id', ''),
                    content_title=align_data.get('content_title', ''),
                    alignment_type=align_data.get('alignment_type', 'covers'),
                    proficiency_level=align_data.get('proficiency_level', 'intermediate'),
                    confidence=float(align_data.get('confidence', 0.5)),
                    evidence=align_data.get('evidence', []),
                    supporting_objectives=align_data.get('supporting_objectives', []),
                )
                alignments.append(alignment)

            return alignments

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse alignment response: {str(e)}")
            return []

    def _calculate_coverage(
        self,
        alignments: List[SkillAlignment],
        required_skills: List[Dict[str, str]],
    ) -> Dict[str, float]:
        """Calculate coverage percentage for each skill."""
        coverage = {}

        for skill in required_skills:
            skill_id = skill.get('id', skill.get('name', ''))
            skill_alignments = [a for a in alignments if a.skill_id == skill_id]

            if skill_alignments:
                # Coverage is average confidence of alignments
                avg_confidence = sum(a.confidence for a in skill_alignments) / len(skill_alignments)
                coverage[skill_id] = avg_confidence
            else:
                coverage[skill_id] = 0.0

        return coverage

    def _identify_gaps(
        self,
        required_skills: List[Dict[str, str]],
        coverage: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Identify gaps in skill coverage."""
        gaps = []

        for skill in required_skills:
            skill_id = skill.get('id', skill.get('name', ''))
            skill_name = skill.get('name', skill_id)
            required_level = skill.get('level', 'intermediate')
            current_coverage = coverage.get(skill_id, 0.0)

            if current_coverage < 0.8:  # Less than 80% coverage is a gap
                gap_severity = self._determine_gap_severity(current_coverage)

                gap = {
                    'skill_id': skill_id,
                    'skill_name': skill_name,
                    'required_proficiency': required_level,
                    'current_coverage': current_coverage,
                    'gap_severity': gap_severity,
                    'gap_description': f"Missing {(1 - current_coverage):.0%} coverage of {skill_name}",
                    'recommendations': self._generate_gap_recommendations(skill_name, required_level),
                }
                gaps.append(gap)

        return gaps

    def _determine_gap_severity(self, coverage: float) -> str:
        """Determine severity of gap based on coverage."""
        if coverage == 0.0:
            return 'critical'
        elif coverage < 0.3:
            return 'high'
        elif coverage < 0.6:
            return 'medium'
        else:
            return 'low'

    def _generate_gap_recommendations(self, skill_name: str, proficiency: str) -> List[str]:
        """Generate recommendations for addressing gaps."""
        return [
            f"Add content covering {skill_name} at {proficiency} level",
            f"Include {skill_name} in learning objectives",
            f"Create practice activities for {skill_name}",
            f"Add assessment items for {skill_name}",
        ]

    def _get_covered_skills(self, coverage: Dict[str, float], threshold: float = 0.8) -> List[str]:
        """Get skills with coverage above threshold."""
        return [skill_id for skill_id, cov in coverage.items() if cov >= threshold]

    def _get_partial_skills(self, coverage: Dict[str, float], threshold: float = 0.3) -> List[str]:
        """Get skills with partial coverage."""
        return [skill_id for skill_id, cov in coverage.items() if 0.1 < cov < 0.8]

    def _get_uncovered_skills(self, coverage: Dict[str, float], threshold: float = 0.1) -> List[str]:
        """Get skills with little to no coverage."""
        return [skill_id for skill_id, cov in coverage.items() if cov <= 0.1]

    def _calculate_overall_coverage(self, coverage: Dict[str, float]) -> float:
        """Calculate weighted average coverage across all skills."""
        if not coverage:
            return 0.0
        return sum(coverage.values()) / len(coverage)

    def _calculate_avg_confidence(self, alignments: List[SkillAlignment]) -> float:
        """Calculate average confidence across alignments."""
        if not alignments:
            return 0.0
        return sum(a.confidence for a in alignments) / len(alignments)
