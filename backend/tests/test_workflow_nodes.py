"""
Tests for Workforce Alignment Workflow Nodes.

Tests for Phase 2 node implementations with service integration.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from workflows.workforce_alignment_state import WorkforceAlignmentState
from workflows.nodes import (
    extract_requirements,
    ingest_and_normalize_course_materials,
    validate_request_and_access,
)


class TestExtractRequirementsNode:
    """Tests for extract_requirements node."""

    def test_extract_requirements_success(self):
        """Test successful requirements extraction."""
        state = WorkforceAlignmentState(
            tenant_id="test-tenant",
            request_id="req-123",
            initiating_user_id="user-1",
            program_id="prog-1",
            program_name="Web Development",
            course_ids=["course-1"],
            input_package_id="pkg-1",
            input_package_format="imscc",
            input_skill_framework_id="framework-1",
        )

        with patch('workflows.nodes.RequirementsExtractionService') as mock_service:
            mock_instance = Mock()
            mock_instance.extract_requirements.return_value = Mock(
                program_name="Web Development",
                program_description="A comprehensive web development program",
                target_roles=[{"name": "Web Developer"}],
                required_skills=[{"name": "JavaScript"}],
                constraints={},
                accessibility_requirements=[],
                style_guidelines=[],
                ambiguities=[],
                confidence=0.95
            )
            mock_service.return_value = mock_instance

            result = extract_requirements(state)

            assert result.requirements_extracted
            assert result.extraction_confidence == 0.95
            assert "extract_requirements" in result.completed_nodes
            assert result.current_node == "extract_requirements"

    def test_extract_requirements_low_confidence_triggers_interrupt(self):
        """Test that low confidence triggers human interrupt."""
        state = WorkforceAlignmentState(
            tenant_id="test-tenant",
            request_id="req-123",
            initiating_user_id="user-1",
            program_id="prog-1",
            program_name="Unclear Program",
            course_ids=["course-1"],
            input_package_id="pkg-1",
            input_package_format="imscc",
            input_skill_framework_id="framework-1",
        )

        with patch('workflows.nodes.RequirementsExtractionService') as mock_service:
            mock_instance = Mock()
            mock_instance.extract_requirements.return_value = Mock(
                program_name="Unclear Program",
                program_description="Description",
                target_roles=[],
                required_skills=[],
                constraints={},
                accessibility_requirements=[],
                style_guidelines=[],
                ambiguities=[{"item": "scope", "question": "What is the scope?"}],
                confidence=0.45
            )
            mock_service.return_value = mock_instance

            result = extract_requirements(state)

            assert result.human_interrupt_pending
            assert result.current_checkpoint == "requirements_confirmation"
            assert result.extraction_confidence == 0.45

    def test_extract_requirements_error_handling(self):
        """Test error handling in requirements extraction."""
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
        )

        with patch('workflows.nodes.RequirementsExtractionService') as mock_service:
            mock_instance = Mock()
            mock_instance.extract_requirements.side_effect = Exception("API Error")
            mock_service.return_value = mock_instance

            result = extract_requirements(state)

            assert result.workflow_status == "failed"
            assert "API Error" in result.error_message


class TestIngestAndNormalizeCourseNode:
    """Tests for ingest_and_normalize_course_materials node."""

    def test_ingest_course_materials_success(self):
        """Test successful course ingestion."""
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
        )

        with patch('workflows.nodes.CourseIngestionService') as mock_service:
            mock_instance = Mock()
            mock_hierarchy = Mock()
            mock_hierarchy.course_id = "course-1"
            mock_hierarchy.course_title = "Test Course"
            mock_hierarchy.course_description = "Description"
            mock_hierarchy.modules = [{"id": "mod-1", "title": "Module 1"}]
            mock_hierarchy.objectives = ["Objective 1"]

            mock_instance.ingest_package.return_value = mock_hierarchy
            mock_instance.extract_learning_objectives.return_value = ["Objective 1"]
            mock_instance.generate_embeddings.return_value = {"item-1": [0.1] * 384}
            mock_service.return_value = mock_instance

            result = ingest_and_normalize_course_materials(state)

            assert result.course_structure_extracted
            assert result.course_hierarchy_data["course_title"] == "Test Course"
            assert len(result.extracted_learning_objectives) > 0
            assert "ingest_and_normalize_course_materials" in result.completed_nodes

    def test_ingest_course_materials_error_handling(self):
        """Test error handling in course ingestion."""
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
        )

        with patch('workflows.nodes.CourseIngestionService') as mock_service:
            mock_instance = Mock()
            mock_instance.ingest_package.side_effect = Exception("Invalid package")
            mock_service.return_value = mock_instance

            result = ingest_and_normalize_course_materials(state)

            assert result.workflow_status == "failed"
            assert "Invalid package" in result.error_message


class TestValidateRequestAndAccessNode:
    """Tests for validate_request_and_access node."""

    def test_validate_request_success(self):
        """Test successful validation."""
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
        )

        with patch('workflows.nodes.TenantContext'):
            result = validate_request_and_access(state)

            assert result.workflow_status == "pending"
            assert "validate_request_and_access" in result.completed_nodes

    def test_validate_request_missing_program_name(self):
        """Test validation fails without program name."""
        state = WorkforceAlignmentState(
            tenant_id="test-tenant",
            request_id="req-123",
            initiating_user_id="user-1",
            program_id="prog-1",
            program_name="",  # Missing
            course_ids=["course-1"],
            input_package_id="pkg-1",
            input_package_format="imscc",
            input_skill_framework_id="framework-1",
        )

        with patch('workflows.nodes.TenantContext'):
            result = validate_request_and_access(state)

            assert result.workflow_status == "failed"
            assert "required" in result.error_message.lower()

    def test_validate_request_missing_package_id(self):
        """Test validation fails without package ID."""
        state = WorkforceAlignmentState(
            tenant_id="test-tenant",
            request_id="req-123",
            initiating_user_id="user-1",
            program_id="prog-1",
            program_name="Test Program",
            course_ids=["course-1"],
            input_package_id="",  # Missing
            input_package_format="imscc",
            input_skill_framework_id="framework-1",
        )

        with patch('workflows.nodes.TenantContext'):
            result = validate_request_and_access(state)

            assert result.workflow_status == "failed"
            assert "package" in result.error_message.lower()


class TestWorkflowNodeStateTransitions:
    """Tests for workflow node state transitions."""

    def test_node_execution_updates_current_node(self):
        """Test that node execution updates current_node field."""
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
        )

        with patch('workflows.nodes.TenantContext'):
            result = validate_request_and_access(state)

            assert result.current_node == "validate_request_and_access"

    def test_node_execution_appends_to_completed_nodes(self):
        """Test that successful execution appends to completed_nodes."""
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
            completed_nodes=["previous_node"],
        )

        with patch('workflows.nodes.TenantContext'):
            result = validate_request_and_access(state)

            assert "validate_request_and_access" in result.completed_nodes
            assert "previous_node" in result.completed_nodes
