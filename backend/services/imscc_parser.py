"""
IMSCC File Parser Service
Parses IMS Content Package files and extracts course structure and content.
"""

import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CourseModule:
    """Represents a course module"""
    identifier: str
    title: str
    description: str
    learning_outcomes: List[str]
    content_items: List[Dict[str, Any]]
    assessment_items: List[Dict[str, Any]]


@dataclass
class CourseStructure:
    """Represents complete course structure"""
    course_id: str
    course_title: str
    course_description: str
    credit_hours: int
    modules: List[CourseModule]
    prerequisites: List[str]
    learning_outcomes: List[str]
    assessment_strategy: str


class IMSCCParser:
    """Parser for IMS Content Package (IMSCC) files"""

    # XML namespaces used in IMSCC
    NAMESPACES = {
        'imscc': 'http://www.imsglobal.org/xsd/imsccv1p3/imscp_v1p0',
        'lom': 'http://ltsc.ieee.org/xsd/LOM',
        'imsmd': 'http://www.imsglobal.org/xsd/imsmd_v1p2',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_course = None

    async def parse_imscc_file(self, file_path: str) -> Optional[CourseStructure]:
        """
        Parse an IMSCC file and extract course structure.

        Args:
            file_path: Path to the .imscc or .zip file

        Returns:
            CourseStructure object with extracted data
        """
        try:
            self.logger.info(f"Parsing IMSCC file: {file_path}")

            # Extract IMSCC (which is a ZIP file)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Read manifest.xml
                manifest_data = zip_ref.read('imsmanifest.xml')
                root = ET.fromstring(manifest_data)

                # Extract course metadata
                course_structure = self._extract_course_metadata(root)

                # Extract organizations and modules
                course_structure.modules = self._extract_modules(root, zip_ref)

                # Extract learning outcomes
                course_structure.learning_outcomes = self._extract_learning_outcomes(root)

                self.logger.info(f"Successfully parsed course: {course_structure.course_title}")
                return course_structure

        except zipfile.BadZipFile:
            self.logger.error(f"Invalid ZIP file: {file_path}")
            return None
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing IMSCC file: {str(e)}")
            return None

    def _extract_course_metadata(self, root: ET.Element) -> CourseStructure:
        """Extract basic course metadata from manifest"""
        metadata = root.find('.//imsmd:lom', self.NAMESPACES)

        course_title = "Untitled Course"
        course_description = ""

        if metadata is not None:
            title_elem = metadata.find('.//imsmd:title/imsmd:string', self.NAMESPACES)
            if title_elem is not None:
                course_title = title_elem.text or "Untitled Course"

            desc_elem = metadata.find('.//imsmd:description/imsmd:string', self.NAMESPACES)
            if desc_elem is not None:
                course_description = desc_elem.text or ""

        return CourseStructure(
            course_id=f"course_{hash(course_title) % 10000}",
            course_title=course_title,
            course_description=course_description,
            credit_hours=3,
            modules=[],
            prerequisites=[],
            learning_outcomes=[],
            assessment_strategy="Formative and summative"
        )

    def _extract_modules(self, root: ET.Element, zip_ref: zipfile.ZipFile) -> List[CourseModule]:
        """Extract course modules and their content"""
        modules = []

        # Find all organizations
        orgs = root.findall('.//imscc:organization', self.NAMESPACES)

        for org in orgs:
            items = org.findall('.//imscc:item', self.NAMESPACES)

            for idx, item in enumerate(items):
                identifier = item.get('identifier', f'module_{idx}')
                title = item.get('title', f'Module {idx + 1}')

                # Extract content items associated with this module
                content_items = self._extract_content_items(item, zip_ref)

                module = CourseModule(
                    identifier=identifier,
                    title=title,
                    description=f"Module {idx + 1} content",
                    learning_outcomes=[
                        f"Understand {title.lower()} concepts",
                        f"Apply {title.lower()} principles",
                        f"Evaluate {title.lower()} scenarios"
                    ],
                    content_items=content_items,
                    assessment_items=self._extract_assessments(item)
                )
                modules.append(module)

        return modules

    def _extract_content_items(self, item: ET.Element, zip_ref: zipfile.ZipFile) -> List[Dict[str, Any]]:
        """Extract content items (resources) from a module"""
        content_items = []

        # Find all item references
        item_refs = item.findall('.//imscc:item', self.NAMESPACES)

        for ref in item_refs:
            identifier = ref.get('identifier', 'unknown')
            title = ref.get('title', 'Untitled')

            content_items.append({
                'identifier': identifier,
                'title': title,
                'type': 'resource',
                'resource_type': self._determine_resource_type(title)
            })

        return content_items

    def _extract_assessments(self, item: ET.Element) -> List[Dict[str, Any]]:
        """Extract assessment items from a module"""
        assessments = []

        # Look for assessment files
        item_refs = item.findall('.//imscc:item', self.NAMESPACES)

        for ref in item_refs:
            title = ref.get('title', '').lower()
            if any(keyword in title for keyword in ['quiz', 'test', 'assessment', 'exam']):
                assessments.append({
                    'type': 'quiz',
                    'title': ref.get('title'),
                    'identifier': ref.get('identifier')
                })

        return assessments

    def _extract_learning_outcomes(self, root: ET.Element) -> List[str]:
        """Extract learning outcomes from course metadata"""
        outcomes = []

        # Look for learning objectives in metadata
        objectives = root.findall('.//imsmd:educational/imsmd:learningResourceType', self.NAMESPACES)

        if objectives:
            for obj in objectives:
                if obj.text:
                    outcomes.append(obj.text)

        # Default outcomes if none found
        if not outcomes:
            outcomes = [
                "Understand key concepts and terminology",
                "Apply learned principles to practical scenarios",
                "Analyze and evaluate complex problems",
                "Create solutions based on course content"
            ]

        return outcomes

    def _determine_resource_type(self, title: str) -> str:
        """Determine resource type from title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ['reading', 'article', 'text', 'document']):
            return 'reading'
        elif any(word in title_lower for word in ['video', 'lecture', 'recording']):
            return 'video'
        elif any(word in title_lower for word in ['quiz', 'test', 'assessment']):
            return 'assessment'
        elif any(word in title_lower for word in ['discussion', 'forum']):
            return 'discussion'
        elif any(word in title_lower for word in ['assignment', 'activity']):
            return 'activity'
        else:
            return 'resource'

    async def parse_multiple_files(self, file_paths: List[str]) -> Dict[str, CourseStructure]:
        """Parse multiple IMSCC files"""
        courses = {}

        for file_path in file_paths:
            course = await self.parse_imscc_file(file_path)
            if course:
                courses[file_path] = course

        return courses

    def extract_text_content(self, course: CourseStructure) -> str:
        """Extract all text content from a course for processing"""
        text_content = []

        # Add course title and description
        text_content.append(f"Course: {course.course_title}")
        if course.course_description:
            text_content.append(f"Description: {course.course_description}")

        # Add learning outcomes
        text_content.append("Learning Outcomes:")
        for outcome in course.learning_outcomes:
            text_content.append(f"- {outcome}")

        # Add module information
        text_content.append("Modules:")
        for module in course.modules:
            text_content.append(f"\n{module.title}")
            if module.description:
                text_content.append(f"  Description: {module.description}")
            if module.learning_outcomes:
                text_content.append("  Learning Outcomes:")
                for outcome in module.learning_outcomes:
                    text_content.append(f"    - {outcome}")
            if module.content_items:
                text_content.append("  Content Items:")
                for item in module.content_items:
                    text_content.append(f"    - {item['title']} ({item['resource_type']})")

        return "\n".join(text_content)

    def course_to_dict(self, course: CourseStructure) -> Dict[str, Any]:
        """Convert course structure to dictionary for JSON serialization"""
        return {
            'course_id': course.course_id,
            'course_title': course.course_title,
            'course_description': course.course_description,
            'credit_hours': course.credit_hours,
            'prerequisites': course.prerequisites,
            'learning_outcomes': course.learning_outcomes,
            'assessment_strategy': course.assessment_strategy,
            'modules': [
                {
                    'identifier': m.identifier,
                    'title': m.title,
                    'description': m.description,
                    'learning_outcomes': m.learning_outcomes,
                    'content_items': m.content_items,
                    'assessment_items': m.assessment_items
                }
                for m in course.modules
            ]
        }
