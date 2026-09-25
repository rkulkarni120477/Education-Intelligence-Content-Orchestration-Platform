"""
Recommendations Service.

Generates recommendations for curriculum improvements based on skill gaps,
coverage analysis, and educational best practices.
"""

from typing import Dict, List, Any, Optional
import json
import logging
from dataclasses import dataclass
from enum import Enum
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RecommendationType(str, Enum):
    """Types of recommendations."""
    ADD_CONTENT = "add_content"
    REORDER_CONTENT = "reorder_content"
    ENHANCE_ASSESSMENT = "enhance_assessment"
    ADD_PRACTICE = "add_practice"
    IMPROVE_CLARITY = "improve_clarity"
    ADD_ACCESSIBILITY = "add_accessibility"
    IMPROVE_SEQUENCING = "improve_sequencing"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Recommendation:
    """A single curriculum improvement recommendation."""
    id: str
    type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    rationale: str
    implementation_steps: List[str]
    affected_skills: List[str]
    estimated_effort: str  # small, medium, large
    expected_impact: str  # description of expected improvement
    source: str  # e.g., "gap_analysis", "coverage_analysis", "assessment_gap"


class RecommendationsResult(BaseModel):
    """Results from recommendations generation."""
    total_recommendations: int
    critical_recommendations: List[Dict[str, Any]]
    high_priority_recommendations: List[Dict[str, Any]]
    medium_priority_recommendations: List[Dict[str, Any]]
    low_priority_recommendations: List[Dict[str, Any]]
    recommendations_by_type: Dict[str, int]
    estimated_total_effort: str  # small, medium, large
    recommendations_metadata: Dict[str, Any]


