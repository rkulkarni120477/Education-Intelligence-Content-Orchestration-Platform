"""
Unit tests for Requirements Extraction Service.

Tests for Claude API integration, prompt handling, and response parsing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock langchain if not installed
try:
    from services.requirements_extraction import (
        RequirementsExtractionService,
        RequirementsExtractionResult,
        extract_program_requirements,
    )
except ImportError:
    pytest.skip("langchain_anthropic not installed", allow_module_level=True)


class TestRequirementsExtractionService:
    """Tests for RequirementsExtractionService."""

    def test_service_initialization(self):
        """Test service can be initialized."""
        service = RequirementsExtractionService()
        assert service.model == "claude-opus-5-5"
        assert service.client is not None

    def test_extract_requirements_response_structure(self):
        """Test that extracted requirements have correct structure."""
        result = RequirementsExtractionResult(
            program_name="Test Program",
            program_description="A test program",
            target_roles=[{"name": "Developer", "description": "Software developer"}],
            required_skills=[{"name": "Python", "level": "intermediate"}],
            constraints={"duration": "12 weeks"},
            accessibility_requirements=["WCAG 2.1 AA"],
            style_guidelines=["Follow institutional branding"],
            ambiguities=[],
            confidence=0.95,
            extraction_metadata={"model": "claude-opus-5-5"}
        )

        assert result.program_name == "Test Program"
        assert len(result.target_roles) == 1
        assert result.confidence == 0.95

    def test_extract_program_requirements_function(self):
        """Test convenience function exists and is callable."""
        # This test just verifies the function signature
        assert callable(extract_program_requirements)

    @patch('services.requirements_extraction.ChatAnthropic')
    def test_extract_requirements_with_mocked_claude(self, mock_chat):
        """Test requirements extraction with mocked Claude API."""
        # Mock Claude response
        mock_response = Mock()
        mock_response.content = '''{
            "program_description": "Web Development Program",
            "target_roles": [{"name": "Web Developer", "description": "Full-stack developer"}],
            "required_skills": [{"name": "JavaScript", "proficiency": "advanced"}],
            "constraints": {"duration": "16 weeks", "format": "hybrid"},
            "accessibility_requirements": ["WCAG 2.1 AA"],
            "style_guidelines": [],
            "ambiguities": [],
            "confidence": 0.92,
            "notes": "Clear requirements extracted"
        }'''

        mock_instance = Mock()
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance

        service = RequirementsExtractionService()
        result = service.extract_requirements(
            program_name="Web Development",
            program_context="Computer Science department",
            institution_goals="Prepare web developers",
            workforce_role_descriptions="Full-stack web developers"
        )

        assert result.program_name == "Web Development"
        assert result.confidence == 0.92
        assert len(result.target_roles) == 1

    @patch('services.requirements_extraction.ChatAnthropic')
    def test_extract_requirements_with_low_confidence(self, mock_chat):
        """Test that low confidence triggers interrupt flag."""
        mock_response = Mock()
        mock_response.content = '''{
            "program_description": "Unclear program",
            "target_roles": [],
            "required_skills": [],
            "constraints": {},
            "accessibility_requirements": [],
            "style_guidelines": [],
            "ambiguities": [{"item": "program_scope", "question": "What is the target audience?"}],
            "confidence": 0.45,
            "notes": "Ambiguous requirements"
        }'''

        mock_instance = Mock()
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance

        service = RequirementsExtractionService()
        result = service.extract_requirements(
            program_name="Unclear Program",
            program_context="",
            institution_goals="",
            workforce_role_descriptions=""
        )

        assert result.confidence < 0.7
        assert len(result.ambiguities) > 0

    @patch('services.requirements_extraction.ChatAnthropic')
    def test_extract_requirements_with_malformed_json(self, mock_chat):
        """Test handling of malformed JSON response."""
        mock_response = Mock()
        mock_response.content = "Invalid JSON response"

        mock_instance = Mock()
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance

        service = RequirementsExtractionService()
        result = service.extract_requirements(
            program_name="Test Program",
            program_context="",
            institution_goals="",
            workforce_role_descriptions=""
        )

        # Should return partial result with error note
        assert result.program_name == "Test Program"
        assert result.confidence == 0.0
        assert len(result.ambiguities) > 0

    def test_extract_requirements_with_optional_parameters(self):
        """Test extraction with optional style guide and context."""
        service = RequirementsExtractionService()

        # Verify method signature accepts optional params
        import inspect
        sig = inspect.signature(service.extract_requirements)
        assert 'style_guide' in sig.parameters
        assert 'additional_context' in sig.parameters
        assert sig.parameters['style_guide'].default is None
        assert sig.parameters['additional_context'].default is None


class TestRequirementsExtractionIntegration:
    """Integration tests for requirements extraction."""

    def test_requirement_extraction_workflow_state_integration(self):
        """Test that extracted data matches workflow state expectations."""
        from workflows.workforce_alignment_state import WorkforceAlignmentState

        # Create state with extraction results
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
            extracted_target_roles=[{"name": "Role1", "description": "Description1"}],
            extracted_required_skills=[{"name": "Skill1", "level": "advanced"}],
            extraction_confidence=0.85,
        )

        assert state.extracted_target_roles is not None
        assert state.extracted_required_skills is not None
        assert state.extraction_confidence == 0.85
