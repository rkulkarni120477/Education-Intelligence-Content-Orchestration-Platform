"""
Requirements Extraction Service.

Uses Claude to extract institution requirements from program context,
goals, and workforce role descriptions.
"""

from typing import Dict, List, Any, Optional
import json
import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExtractedRequirement(BaseModel):
    """A single extracted requirement from source material."""
    category: str  # goals, roles, skills, constraints, guidelines
    content: str
    source_reference: str
    confidence: float  # 0-1
    requires_clarification: bool
    clarification_question: Optional[str] = None


class RequirementsExtractionResult(BaseModel):
    """Results from requirements extraction."""
    program_name: str
    program_description: str
    target_roles: List[Dict[str, str]]  # [{name, description, context}]
    required_skills: List[Dict[str, str]]  # [{name, level, reason}]
    constraints: Dict[str, Any]  # {duration, format, audience, prerequisites}
    accessibility_requirements: List[str]
    style_guidelines: List[str]
    ambiguities: List[Dict[str, str]]  # [{item, question, context}]
    confidence: float  # overall extraction confidence
    extraction_metadata: Dict[str, Any]


class RequirementsExtractionService:
    """Service for extracting institution requirements using Claude."""

    def __init__(self, model: str = "claude-opus-5-5"):
        """
        Initialize the service.

        Args:
            model: Claude model to use for extraction
        """
        self.model = model
        self.client = ChatAnthropic(model=model)

    def extract_requirements(
        self,
        program_name: str,
        program_context: str,
        institution_goals: str,
        workforce_role_descriptions: str,
        style_guide: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> RequirementsExtractionResult:
        """
        Extract institution requirements using Claude.

        Args:
            program_name: Name of the program
            program_context: Context about the program (level, type, audience)
            institution_goals: Institution's educational and mission goals
            workforce_role_descriptions: Descriptions of target workforce roles
            style_guide: Optional style guide or branding guidelines
            additional_context: Any additional context (policies, constraints)

        Returns:
            RequirementsExtractionResult with extracted requirements
        """
        try:
            logger.info(f"Extracting requirements for program: {program_name}")

            # Build system prompt
            system_prompt = """You are an expert educational curriculum analyst. Your task is to extract
structured requirements from institution context, goals, and workforce role descriptions.

Extract and structure:
1. Program description and context
2. Target workforce roles (name, description, key responsibilities)
3. Required skills for each role (skill name, proficiency level, reason)
4. Constraints (duration, delivery format, audience, prerequisites)
5. Accessibility requirements
6. Style and branding guidelines
7. Ambiguities or questions that need clarification

For each extracted item, provide:
- Clear description
- Source reference (which input section it came from)
- Confidence level (0-1)
- Any questions that need clarification

Format your response as a JSON object matching this structure:
{
  "program_description": "...",
  "target_roles": [{"name": "...", "description": "...", "context": "..."}],
  "required_skills": [{"name": "...", "proficiency": "...", "reason": "..."}],
  "constraints": {"duration": "...", "format": "...", "audience": "..."},
  "accessibility_requirements": ["..."],
  "style_guidelines": ["..."],
  "ambiguities": [{"item": "...", "question": "...", "context": "..."}],
  "confidence": 0.85,
  "notes": "..."
}"""

            # Build user message with all context
            context_parts = [
                f"Program: {program_name}",
                f"Program Context: {program_context}",
                f"Institution Goals: {institution_goals}",
                f"Workforce Roles: {workforce_role_descriptions}",
            ]

            if style_guide:
                context_parts.append(f"Style Guide: {style_guide}")

            if additional_context:
                context_parts.append(f"Additional Context: {additional_context}")

            user_message = "\n\n".join(context_parts)

            # Call Claude
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message),
            ]

            response = self.client.invoke(messages)
            response_text = response.content

            # Parse JSON response
            try:
                # Extract JSON from response (may have surrounding text)
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    extracted = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse Claude response: {str(e)}")
                # Return partial result with error note
                extracted = {
                    "program_description": program_name,
                    "target_roles": [],
                    "required_skills": [],
                    "constraints": {},
                    "accessibility_requirements": [],
                    "style_guidelines": [],
                    "ambiguities": [{"item": "parsing_error", "question": "Response parsing failed", "context": str(e)}],
                    "confidence": 0.0,
                    "notes": "Extraction failed - could not parse response"
                }

            # Build result
            result = RequirementsExtractionResult(
                program_name=program_name,
                program_description=extracted.get("program_description", program_name),
                target_roles=extracted.get("target_roles", []),
                required_skills=extracted.get("required_skills", []),
                constraints=extracted.get("constraints", {}),
                accessibility_requirements=extracted.get("accessibility_requirements", []),
                style_guidelines=extracted.get("style_guidelines", []),
                ambiguities=extracted.get("ambiguities", []),
                confidence=float(extracted.get("confidence", 0.0)),
                extraction_metadata={
                    "model": self.model,
                    "source_context_length": len(user_message),
                    "notes": extracted.get("notes", ""),
                }
            )

            logger.info(f"✓ Requirements extracted for {program_name} (confidence: {result.confidence})")
            return result

        except Exception as e:
            logger.error(f"Requirements extraction failed: {str(e)}")
            raise


def extract_program_requirements(
    program_name: str,
    program_context: str,
    institution_goals: str,
    workforce_role_descriptions: str,
    style_guide: Optional[str] = None,
    additional_context: Optional[str] = None,
) -> RequirementsExtractionResult:
    """
    Convenience function to extract requirements.

    Args:
        See RequirementsExtractionService.extract_requirements

    Returns:
        RequirementsExtractionResult
    """
    service = RequirementsExtractionService()
    return service.extract_requirements(
        program_name=program_name,
        program_context=program_context,
        institution_goals=institution_goals,
        workforce_role_descriptions=workforce_role_descriptions,
        style_guide=style_guide,
        additional_context=additional_context,
    )
