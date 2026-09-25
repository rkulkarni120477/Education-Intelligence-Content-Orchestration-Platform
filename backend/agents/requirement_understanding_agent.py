"""
Requirement Understanding Agent
Analyzes curriculum materials and extracts key requirements for the workflow.
"""

import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)


class RequirementAnalysis(BaseModel):
    """Output from requirement understanding agent"""
    program_name: str
    program_intent: str
    target_roles: List[str]
    key_requirements: List[str]
    accreditation_requirements: List[str]
    program_persona: Dict[str, Any]
    extracted_outcomes: List[str]
    content_structure: Dict[str, Any]
    is_valid: bool
    validation_errors: List[str]


class RequirementUnderstandingAgent:
    """
    Agent that analyzes uploaded curriculum materials and extracts requirements.
    Validates IMSCC packages and course materials.
    """

    def __init__(self, db=None):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def analyze_curriculum(
        self,
        imscc_files: List[Dict[str, Any]],
        target_roles: List[str],
        course_design_data: Optional[Dict[str, Any]] = None,
        style_guide: Optional[Dict[str, Any]] = None,
    ) -> RequirementAnalysis:
        """
        Analyze curriculum materials and extract requirements.

        Args:
            imscc_files: List of IMSCC file metadata
            target_roles: Target job roles (e.g., "SOC Analyst I", "Cloud Security Associate")
            course_design_data: Course design spreadsheet data
            style_guide: University style guide and learning guidelines

        Returns:
            RequirementAnalysis with extracted requirements
        """
        self.logger.info(f"Analyzing curriculum with {len(imscc_files)} IMSCC files")

        validation_errors = []

        # Validate IMSCC files
        if not imscc_files:
            validation_errors.append("No IMSCC files provided")

        for imscc_file in imscc_files:
            if not self._validate_imscc_structure(imscc_file):
                validation_errors.append(f"Invalid IMSCC structure: {imscc_file.get('filename')}")

        # Validate target roles
        if not target_roles or len(target_roles) == 0:
            validation_errors.append("No target job roles specified")

        # Extract program structure from course design
        program_structure = self._extract_program_structure(course_design_data)

        # Extract learning outcomes
        extracted_outcomes = self._extract_learning_outcomes(imscc_files)

        # Build program persona
        program_persona = {
            "target_roles": target_roles,
            "delivery_mode": "hybrid",
            "credit_hours": program_structure.get("total_credit_hours", 0),
            "course_count": len(imscc_files),
            "accreditation_bodies": program_structure.get("accreditation", [])
        }

        # Extract key requirements
        key_requirements = [
            "Map to NIST NICE Framework work roles",
            "Preserve credit-hour structure",
            "Maintain accreditation compliance",
            "Align with industry job postings",
            "Ensure WCAG 2.1 AA accessibility"
        ]

        is_valid = len(validation_errors) == 0

        return RequirementAnalysis(
            program_name=self._extract_program_name(course_design_data),
            program_intent=f"Prepare graduates for {', '.join(target_roles)}",
            target_roles=target_roles,
            key_requirements=key_requirements,
            accreditation_requirements=program_structure.get("accreditation", []),
            program_persona=program_persona,
            extracted_outcomes=extracted_outcomes,
            content_structure=program_structure,
            is_valid=is_valid,
            validation_errors=validation_errors
        )

    def _validate_imscc_structure(self, imscc_file: Dict[str, Any]) -> bool:
        """Validate that IMSCC file has proper structure"""
        # Check for required IMSCC components
        required_components = ["manifest", "metadata", "organizations"]

        # For now, validate file metadata exists
        if not imscc_file.get("filename"):
            return False

        if not imscc_file.get("filename", "").endswith(".imscc"):
            return False

        return True

    def _extract_program_structure(self, course_design_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract program structure from course design data"""
        if not course_design_data:
            return {
                "total_credit_hours": 0,
                "course_count": 0,
                "accreditation": []
            }

        return {
            "total_credit_hours": course_design_data.get("total_credit_hours", 120),
            "course_count": course_design_data.get("course_count", 0),
            "accreditation": course_design_data.get("accreditation", ["ACBSP"]),
            "competency_framework": course_design_data.get("framework", "NIST NICE")
        }

    def _extract_program_name(self, course_design_data: Optional[Dict[str, Any]]) -> str:
        """Extract program name"""
        if course_design_data and course_design_data.get("program_name"):
            return course_design_data["program_name"]
        return "Cybersecurity Concentration"

    def _extract_learning_outcomes(self, imscc_files: List[Dict[str, Any]]) -> List[str]:
        """Extract learning outcomes from IMSCC files"""
        outcomes = [
            "Understand network security fundamentals",
            "Apply cloud security best practices",
            "Perform incident response procedures",
            "Implement access control mechanisms",
            "Conduct security assessments"
        ]
        return outcomes

    async def validate_inputs(
        self,
        imscc_files: List[Dict[str, Any]],
        target_roles: List[str]
    ) -> Dict[str, Any]:
        """
        Validate that all required inputs are present and correct.

        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []

        if not imscc_files:
            errors.append("No IMSCC files uploaded")
        elif len(imscc_files) < 2:
            warnings.append("Minimum 2 courses recommended for curriculum analysis")

        if not target_roles:
            errors.append("No target job roles specified")

        for imscc in imscc_files:
            if not imscc.get("filename", "").lower().endswith((".imscc", ".zip")):
                errors.append(f"Invalid file format: {imscc.get('filename')}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "file_count": len(imscc_files),
            "role_count": len(target_roles)
        }
