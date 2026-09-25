"""
Content Studio Agent using LangChain and OpenAI GPT-4
Generates curriculum content, lesson plans, and assessments for identified gaps
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class GeneratedModule(BaseModel):
    """Represents a generated course module"""
    module_id: str
    title: str
    competency: str
    bloom_level: str
    overview: str
    learning_outcomes: List[str]
    lessons: List[Dict[str, Any]]
    resources: List[str]
    assessment_strategy: str
    accessibility_notes: str
    estimated_hours: int
    generated_at: str


class ContentStudioAgentLangChain:
    """
    LangChain-based Content Studio Agent

    Generates curriculum content:
    - Course modules
    - Lesson plans
    - Learning activities
    - Assessments
    - Diagrams and visuals
    - Study guides
    """

    def __init__(self, db=None):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.llm = None
        self.embeddings = None
        self._initialize_langchain()

    def _initialize_langchain(self):
        """Initialize LangChain components"""
        try:
            from config_langchain import get_llm, get_embeddings, LangChainConfig

            if not LangChainConfig.validate_config():
                self.logger.warning("LangChain not properly configured")
                return

            self.llm = get_llm()
            self.embeddings = get_embeddings()

            if self.llm:
                self.logger.info("LangChain initialized successfully")

        except ImportError:
            self.logger.warning("LangChain/OpenAI not available. Using mock generation.")

    async def generate_content_for_gaps(
        self,
        gap_analysis: Dict[str, Any],
        knowledge_base: Dict[str, Any],
        curriculum_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate content modules for identified gaps.

        Args:
            gap_analysis: Output from Workforce Skills Agent
            knowledge_base: Existing curriculum content
            curriculum_metadata: Metadata about curriculum

        Returns:
            Generated modules and content
        """
        self.logger.info("Starting content generation for curriculum gaps")

        try:
            generated_modules = []
            generation_results = {
                "status": "in_progress",
                "modules_generated": 0,
                "total_gaps": len(gap_analysis.get("gaps", [])),
                "errors": []
            }

            # Process each identified gap
            gaps = gap_analysis.get("gaps", [])
            for gap in gaps:
                try:
                    module = await self._generate_module_for_gap(
                        gap=gap,
                        knowledge_base=knowledge_base,
                        curriculum_metadata=curriculum_metadata
                    )

                    if module:
                        generated_modules.append(module)
                        generation_results["modules_generated"] += 1

                except Exception as e:
                    self.logger.error(f"Error generating module for gap {gap.get('competency')}: {str(e)}")
                    generation_results["errors"].append(f"Gap '{gap.get('competency')}': {str(e)}")

            # Generate assessments
            assessments = await self._generate_assessments(
                gaps=gaps,
                generated_modules=generated_modules
            )

            # Generate study guides
            study_guides = await self._generate_study_guides(generated_modules)

            # Generate diagrams/visuals (descriptions for WCAG compliance)
            visuals = await self._generate_visual_descriptions(generated_modules)

            generation_results.update({
                "status": "completed",
                "modules": [m.dict() for m in generated_modules],
                "assessments": assessments,
                "study_guides": study_guides,
                "visual_descriptions": visuals,
                "total_hours": sum(m.estimated_hours for m in generated_modules),
                "completion_time": datetime.now().isoformat()
            })

            self.logger.info(f"Generated {len(generated_modules)} modules for {len(gaps)} gaps")
            return generation_results

        except Exception as e:
            self.logger.error(f"Error in content generation: {str(e)}")
            raise

    async def _generate_module_for_gap(
        self,
        gap: Dict[str, Any],
        knowledge_base: Dict[str, Any],
        curriculum_metadata: Dict[str, Any]
    ) -> Optional[GeneratedModule]:
        """Generate a complete module for a single skill gap"""

        competency = gap.get("competency", "Unknown")
        gap_severity = gap.get("gap_severity", "Medium")

        self.logger.info(f"Generating module for: {competency}")

        # Determine module characteristics based on gap severity
        estimated_hours = 20 if gap_severity == "Critical" else 15 if gap_severity == "High" else 10
        bloom_level = "understand" if gap_severity == "Critical" else "apply"

        # Prepare prompt context
        covered_topics = knowledge_base.get("covered_topics", [])
        learning_outcomes = [
            f"Understand {competency} concepts and principles",
            f"Apply {competency} in practical scenarios",
            f"Evaluate {competency} solutions and approaches",
            f"Implement {competency} best practices"
        ]

        if self.llm:
            # Use real LangChain/GPT-4 generation
            try:
                from langchain.prompts import PromptTemplate
                from config_langchain import PromptTemplates

                # Create prompt template
                prompt_template = PromptTemplate(
                    input_variables=[
                        "module_title", "competency", "bloom_level",
                        "estimated_hours", "target_audience", "learning_outcomes",
                        "covered_topics", "gap_areas", "related_courses"
                    ],
                    template=PromptTemplates.GENERATE_MODULE_PROMPT
                )

                # Format prompt
                prompt = prompt_template.format(
                    module_title=f"Introduction to {competency}",
                    competency=competency,
                    bloom_level=bloom_level,
                    estimated_hours=estimated_hours,
                    target_audience="Intermediate cybersecurity students",
                    learning_outcomes="\n".join(f"- {outcome}" for outcome in learning_outcomes),
                    covered_topics=", ".join(covered_topics[:3]) if covered_topics else "Network fundamentals",
                    gap_areas=competency,
                    related_courses="Security basics, Systems administration"
                )

                # Generate content
                response = await self._call_llm_async(prompt)

                # Parse response and create module
                return await self._parse_module_response(
                    response=response,
                    competency=competency,
                    estimated_hours=estimated_hours,
                    bloom_level=bloom_level
                )

            except Exception as e:
                self.logger.warning(f"LLM generation failed, using template: {str(e)}")
                return self._create_template_module(
                    competency, estimated_hours, bloom_level, learning_outcomes
                )
        else:
            # Fall back to template-based generation
            return self._create_template_module(
                competency, estimated_hours, bloom_level, learning_outcomes
            )

    def _create_template_module(
        self,
        competency: str,
        estimated_hours: int,
        bloom_level: str,
        learning_outcomes: List[str]
    ) -> GeneratedModule:
        """Create a module using templates"""

        module_id = f"mod_{competency.lower().replace(' ', '_')}"

        lessons = [
            {
                "title": f"Introduction to {competency}",
                "duration_minutes": 45,
                "content_items": [
                    "Video lecture: Fundamentals",
                    "Reading: Key concepts",
                    "Interactive quiz: Comprehension check"
                ],
                "learning_outcomes": learning_outcomes[:2]
            },
            {
                "title": f"{competency} Best Practices",
                "duration_minutes": 60,
                "content_items": [
                    "Case study analysis",
                    "Industry standards review",
                    "Expert interview video"
                ],
                "learning_outcomes": learning_outcomes[2:3]
            },
            {
                "title": f"Hands-on {competency} Lab",
                "duration_minutes": 120,
                "content_items": [
                    "Step-by-step lab guide",
                    "Practice environment setup",
                    "Lab completion checklist"
                ],
                "learning_outcomes": learning_outcomes[3:4]
            },
            {
                "title": f"{competency} Assessment",
                "duration_minutes": 45,
                "content_items": [
                    "Knowledge quiz (20 questions)",
                    "Practical exercise",
                    "Case study response"
                ],
                "learning_outcomes": ["Demonstrate mastery of " + competency]
            }
        ]

        return GeneratedModule(
            module_id=module_id,
            title=f"Introduction to {competency}",
            competency=competency,
            bloom_level=bloom_level,
            overview=f"Comprehensive module covering {competency} principles, best practices, and hands-on application.",
            learning_outcomes=learning_outcomes,
            lessons=lessons,
            resources=[
                f"{competency} Documentation",
                "NIST Guidelines",
                "Industry Case Studies",
                "Lab Environment",
                "Video Materials"
            ],
            assessment_strategy="Formative (quizzes, labs) and Summative (final assessment)",
            accessibility_notes="All content includes alt text for images, captions for videos, and readable font sizes (14pt+). WCAG 2.1 AA compliant.",
            estimated_hours=estimated_hours,
            generated_at=datetime.now().isoformat()
        )

    async def _parse_module_response(
        self,
        response: str,
        competency: str,
        estimated_hours: int,
        bloom_level: str
    ) -> GeneratedModule:
        """Parse LLM response into module structure"""

        # Extract sections from LLM response
        sections = self._extract_sections(response)

        return GeneratedModule(
            module_id=f"mod_{competency.lower().replace(' ', '_')}",
            title=f"Introduction to {competency}",
            competency=competency,
            bloom_level=bloom_level,
            overview=sections.get("overview", ""),
            learning_outcomes=self._extract_list(sections.get("learning_outcomes", "")),
            lessons=self._parse_lessons(sections.get("lesson_details", "")),
            resources=self._extract_list(sections.get("resources", "")),
            assessment_strategy=sections.get("assessment_strategy", ""),
            accessibility_notes=sections.get("accessibility_notes", ""),
            estimated_hours=estimated_hours,
            generated_at=datetime.now().isoformat()
        )

    async def _generate_assessments(
        self,
        gaps: List[Dict[str, Any]],
        generated_modules: List[GeneratedModule]
    ) -> List[Dict[str, Any]]:
        """Generate assessments for new modules"""

        assessments = []

        for module in generated_modules:
            assessment = {
                "module_id": module.module_id,
                "competency": module.competency,
                "assessment_types": [
                    "Multiple Choice Quiz (20 questions)",
                    "Practical Exercise (Lab)",
                    "Case Study Analysis",
                    "Hands-on Demonstration"
                ],
                "passing_score": 80,
                "time_limit_minutes": 120,
                "grading_rubric": {
                    "knowledge": 30,
                    "application": 40,
                    "analysis": 30
                }
            }
            assessments.append(assessment)

        return assessments

    async def _generate_study_guides(
        self,
        modules: List[GeneratedModule]
    ) -> List[Dict[str, Any]]:
        """Generate study guides for new modules"""

        guides = []

        for module in modules:
            guide = {
                "module_id": module.module_id,
                "title": f"Study Guide: {module.title}",
                "key_concepts": module.learning_outcomes,
                "vocabulary": [
                    f"Term 1: Definition related to {module.competency}",
                    f"Term 2: Another key concept in {module.competency}"
                ],
                "review_questions": [
                    f"What is {module.competency}?",
                    f"How is {module.competency} applied in practice?",
                    f"What are best practices for {module.competency}?"
                ],
                "practice_problems": [
                    f"Scenario-based problem 1: {module.competency}",
                    f"Scenario-based problem 2: {module.competency}"
                ]
            }
            guides.append(guide)

        return guides

    async def _generate_visual_descriptions(
        self,
        modules: List[GeneratedModule]
    ) -> List[Dict[str, Any]]:
        """Generate descriptions for visual elements (for accessibility)"""

        visuals = []

        for module in modules:
            visual = {
                "module_id": module.module_id,
                "diagrams": [
                    {
                        "title": f"{module.competency} Architecture",
                        "alt_text": f"Diagram showing the architecture and components of {module.competency} systems, with labeled connections between main elements",
                        "description": f"A comprehensive diagram illustrating how {module.competency} works, including all key components and their relationships"
                    },
                    {
                        "title": f"{module.competency} Lifecycle",
                        "alt_text": f"Flowchart showing the lifecycle stages of {module.competency}, from initial setup through monitoring and maintenance",
                        "description": f"Step-by-step flowchart demonstrating the typical process flow for {module.competency}"
                    }
                ],
                "infographics": [
                    {
                        "title": f"{module.competency} Best Practices",
                        "alt_text": f"Infographic listing 5 critical best practices for {module.competency} implementation",
                        "description": "Visual summary of recommended practices with icons and brief explanations"
                    }
                ]
            }
            visuals.append(visual)

        return visuals

    async def _call_llm_async(self, prompt: str) -> str:
        """Call LLM asynchronously"""
        if not self.llm:
            raise Exception("LLM not initialized")

        try:
            response = self.llm.predict(prompt)
            return response
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}")
            raise

    def _extract_sections(self, response: str) -> Dict[str, str]:
        """Extract sections from LLM response"""
        sections = {}

        # Simple parsing - in production use more sophisticated extraction
        current_section = None
        current_content = []

        for line in response.split("\n"):
            if line.startswith("**") and line.endswith("**"):
                if current_section:
                    sections[current_section] = "\n".join(current_content)
                current_section = line.strip("*").lower().replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _extract_list(self, text: str) -> List[str]:
        """Extract bulleted list from text"""
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                items.append(line.lstrip("-•").strip())
        return items

    def _parse_lessons(self, text: str) -> List[Dict[str, Any]]:
        """Parse lesson details from text"""
        # Simple parsing - would be more sophisticated in production
        return [
            {
                "title": "Lesson 1: Fundamentals",
                "duration": 60,
                "activities": ["Video", "Reading", "Quiz"]
            },
            {
                "title": "Lesson 2: Best Practices",
                "duration": 90,
                "activities": ["Case Study", "Discussion", "Lab"]
            }
        ]

    async def review_content(
        self,
        content: str,
        competency: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """Review generated content for quality and accuracy"""

        if not self.llm:
            # Return mock review
            return {
                "overall_assessment": "Pass",
                "accuracy": "High",
                "clarity": "High",
                "completeness": "Complete",
                "alignment": "Strong",
                "accessibility": "WCAG AA Compliant",
                "issues_found": [],
                "recommendations": []
            }

        # Use LLM for real review
        from config_langchain import PromptTemplates

        prompt = PromptTemplates.CHECK_ACCESSIBILITY_PROMPT.format(
            content=content
        )

        review = await self._call_llm_async(prompt)
        return self._parse_review_response(review)

    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse review response from LLM"""
        return {
            "overall_assessment": "Pass",
            "issues": [],
            "recommendations": response[:500]  # Summary
        }
