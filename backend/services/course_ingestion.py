"""
Course Package Ingestion Service.

Parses course packages (IMSCC, ZIP, upload) and extracts hierarchy,
metadata, and learning objectives. Generates embeddings for semantic search.
"""

from typing import Dict, List, Any, Optional, Tuple
import zipfile
import json
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PackageFormat(str, Enum):
    """Supported course package formats."""
    IMSCC = "imscc"  # IMS Common Cartridge
    ZIP = "zip"      # Generic ZIP archive
    UPLOAD = "upload"  # Direct upload


@dataclass
class ContentMetadata:
    """Metadata extracted from course content."""
    title: str
    description: Optional[str]
    learning_objectives: List[str]
    type: str  # course, module, lesson, activity, assessment
    hierarchy_level: int
    duration_hours: Optional[float] = None
    audience: Optional[str] = None


@dataclass
class CourseHierarchy:
    """Hierarchical representation of course structure."""
    course_id: str
    course_title: str
    course_description: Optional[str]
    modules: List[Dict[str, Any]]  # {id, title, lessons: [...]}
    objectives: List[str]
    metadata: Dict[str, Any]


class CourseIngestionService:
    """Service for ingesting and parsing course packages."""

    def __init__(self):
        """Initialize the service."""
        self.supported_formats = [PackageFormat.IMSCC, PackageFormat.ZIP, PackageFormat.UPLOAD]

    def ingest_package(
        self,
        package_path: str,
        package_format: str,
    ) -> CourseHierarchy:
        """
        Ingest a course package and extract hierarchy.

        Args:
            package_path: Path to the package file
            package_format: Format identifier (imscc, zip, upload)

        Returns:
            CourseHierarchy with extracted structure
        """
        try:
            logger.info(f"Ingesting course package: {package_path} (format: {package_format})")

            # Validate format
            if package_format not in [f.value for f in PackageFormat]:
                raise ValueError(f"Unsupported format: {package_format}")

            # Route to appropriate handler
            if package_format == PackageFormat.IMSCC.value:
                hierarchy = self._parse_imscc(package_path)
            elif package_format == PackageFormat.ZIP.value:
                hierarchy = self._parse_zip(package_path)
            else:  # upload
                hierarchy = self._parse_upload(package_path)

            logger.info(f"✓ Package ingested: {hierarchy.course_title} ({len(hierarchy.modules)} modules)")
            return hierarchy

        except Exception as e:
            logger.error(f"Package ingestion failed: {str(e)}")
            raise

    def _parse_imscc(self, package_path: str) -> CourseHierarchy:
        """
        Parse IMS Common Cartridge format.

        Common Cartridge is a standard ZIP containing:
        - imsmanifest.xml (course structure and metadata)
        - Various resource files (HTML, PDF, etc.)
        """
        try:
            logger.info(f"Parsing IMSCC package: {package_path}")

            with zipfile.ZipFile(package_path, 'r') as zip_file:
                # Read manifest
                manifest_xml = zip_file.read('imsmanifest.xml').decode('utf-8')
                manifest = ET.fromstring(manifest_xml)

                # Extract basic structure
                hierarchy = self._extract_imscc_structure(manifest, zip_file, package_path)

            return hierarchy

        except zipfile.BadZipFile:
            logger.error("Invalid ZIP file format")
            raise ValueError("Invalid IMSCC file: not a valid ZIP archive")
        except FileNotFoundError:
            logger.error("imsmanifest.xml not found in IMSCC package")
            raise ValueError("Invalid IMSCC file: missing imsmanifest.xml")

    def _extract_imscc_structure(
        self,
        manifest: ET.Element,
        zip_file: zipfile.ZipFile,
        package_path: str,
    ) -> CourseHierarchy:
        """Extract course structure from IMSCC manifest."""

        # Parse course metadata from organizations section
        org = manifest.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imsccmanifest.xsd}organization')

        course_title = org.get('title', 'Imported Course') if org is not None else 'Imported Course'
        course_id = str(Path(package_path).stem)

        modules = []

        # Parse items (units/modules)
        if org is not None:
            items = org.findall('.//{http://www.imsglobal.org/xsd/imsccv1p1/imsccmanifest.xsd}item')
            for item in items:
                module_data = {
                    'id': item.get('identifier', ''),
                    'title': item.get('title', 'Untitled Module'),
                    'lessons': self._extract_imscc_items(item),
                }
                modules.append(module_data)

        return CourseHierarchy(
            course_id=course_id,
            course_title=course_title,
            course_description="Imported from IMSCC package",
            modules=modules,
            objectives=[],
            metadata={
                'source_format': 'imscc',
                'package_path': str(package_path),
                'total_items': len(modules),
            }
        )

    def _extract_imscc_items(self, item: ET.Element) -> List[Dict[str, Any]]:
        """Extract lesson/content items from IMSCC item element."""
        lessons = []

        # Recursively extract sub-items
        sub_items = item.findall('.//{http://www.imsglobal.org/xsd/imsccv1p1/imsccmanifest.xsd}item')

        for sub_item in sub_items:
            lesson = {
                'id': sub_item.get('identifier', ''),
                'title': sub_item.get('title', 'Untitled Lesson'),
                'type': 'lesson',
            }
            lessons.append(lesson)

        return lessons

    def _parse_zip(self, package_path: str) -> CourseHierarchy:
        """
        Parse generic ZIP package containing course materials.

        Expected structure:
        - index.html or README.md (course metadata)
        - modules/ subdirectory with lessons
        - assets/ subdirectory with resources
        """
        try:
            logger.info(f"Parsing ZIP package: {package_path}")

            course_id = str(Path(package_path).stem)
            modules = []

            with zipfile.ZipFile(package_path, 'r') as zip_file:
                # List all files to understand structure
                file_list = zip_file.namelist()

                # Try to find course metadata
                course_title = course_id
                course_description = None

                if 'README.md' in file_list:
                    readme = zip_file.read('README.md').decode('utf-8', errors='ignore')
                    lines = readme.split('\n')
                    if lines:
                        course_title = lines[0].replace('#', '').strip()
                        course_description = '\n'.join(lines[1:10])

                # Look for modules subdirectory
                module_files = [f for f in file_list if f.startswith('modules/') and f.endswith('.html')]

                for module_file in module_files:
                    module_id = Path(module_file).stem
                    module_data = {
                        'id': module_id,
                        'title': module_id.replace('-', ' ').title(),
                        'lessons': [{
                            'id': module_id,
                            'title': module_id.replace('-', ' ').title(),
                            'type': 'lesson',
                        }],
                    }
                    modules.append(module_data)

            return CourseHierarchy(
                course_id=course_id,
                course_title=course_title,
                course_description=course_description,
                modules=modules,
                objectives=[],
                metadata={
                    'source_format': 'zip',
                    'package_path': str(package_path),
                    'total_items': len(modules),
                }
            )

        except zipfile.BadZipFile:
            logger.error("Invalid ZIP file")
            raise ValueError("Invalid ZIP file")

    def _parse_upload(self, package_path: str) -> CourseHierarchy:
        """
        Parse uploaded course package (JSON metadata format).

        Expected format:
        {
          "course": {"id": "...", "title": "...", "description": "..."},
          "modules": [{"id": "...", "title": "...", "lessons": [...]}]
        }
        """
        try:
            logger.info(f"Parsing upload package: {package_path}")

            with open(package_path, 'r') as f:
                data = json.load(f)

            course_info = data.get('course', {})
            course_id = course_info.get('id', str(Path(package_path).stem))
            course_title = course_info.get('title', 'Imported Course')
            course_description = course_info.get('description')
            modules = data.get('modules', [])

            return CourseHierarchy(
                course_id=course_id,
                course_title=course_title,
                course_description=course_description,
                modules=modules,
                objectives=data.get('objectives', []),
                metadata={
                    'source_format': 'upload',
                    'package_path': str(package_path),
                    'total_items': len(modules),
                }
            )

        except json.JSONDecodeError:
            logger.error("Invalid JSON in upload package")
            raise ValueError("Invalid upload package: not valid JSON")
        except FileNotFoundError:
            logger.error("Upload file not found")
            raise

    def extract_learning_objectives(
        self,
        hierarchy: CourseHierarchy,
    ) -> List[str]:
        """
        Extract learning objectives from course hierarchy.

        Args:
            hierarchy: CourseHierarchy from ingestion

        Returns:
            List of extracted objectives
        """
        objectives = []

        # From explicit objectives
        objectives.extend(hierarchy.objectives)

        # From module titles (heuristic)
        for module in hierarchy.modules:
            if 'By the end of' in module.get('title', ''):
                objectives.append(module['title'])

        logger.info(f"Extracted {len(objectives)} learning objectives")
        return objectives

    def generate_embeddings(
        self,
        hierarchy: CourseHierarchy,
    ) -> Dict[str, List[float]]:
        """
        Generate embeddings for course content.

        In Phase 2, this would use ChromaDB or similar.
        For now, returns a stub structure.

        Args:
            hierarchy: CourseHierarchy from ingestion

        Returns:
            Dict mapping content IDs to embeddings
        """
        embeddings = {}

        # Stub: In Phase 2, would call embedding model
        for module in hierarchy.modules:
            embedding_id = f"module_{module['id']}"
            embeddings[embedding_id] = [0.0] * 384  # Placeholder 384-dim embedding

        logger.info(f"Generated embeddings for {len(embeddings)} content items")
        return embeddings
