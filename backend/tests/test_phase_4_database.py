"""
Tests for Phase 4: Database Persistence and API Endpoints.

Tests for database models, persistence service, and API routes.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
import uuid

try:
    from database.models import (
        SkillAlignment, Recommendation, GapAnalysis,
        CoverageReport, AccessibilityAudit
    )
    from services.database_persistence import DatabasePersistenceService
except ImportError:
    pytest.skip("Database models not available", allow_module_level=True)


class TestDatabaseModels:
    """Tests for Phase 4 database models."""

    def test_skill_alignment_model_creation(self):
        """Test SkillAlignment model instantiation."""
        alignment = SkillAlignment(
            id=str(uuid.uuid4()),
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            skill_id="skill-python",
            skill_name="Python",
            content_id="module-1",
            content_title="Module 1: Basics",
            alignment_type="introduces",
            proficiency_level="beginner",
            confidence=0.85,
            status="candidate",
        )

        assert alignment.skill_name == "Python"
        assert alignment.confidence == 0.85
        assert alignment.status == "candidate"

    def test_recommendation_model_creation(self):
        """Test Recommendation model instantiation."""
        recommendation = Recommendation(
            id=str(uuid.uuid4()),
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            type="add_content",
            priority="critical",
            title="Add Python Module",
            description="Add foundational Python content",
            rationale="Python is critical for this program",
            estimated_effort="large",
            status="proposed",
        )

        assert recommendation.type == "add_content"
        assert recommendation.priority == "critical"
        assert recommendation.status == "proposed"

    def test_gap_analysis_model_creation(self):
        """Test GapAnalysis model instantiation."""
        gap = GapAnalysis(
            id=str(uuid.uuid4()),
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            skill_id="skill-react",
            skill_name="React",
            required_proficiency="intermediate",
            current_coverage=0.0,
            gap_severity="critical",
            gap_description="React is not covered in course",
            status="identified",
        )

        assert gap.skill_name == "React"
        assert gap.gap_severity == "critical"
        assert gap.current_coverage == 0.0

    def test_coverage_report_model_creation(self):
        """Test CoverageReport model instantiation."""
        report = CoverageReport(
            id=str(uuid.uuid4()),
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            total_skills=5,
            total_alignments=12,
            overall_coverage=0.75,
            status="generated",
        )

        assert report.total_skills == 5
        assert report.overall_coverage == 0.75

    def test_accessibility_audit_model_creation(self):
        """Test AccessibilityAudit model instantiation."""
        audit = AccessibilityAudit(
            id=str(uuid.uuid4()),
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            scope="wcag-2.1-aa",
            total_findings=3,
            critical_issues=1,
            status="completed",
        )

        assert audit.scope == "wcag-2.1-aa"
        assert audit.total_findings == 3


class TestDatabasePersistenceService:
    """Tests for DatabasePersistenceService."""

    def test_save_skill_alignments(self):
        """Test saving skill alignments to database."""
        mock_session = Mock(spec=Session)

        alignments = [
            {
                'skill_id': 'skill-1',
                'skill_name': 'Python',
                'content_id': 'module-1',
                'content_title': 'Module 1',
                'alignment_type': 'introduces',
                'proficiency_level': 'beginner',
                'confidence': 0.85,
            }
        ]

        with patch('services.database_persistence.uuid.uuid4', return_value='test-uuid'):
            ids = DatabasePersistenceService.save_skill_alignments(
                mock_session,
                "tenant-1",
                "workflow-1",
                alignments
            )

        assert len(ids) == 1
        assert mock_session.add.called
        assert mock_session.commit.called

    def test_save_recommendations(self):
        """Test saving recommendations to database."""
        mock_session = Mock(spec=Session)

        recommendations = [
            {
                'type': 'add_content',
                'priority': 'critical',
                'title': 'Add Python Module',
                'description': 'Add foundational Python content',
                'rationale': 'Critical skill gap',
                'affected_skills': ['python'],
                'estimated_effort': 'large',
            }
        ]

        with patch('services.database_persistence.uuid.uuid4', return_value='test-uuid'):
            ids = DatabasePersistenceService.save_recommendations(
                mock_session,
                "tenant-1",
                "workflow-1",
                recommendations
            )

        assert len(ids) == 1
        assert mock_session.add.called
        assert mock_session.commit.called

    def test_save_gap_analysis(self):
        """Test saving gap analysis to database."""
        mock_session = Mock(spec=Session)

        gaps = [
            {
                'skill_id': 'skill-react',
                'skill_name': 'React',
                'required_proficiency': 'intermediate',
                'current_coverage': 0.0,
                'gap_severity': 'critical',
                'gap_description': 'React not covered',
            }
        ]

        with patch('services.database_persistence.uuid.uuid4', return_value='test-uuid'):
            ids = DatabasePersistenceService.save_gap_analysis(
                mock_session,
                "tenant-1",
                "workflow-1",
                gaps
            )

        assert len(ids) == 1

    def test_save_coverage_report(self):
        """Test saving coverage report to database."""
        mock_session = Mock(spec=Session)

        coverage_data = {
            'total_skills': 5,
            'total_alignments': 12,
            'overall_coverage': 0.75,
            'covered_skills': ['python', 'javascript'],
            'uncovered_skills': ['react'],
        }

        with patch('services.database_persistence.uuid.uuid4', return_value='test-uuid'):
            report_id = DatabasePersistenceService.save_coverage_report(
                mock_session,
                "tenant-1",
                "workflow-1",
                coverage_data
            )

        assert report_id is not None
        assert mock_session.add.called

    def test_save_accessibility_audit(self):
        """Test saving accessibility audit to database."""
        mock_session = Mock(spec=Session)

        audit_data = {
            'scope': 'wcag-2.1-aa',
            'total_findings': 3,
            'critical_issues': 1,
            'findings': [
                {'type': 'missing_alt_text', 'severity': 'critical'}
            ],
        }

        with patch('services.database_persistence.uuid.uuid4', return_value='test-uuid'):
            audit_id = DatabasePersistenceService.save_accessibility_audit(
                mock_session,
                "tenant-1",
                "workflow-1",
                audit_data
            )

        assert audit_id is not None

    def test_approve_alignment(self):
        """Test approving a skill alignment."""
        mock_session = Mock(spec=Session)
        mock_alignment = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_alignment

        result = DatabasePersistenceService.approve_alignment(
            mock_session,
            "alignment-1",
            "user-1",
            "Approved"
        )

        assert result is True
        assert mock_alignment.status == "approved"
        assert mock_session.commit.called

    def test_approve_recommendation(self):
        """Test approving a recommendation."""
        mock_session = Mock(spec=Session)
        mock_rec = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_rec

        result = DatabasePersistenceService.approve_recommendation(
            mock_session,
            "recommendation-1",
            "user-1",
            "Approved"
        )

        assert result is True
        assert mock_rec.status == "approved"
        assert mock_session.commit.called


class TestPhase4ModelIntegration:
    """Integration tests for Phase 4 models."""

    def test_skill_alignment_with_evidence(self):
        """Test SkillAlignment with evidence tracking."""
        alignment = SkillAlignment(
            id=str(uuid.uuid4()),
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            skill_id="skill-python",
            skill_name="Python",
            content_id="module-1",
            content_title="Module 1",
            alignment_type="introduces",
            proficiency_level="beginner",
            confidence=0.85,
            evidence=[
                {"quote": "Python is introduced in lesson 1", "reference": "Module 1, Lesson 1"},
            ],
            supporting_objectives=["Understand Python syntax"],
        )

        assert len(alignment.evidence) == 1
        assert len(alignment.supporting_objectives) == 1

    def test_recommendation_with_implementation_steps(self):
        """Test Recommendation with detailed implementation guidance."""
        recommendation = Recommendation(
            id=str(uuid.uuid4()),
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            type="add_content",
            priority="critical",
            title="Add Python Module",
            description="Add foundational Python content",
            rationale="Critical gap in Python coverage",
            implementation_steps=[
                "Create Python basics module",
                "Add practice exercises",
                "Add assessment items",
            ],
            affected_skills=["python"],
            estimated_effort="large",
            expected_impact="Close critical Python gap",
        )

        assert len(recommendation.implementation_steps) == 3
        assert recommendation.affected_skills == ["python"]
