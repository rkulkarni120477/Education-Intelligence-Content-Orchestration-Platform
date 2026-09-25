"""
Tests for Skill Mapping Service.

Tests for skill-to-content alignment, coverage calculation, and gap analysis.
"""

import pytest
from unittest.mock import Mock, patch
import sys

try:
    from services.skill_mapping import (
        SkillMappingService,
        SkillAlignment,
        SkillMappingResult,
    )
except ImportError:
    pytest.skip("langchain_anthropic not installed", allow_module_level=True)


class TestSkillMappingService:
    """Tests for SkillMappingService."""

    def test_service_initialization(self):
        """Test service initializes correctly."""
        service = SkillMappingService()
        assert service.model == "claude-opus-5-5"
        assert service.client is not None

    def test_skill_alignment_structure(self):
        """Test SkillAlignment dataclass."""
        alignment = SkillAlignment(
            skill_name="Python",
            skill_id="skill-python",
            content_id="module-1",
            content_title="Module 1: Basics",
            alignment_type="introduces",
            proficiency_level="beginner",
            confidence=0.85,
            evidence=["Python is introduced in lesson 1"],
            supporting_objectives=["Understand Python syntax"]
        )

        assert alignment.skill_name == "Python"
        assert alignment.confidence == 0.85
        assert len(alignment.evidence) == 1

    def test_coverage_calculation(self):
        """Test coverage calculation."""
        service = SkillMappingService()

        alignments = [
            SkillAlignment("Python", "py", "m1", "M1", "introduces", "beginner", 0.8, [], []),
            SkillAlignment("Python", "py", "m2", "M2", "reinforces", "intermediate", 0.9, [], []),
            SkillAlignment("JavaScript", "js", "m3", "M3", "introduces", "beginner", 0.6, [], []),
        ]

        required_skills = [
            {'name': 'Python', 'id': 'py'},
            {'name': 'JavaScript', 'id': 'js'},
        ]

        coverage = service._calculate_coverage(alignments, required_skills)

        assert 'py' in coverage
        assert 'js' in coverage
        assert coverage['py'] > 0.7
        assert coverage['js'] == 0.6

    def test_gap_identification(self):
        """Test gap identification."""
        service = SkillMappingService()

        coverage = {
            'py': 0.8,   # Covered
            'js': 0.4,   # Partial
            'java': 0.0,  # Uncovered
        }

        required_skills = [
            {'name': 'Python', 'id': 'py'},
            {'name': 'JavaScript', 'id': 'js'},
            {'name': 'Java', 'id': 'java', 'level': 'intermediate'},
        ]

        gaps = service._identify_gaps(required_skills, coverage)

        assert len(gaps) == 2  # JS and Java have gaps
        critical_gaps = [g for g in gaps if g['gap_severity'] == 'critical']
        assert len(critical_gaps) == 1  # Java is critical

    def test_gap_severity_determination(self):
        """Test gap severity classification."""
        service = SkillMappingService()

        assert service._determine_gap_severity(0.0) == 'critical'
        assert service._determine_gap_severity(0.2) == 'high'
        assert service._determine_gap_severity(0.5) == 'medium'
        assert service._determine_gap_severity(0.7) == 'low'

    def test_overall_coverage_calculation(self):
        """Test overall coverage calculation."""
        service = SkillMappingService()

        coverage = {
            'skill1': 0.8,
            'skill2': 0.6,
            'skill3': 0.9,
        }

        overall = service._calculate_overall_coverage(coverage)

        assert overall == pytest.approx(0.7667, rel=1e-3)

    def test_get_covered_skills(self):
        """Test getting covered skills."""
        service = SkillMappingService()

        coverage = {
            'skill1': 0.9,
            'skill2': 0.5,
            'skill3': 0.85,
        }

        covered = service._get_covered_skills(coverage, threshold=0.8)

        assert 'skill1' in covered
        assert 'skill3' in covered
        assert 'skill2' not in covered

    def test_skill_mapping_result_structure(self):
        """Test SkillMappingResult structure."""
        result = SkillMappingResult(
            total_skills=5,
            total_content_items=20,
            total_alignments=15,
            coverage_by_skill={'skill1': 0.8, 'skill2': 0.6},
            covered_skills=['skill1'],
            partially_covered_skills=['skill2'],
            uncovered_skills=[],
            overall_coverage=0.7,
            critical_gaps=[],
            alignment_confidence=0.82,
            mapping_metadata={'model': 'claude-opus-5-5'}
        )

        assert result.total_skills == 5
        assert result.overall_coverage == 0.7
        assert result.alignment_confidence == 0.82

    def test_map_skills_to_content_with_empty_inputs(self):
        """Test mapping with empty inputs."""
        service = SkillMappingService()

        with patch.object(service, '_identify_alignments_with_claude', return_value=[]):
            result = service.map_skills_to_content(
                course_title="Test Course",
                course_objectives=[],
                course_content=[],
                required_skills=[],
            )

            assert result.total_skills == 0
            assert result.total_alignments == 0
            assert result.overall_coverage == 0.0


class TestSkillMappingIntegration:
    """Integration tests for skill mapping."""

    def test_skill_mapping_workflow_state_integration(self):
        """Test that mapping results integrate with workflow state."""
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
            skill_mappings_generated=True,
            coverage_by_skill={'skill1': 0.8, 'skill2': 0.5},
            total_alignments=10,
            overall_coverage_percentage=0.65,
            covered_skills=['skill1'],
            uncovered_skills=['skill3'],
        )

        assert state.skill_mappings_generated
        assert state.overall_coverage_percentage == 0.65
        assert len(state.covered_skills) == 1


class TestSkillAlignmentTypes:
    """Tests for skill alignment type validation."""

    def test_valid_alignment_types(self):
        """Test valid alignment types."""
        valid_types = ['introduces', 'reinforces', 'assesses', 'covers']

        for alignment_type in valid_types:
            alignment = SkillAlignment(
                skill_name="Test",
                skill_id="test",
                content_id="c1",
                content_title="Content",
                alignment_type=alignment_type,
                proficiency_level="intermediate",
                confidence=0.8,
                evidence=[],
                supporting_objectives=[]
            )
            assert alignment.alignment_type == alignment_type

    def test_proficiency_levels(self):
        """Test proficiency level assignments."""
        levels = ['beginner', 'intermediate', 'advanced', 'expert']

        for level in levels:
            alignment = SkillAlignment(
                skill_name="Test",
                skill_id="test",
                content_id="c1",
                content_title="Content",
                alignment_type="introduces",
                proficiency_level=level,
                confidence=0.8,
                evidence=[],
                supporting_objectives=[]
            )
            assert alignment.proficiency_level == level
