"""
Unit tests for Course Ingestion Service.

Tests for package parsing, hierarchy extraction, and embedding generation.
"""

import pytest
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch
from services.course_ingestion import (
    CourseIngestionService,
    CourseHierarchy,
    PackageFormat,
    ContentMetadata,
)


class TestCourseIngestionService:
    """Tests for CourseIngestionService."""

    def test_service_initialization(self):
        """Test service initializes correctly."""
        service = CourseIngestionService()
        assert service.supported_formats == [PackageFormat.IMSCC, PackageFormat.ZIP, PackageFormat.UPLOAD]

    def test_package_format_enum(self):
        """Test PackageFormat enum values."""
        assert PackageFormat.IMSCC.value == "imscc"
        assert PackageFormat.ZIP.value == "zip"
        assert PackageFormat.UPLOAD.value == "upload"

    def test_ingest_unsupported_format(self):
        """Test error handling for unsupported formats."""
        service = CourseIngestionService()

        with pytest.raises(ValueError, match="Unsupported format"):
            service.ingest_package(
                package_path="/tmp/test.pkg",
                package_format="unsupported"
            )

    def test_parse_upload_format(self):
        """Test parsing upload format with JSON metadata."""
        service = CourseIngestionService()

        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            upload_data = {
                "course": {
                    "id": "course-123",
                    "title": "Advanced Python",
                    "description": "Learn advanced Python concepts"
                },
                "modules": [
                    {
                        "id": "module-1",
                        "title": "Decorators and Metaclasses",
                        "lessons": [
                            {"id": "lesson-1", "title": "Decorators", "type": "lesson"},
                            {"id": "lesson-2", "title": "Metaclasses", "type": "lesson"}
                        ]
                    }
                ],
                "objectives": [
                    "Understand decorators",
                    "Master metaclasses"
                ]
            }
            json.dump(upload_data, f)
            temp_path = f.name

        try:
            hierarchy = service.ingest_package(
                package_path=temp_path,
                package_format=PackageFormat.UPLOAD.value
            )

            assert hierarchy.course_id == "course-123"
            assert hierarchy.course_title == "Advanced Python"
            assert len(hierarchy.modules) == 1
            assert len(hierarchy.objectives) == 2
        finally:
            Path(temp_path).unlink()

    def test_parse_upload_invalid_json(self):
        """Test error handling for invalid JSON upload."""
        service = CourseIngestionService()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {]")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid upload package"):
                service.ingest_package(
                    package_path=temp_path,
                    package_format=PackageFormat.UPLOAD.value
                )
        finally:
            Path(temp_path).unlink()

    def test_extract_learning_objectives(self):
        """Test learning objective extraction."""
        service = CourseIngestionService()

        hierarchy = CourseHierarchy(
            course_id="course-1",
            course_title="Test Course",
            course_description="Description",
            modules=[
                {
                    "id": "mod-1",
                    "title": "By the end of this module, students will understand...",
                    "lessons": []
                }
            ],
            objectives=["Objective 1", "Objective 2"],
            metadata={}
        )

        objectives = service.extract_learning_objectives(hierarchy)

        assert len(objectives) >= 2
        assert "Objective 1" in objectives

    def test_generate_embeddings(self):
        """Test embedding generation."""
        service = CourseIngestionService()

        hierarchy = CourseHierarchy(
            course_id="course-1",
            course_title="Test Course",
            course_description="Description",
            modules=[
                {"id": "mod-1", "title": "Module 1", "lessons": []},
                {"id": "mod-2", "title": "Module 2", "lessons": []}
            ],
            objectives=[],
            metadata={}
        )

        embeddings = service.generate_embeddings(hierarchy)

        assert "module_mod-1" in embeddings
        assert "module_mod-2" in embeddings
        assert len(embeddings["module_mod-1"]) == 384

    def test_create_zip_package(self):
        """Test parsing of ZIP format packages."""
        service = CourseIngestionService()

        # Create temporary ZIP file
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create README
            readme_path = Path(tmpdir) / "README.md"
            readme_path.write_text("# Test Course\nDescription of the course")

            # Create modules directory
            modules_dir = Path(tmpdir) / "modules"
            modules_dir.mkdir()
            (modules_dir / "module-1.html").write_text("<html>Module 1</html>")
            (modules_dir / "module-2.html").write_text("<html>Module 2</html>")

            # Create ZIP
            zip_path = Path(tmpdir) / "package.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.write(readme_path, "README.md")
                zf.write(modules_dir / "module-1.html", "modules/module-1.html")
                zf.write(modules_dir / "module-2.html", "modules/module-2.html")

            # Parse
            hierarchy = service.ingest_package(
                package_path=str(zip_path),
                package_format=PackageFormat.ZIP.value
            )

            assert hierarchy.course_title == "Test Course"
            assert len(hierarchy.modules) >= 2

    def test_course_hierarchy_structure(self):
        """Test CourseHierarchy data structure."""
        hierarchy = CourseHierarchy(
            course_id="cs-101",
            course_title="Introduction to Programming",
            course_description="Learn programming basics",
            modules=[
                {
                    "id": "mod-1",
                    "title": "Variables and Data Types",
                    "lessons": [
                        {"id": "les-1", "title": "Lesson 1", "type": "lesson"}
                    ]
                }
            ],
            objectives=["Learn Python basics"],
            metadata={"source_format": "imscc", "version": "1.0"}
        )

        assert hierarchy.course_id == "cs-101"
        assert hierarchy.course_title == "Introduction to Programming"
        assert len(hierarchy.modules) == 1
        assert hierarchy.metadata["source_format"] == "imscc"


class TestContentMetadata:
    """Tests for ContentMetadata."""

    def test_content_metadata_creation(self):
        """Test ContentMetadata dataclass."""
        metadata = ContentMetadata(
            title="Lesson 1",
            description="Introduction to variables",
            learning_objectives=["Understand variables"],
            type="lesson",
            hierarchy_level=2,
            duration_hours=1.5,
            audience="Beginners"
        )

        assert metadata.title == "Lesson 1"
        assert metadata.hierarchy_level == 2
        assert metadata.duration_hours == 1.5


class TestCourseIngestionIntegration:
    """Integration tests for course ingestion."""

    def test_course_ingestion_workflow_state_integration(self):
        """Test that ingested data matches workflow state expectations."""
        from workflows.workforce_alignment_state import WorkforceAlignmentState

        hierarchy_data = {
            "course_id": "course-1",
            "course_title": "Test Course",
            "modules": [
                {"id": "mod-1", "title": "Module 1"}
            ]
        }

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
            course_structure_extracted=True,
            course_hierarchy_data=hierarchy_data,
            extracted_learning_objectives=["Objective 1"],
            content_embeddings={"item-1": [0.1] * 384}
        )

        assert state.course_structure_extracted
        assert state.course_hierarchy_data["course_title"] == "Test Course"
        assert len(state.extracted_learning_objectives) > 0