class RecommendationsService:
    """Service for generating curriculum improvement recommendations."""

    def __init__(self, model: str = "claude-opus-5-5"):
        """
        Initialize the recommendations service.

        Args:
            model: Claude model to use
        """
        self.model = model
        self.client = ChatAnthropic(model=model)

    def generate_recommendations(
        self,
        course_title: str,
        current_coverage: Dict[str, float],  # skill_id -> coverage percentage
        gaps: List[Dict[str, Any]],
        course_structure: Dict[str, Any],
        existing_recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> RecommendationsResult:
        """
        Generate curriculum improvement recommendations.

        Args:
            course_title: Title of the course
            current_coverage: Coverage metrics by skill
            gaps: Identified gaps from skill mapping
            course_structure: Current course structure
            existing_recommendations: Previously generated recommendations

        Returns:
            RecommendationsResult with prioritized recommendations
        """
        try:
            logger.info(f"Generating recommendations for {course_title}")

            # Call Claude to generate recommendations
            recommendations = self._generate_with_claude(
                course_title=course_title,
                current_coverage=current_coverage,
                gaps=gaps,
                course_structure=course_structure,
            )

            # Prioritize recommendations
            prioritized = self._prioritize_recommendations(recommendations)

            # Group by priority
            result = RecommendationsResult(
                total_recommendations=len(prioritized),
                critical_recommendations=[r for r in prioritized if r['priority'] == 'critical'],
                high_priority_recommendations=[r for r in prioritized if r['priority'] == 'high'],
                medium_priority_recommendations=[r for r in prioritized if r['priority'] == 'medium'],
                low_priority_recommendations=[r for r in prioritized if r['priority'] == 'low'],
                recommendations_by_type=self._count_by_type(prioritized),
                estimated_total_effort=self._estimate_total_effort(prioritized),
                recommendations_metadata={
                    'model': self.model,
                    'generation_method': 'claude-api',
                    'gap_count': len(gaps),
                    'coverage_average': sum(current_coverage.values()) / len(current_coverage) if current_coverage else 0,
                }
            )

            logger.info(f"✓ Generated {len(prioritized)} recommendations")
            return result

        except Exception as e:
            logger.error(f"Recommendations generation failed: {str(e)}")
            raise

    def _generate_with_claude(
        self,
        course_title: str,
        current_coverage: Dict[str, float],
        gaps: List[Dict[str, Any]],
        course_structure: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate recommendations using Claude."""

        system_prompt = """You are an expert curriculum designer. Generate specific,
actionable recommendations for improving a course based on skill coverage analysis.

For each recommendation, provide:
1. Type (add_content, reorder, enhance_assessment, add_practice, improve_clarity, etc.)
2. Priority (critical, high, medium, low)
3. Title and description
4. Rationale tied to skill gaps
5. Step-by-step implementation plan
6. Affected skills
7. Estimated effort (small, medium, large)
8. Expected impact description

Format as JSON:
{
  "recommendations": [
    {
      "id": "rec_001",
      "type": "add_content",
      "priority": "critical",
      "title": "...",
      "description": "...",
      "rationale": "...",
      "implementation_steps": ["step1", "step2"],
      "affected_skills": ["skill_id1"],
      "estimated_effort": "medium",
      "expected_impact": "...",
      "source": "gap_analysis"
    }
  ]
}"""

        # Build user message
        critical_gaps = [g for g in gaps if g.get('gap_severity') == 'critical']
        high_gaps = [g for g in gaps if g.get('gap_severity') == 'high']

        user_message = f"""Course: {course_title}

Coverage Analysis:
- Skills covered: {len([c for c in current_coverage.values() if c >= 0.8])}
- Partial coverage: {len([c for c in current_coverage.values() if 0.3 <= c < 0.8])}
- Uncovered: {len([c for c in current_coverage.values() if c < 0.3])}

Critical Gaps ({len(critical_gaps)}):
{json.dumps(critical_gaps[:3])}

High Priority Gaps ({len(high_gaps)}):
{json.dumps(high_gaps[:3])}

Generate recommendations to address these gaps and improve course quality."""

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
                return data.get('recommendations', [])
            else:
                raise ValueError("No JSON found in response")

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse recommendations response: {str(e)}")
            return []

    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure all recommendations have valid priority values."""
        valid_priorities = {rec.get('priority', 'medium') for rec in recommendations}

        for rec in recommendations:
            if 'priority' not in rec:
                rec['priority'] = 'medium'
            if rec['priority'] not in ['critical', 'high', 'medium', 'low']:
                rec['priority'] = 'medium'

        return sorted(recommendations, key=lambda x: self._priority_order(x['priority']))

    def _priority_order(self, priority: str) -> int:
        """Get sort order for priority."""
        order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        return order.get(priority, 2)

    def _count_by_type(self, recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count recommendations by type."""
        counts = {}
        for rec in recommendations:
            rec_type = rec.get('type', 'unknown')
            counts[rec_type] = counts.get(rec_type, 0) + 1
        return counts

    def _estimate_total_effort(self, recommendations: List[Dict[str, Any]]) -> str:
        """Estimate total effort for implementing all recommendations."""
        effort_scores = {'small': 1, 'medium': 2, 'large': 3}

        if not recommendations:
            return 'small'

        total_score = sum(effort_scores.get(r.get('estimated_effort', 'medium'), 2) for r in recommendations)
        avg_score = total_score / len(recommendations)

        if avg_score < 1.5:
            return 'small'
        elif avg_score < 2.5:
            return 'medium'
        else:
            return 'large'

    def generate_gap_content_recommendations(
        self,
        skill_name: str,
        gap_severity: str,
        proficiency_level: str,
        course_context: str,
    ) -> List[Dict[str, str]]:
        """
        Generate specific content recommendations for a skill gap.

        Args:
            skill_name: Name of the skill with gap
            gap_severity: critical, high, medium, low
            proficiency_level: Required proficiency level
            course_context: Context about the course

        Returns:
            List of specific content recommendations
        """
        recommendations = []

        if gap_severity == 'critical':
            recommendations.extend([
                f"Create foundational lesson on {skill_name}",
                f"Add practice activities for {skill_name} at {proficiency_level} level",
                f"Include assessment items measuring {skill_name} mastery",
            ])
        elif gap_severity == 'high':
            recommendations.extend([
                f"Expand existing {skill_name} coverage",
                f"Add reinforcement activities for {skill_name}",
            ])
        else:
            recommendations.extend([
                f"Include {skill_name} in course materials",
                f"Reference {skill_name} in related content",
            ])

        return recommendations
