"""
Tests for Recommendations Service.

Tests for curriculum improvement recommendations generation.
"""

import pytest
from unittest.mock import Mock, patch
import sys

try:
    from services.recommendations import (
        RecommendationsService,
        RecommendationsResult,
        RecommendationType,
        RecommendationPriority,
    )
except ImportError:
    pytest.skip("langchain_anthropic not installed", allow_module_level=True)


class TestRecommendationsService:
    """Tests for RecommendationsService."""

    def test_service_initialization(self):
        """Test service initializes correctly."""
        service = RecommendationsService()
        assert service.model == "claude-opus-5-5"
        assert service.client is not None

    def test_recommendation_type_enum(self):
        """Test RecommendationType enum values."""
        assert RecommendationType.ADD_CONTENT.value == "add_content"
        assert RecommendationType.ENHANCE_ASSESSMENT.value == "enhance_assessment"
        assert RecommendationType.ADD_PRACTICE.value == "add_practice"

    def test_recommendation_priority_enum(self):
        """Test RecommendationPriority enum values."""
        assert RecommendationPriority.CRITICAL.value == "critical"
        assert RecommendationPriority.HIGH.value == "high"
        assert RecommendationPriority.MEDIUM.value == "medium"
        assert RecommendationPriority.LOW.value == "low"

    def test_priority_ordering(self):
        """Test priority sort ordering."""
        service = RecommendationsService()

        assert service._priority_order('critical') < service._priority_order('high')
        assert service._priority_order('high') < service._priority_order('medium')
        assert service._priority_order('medium') < service._priority_order('low')

    def test_count_by_type(self):
        """Test counting recommendations by type."""
        service = RecommendationsService()

        recommendations = [
            {'type': 'add_content', 'priority': 'critical'},
            {'type': 'add_content', 'priority': 'high'},
            {'type': 'add_practice', 'priority': 'medium'},
            {'type': 'enhance_assessment', 'priority': 'low'},
        ]

        counts = service._count_by_type(recommendations)

        assert counts['add_content'] == 2
        assert counts['add_practice'] == 1
        assert counts['enhance_assessment'] == 1

    def test_estimate_total_effort(self):
        """Test total effort estimation."""
        service = RecommendationsService()

        small_effort = [
            {'estimated_effort': 'small'},
            {'estimated_effort': 'small'},
        ]
        assert service._estimate_total_effort(small_effort) == 'small'

        large_effort = [
            {'estimated_effort': 'large'},
            {'estimated_effort': 'large'},
        ]
        assert service._estimate_total_effort(large_effort) == 'large'

        mixed_effort = [
            {'estimated_effort': 'small'},
            {'estimated_effort': 'medium'},
            {'estimated_effort': 'large'},
        ]
        assert service._estimate_total_effort(mixed_effort) == 'medium'

    def test_prioritize_recommendations(self):
        """Test recommendation prioritization."""
        service = RecommendationsService()

        recommendations = [
            {'title': 'Low', 'priority': 'low'},
            {'title': 'Critical', 'priority': 'critical'},
            {'title': 'High', 'priority': 'high'},
        ]

        prioritized = service._prioritize_recommendations(recommendations)

        assert prioritized[0]['title'] == 'Critical'
        assert prioritized[1]['title'] == 'High'
        assert prioritized[2]['title'] == 'Low'

    def test_generate_gap_content_recommendations_critical(self):
        """Test content recommendations for critical gaps."""
        service = RecommendationsService()

        recommendations = service.generate_gap_content_recommendations(
            skill_name="Python Programming",
            gap_severity="critical",
            proficiency_level="intermediate",
            course_context="Computer Science"
        )

        assert len(recommendations) >= 3
        assert any("foundational" in r.lower() for r in recommendations)

    def test_generate_gap_content_recommendations_high(self):
        """Test content recommendations for high-priority gaps."""
        service = RecommendationsService()

        recommendations = service.generate_gap_content_recommendations(
            skill_name="JavaScript",
            gap_severity="high",
            proficiency_level="intermediate",
            course_context="Web Development"
        )

        assert len(recommendations) >= 2

    def test_generate_gap_content_recommendations_low(self):
        """Test content recommendations for low-priority gaps."""
        service = RecommendationsService()

        recommendations = service.generate_gap_content_recommendations(
            skill_name="CSS",
            gap_severity="low",
            proficiency_level="beginner",
            course_context="Web Development"
        )

        assert len(recommendations) >= 1

    def test_recommendations_result_structure(self):
        """Test RecommendationsResult structure."""
        result = RecommendationsResult(
            total_recommendations=10,
            critical_recommendations=[
                {'id': 'rec1', 'title': 'Add Python module', 'priority': 'critical'}
            ],
            high_priority_recommendations=[],
            medium_priority_recommendations=[],
            low_priority_recommendations=[],
            recommendations_by_type={'add_content': 3, 'add_practice': 2},
            estimated_total_effort='medium',
            recommendations_metadata={'model': 'claude-opus-5-5'}
        )

        assert result.total_recommendations == 10
        assert len(result.critical_recommendations) == 1
        assert result.estimated_total_effort == 'medium'


class TestRecommendationsIntegration:
    """Integration tests for recommendations."""

    def test_recommendations_workflow_state_integration(self):
        """Test that recommendations integrate with workflow state."""
        from workflows.workforce_alignment_state import WorkforceAlignmentState

        state = WorkforceAlignmentState(
            tenant_id="test-tenant",
            request_id="req-123",
            initiating_user_id="user-1",
            program_id="prog-1",
            program_name="Test Program",
            course_ids=["course-1"],
            input_package_id="pkg-1",
            input_package_format="imscc",
            input_skill_framework_id="framework-1",
            recommendations_generated=True,
            recommendations=[
                {
                    'id': 'rec-1',
                    'type': 'add_content',
                    'priority': 'critical',
                    'title': 'Add Python module',
                    'description': 'Add foundational Python content',
                    'affected_skills': ['python']
                }
            ]
        )

        assert state.recommendations_generated
        assert len(state.recommendations) == 1
        assert state.recommendations[0]['priority'] == 'critical'


class TestRecommendationGrouping:
    """Tests for recommendation grouping by priority."""

    def test_group_critical_recommendations(self):
        """Test grouping of critical recommendations."""
        service = RecommendationsService()

        recommendations = [
            {'title': 'Add Python', 'priority': 'critical'},
            {'title': 'Add JS', 'priority': 'critical'},
            {'title': 'Improve layout', 'priority': 'medium'},
        ]

        prioritized = service._prioritize_recommendations(recommendations)

        critical = [r for r in prioritized if r['priority'] == 'critical']
        assert len(critical) == 2

    def test_empty_recommendations_handling(self):
        """Test handling of empty recommendations list."""
        service = RecommendationsService()

        assert service._estimate_total_effort([]) == 'small'
        assert service._count_by_type([]) == {}


class TestRecommendationValidation:
    """Tests for recommendation validation."""

    def test_prioritize_invalid_priorities(self):
        """Test handling of invalid priority values."""
        service = RecommendationsService()

        recommendations = [
            {'title': 'Rec 1', 'priority': 'invalid'},
            {'title': 'Rec 2'},  # Missing priority
        ]

        prioritized = service._prioritize_recommendations(recommendations)

        # Invalid and missing priorities should default to 'medium'
        assert all(r['priority'] in ['critical', 'high', 'medium', 'low'] for r in prioritized)
