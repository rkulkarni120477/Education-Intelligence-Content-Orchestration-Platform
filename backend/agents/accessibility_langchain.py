"""
Accessibility Agent using LangChain
Validates content against WCAG 2.1 AA standards and provides remediation
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class WCAGLevel(str, Enum):
    """WCAG Conformance Levels"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class AccessibilityIssue(BaseModel):
    """Represents an accessibility issue"""
    issue_id: str
    criterion: str  # WCAG criterion (e.g., 1.4.3)
    title: str
    description: str
    severity: str  # Critical, High, Medium, Low
    affected_content: str
    remediation: str
    auto_remediatable: bool


class AccessibilityReport(BaseModel):
    """Accessibility audit report"""
    audit_id: str
    content_id: str
    wcag_level: WCAGLevel
    total_issues: int
    issues_by_severity: Dict[str, int]
    pass_rate: float
    issues: List[AccessibilityIssue]
    recommendations: List[str]
    auto_remediated_count: int
    audit_date: str


class AccessibilityAgentLangChain:
    """
    LangChain-based Accessibility Agent

    Validates content against WCAG 2.1 AA standards:
    - Text alternatives for images
    - Color contrast ratios
    - Heading structure and hierarchy
    - Keyboard navigation
    - Caption generation
    - Alt text generation
    - Reading level assessment
    """

    # WCAG 2.1 AA Success Criteria (Key ones for educational content)
    WCAG_CRITERIA = {
        "1.1.1": {
            "title": "Non-text Content",
            "description": "All non-text content must have text alternatives",
            "level": "A"
        },
        "1.4.3": {
            "title": "Contrast (Minimum)",
            "description": "Visual presentation of text must have 4.5:1 contrast ratio",
            "level": "AA"
        },
        "1.4.11": {
            "title": "Non-text Contrast",
            "description": "Graphical elements and UI components must have 3:1 contrast ratio",
            "level": "AA"
        },
        "2.1.1": {
            "title": "Keyboard",
            "description": "All functionality must be operable via keyboard",
            "level": "A"
        },
        "2.4.3": {
            "title": "Focus Order",
            "description": "Focus order must be logical and meaningful",
            "level": "A"
        },
        "3.1.1": {
            "title": "Language of Page",
            "description": "Default language of page must be specified",
            "level": "A"
        },
        "3.2.4": {
            "title": "Consistent Identification",
            "description": "Components with same function must be identified consistently",
            "level": "AA"
        },
        "2.4.6": {
            "title": "Headings and Labels",
            "description": "Headings and labels must be descriptive",
            "level": "AA"
        },
        "1.3.1": {
            "title": "Info and Relationships",
            "description": "Semantic relationships must be programmatically available",
            "level": "A"
        }
    }

    def __init__(self, db=None):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.llm = None
        self._initialize_langchain()

    def _initialize_langchain(self):
        """Initialize LangChain components"""
        try:
            from config_langchain import get_llm, LangChainConfig

            if not LangChainConfig.validate_config():
                self.logger.warning("LangChain not properly configured")
                return

            self.llm = get_llm()
            if self.llm:
                self.logger.info("Accessibility Agent initialized")

        except ImportError:
            self.logger.warning("LangChain not available")

    async def audit_content(
        self,
        content: str,
        content_type: str,
        wcag_level: WCAGLevel = WCAGLevel.AA
    ) -> AccessibilityReport:
        """
        Audit content for WCAG compliance.

        Args:
            content: Content to audit
            content_type: Type of content (text, html, pdf, video, etc.)
            wcag_level: WCAG level to check against

        Returns:
            Accessibility audit report
        """
        self.logger.info(f"Auditing {content_type} content for WCAG {wcag_level}")

        audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        issues = []

        # Run automated checks
        text_issues = self._check_text_content(content)
        structure_issues = self._check_content_structure(content)
        contrast_issues = self._check_color_contrast(content)
        keyboard_issues = self._check_keyboard_navigation(content)

        all_issues = text_issues + structure_issues + contrast_issues + keyboard_issues

        # If LLM available, do semantic review
        if self.llm:
            try:
                semantic_issues = await self._semantic_accessibility_review(content)
                all_issues.extend(semantic_issues)
            except Exception as e:
                self.logger.warning(f"Semantic review failed: {str(e)}")

        # Remove duplicates
        all_issues = self._deduplicate_issues(all_issues)

        # Generate auto-remediation suggestions
        auto_remediated = self._generate_auto_remediations(all_issues)

        # Calculate pass rate
        pass_rate = self._calculate_pass_rate(all_issues)

        # Prepare recommendations
        recommendations = self._generate_recommendations(all_issues)

        # Categorize by severity
        severity_counts = self._count_by_severity(all_issues)

        return AccessibilityReport(
            audit_id=audit_id,
            content_id=content_type,
            wcag_level=wcag_level,
            total_issues=len(all_issues),
            issues_by_severity=severity_counts,
            pass_rate=pass_rate,
            issues=all_issues[:20],  # Top 20 issues
            recommendations=recommendations,
            auto_remediated_count=auto_remediated,
            audit_date=datetime.now().isoformat()
        )

    def _check_text_content(self, content: str) -> List[AccessibilityIssue]:
        """Check text content for accessibility"""
        issues = []

        # Check for alt text in images
        if "[image:" in content.lower() and "alt:" not in content.lower():
            issues.append(AccessibilityIssue(
                issue_id="text_001",
                criterion="1.1.1",
                title="Missing Alt Text",
                description="Images found without alt text",
                severity="Critical",
                affected_content="Image references",
                remediation="Add descriptive alt text for all images",
                auto_remediatable=True
            ))

        # Check readability
        avg_sentence_length = self._calculate_avg_sentence_length(content)
        if avg_sentence_length > 25:
            issues.append(AccessibilityIssue(
                issue_id="text_002",
                criterion="3.1.5",
                title="Complex Reading Level",
                description=f"Average sentence length: {avg_sentence_length} words (target: <20)",
                severity="Medium",
                affected_content="Body text",
                remediation="Simplify sentences and use clear language",
                auto_remediatable=False
            ))

        return issues

    def _check_content_structure(self, content: str) -> List[AccessibilityIssue]:
        """Check content structure (headings, lists, etc.)"""
        issues = []

        # Check for proper heading hierarchy
        h1_count = content.count("<h1") if "<h1" in content else content.count("# ")
        h2_count = content.count("<h2") if "<h2" in content else content.count("## ")

        if h1_count == 0:
            issues.append(AccessibilityIssue(
                issue_id="struct_001",
                criterion="1.3.1",
                title="Missing H1 Heading",
                description="No H1 (main heading) found",
                severity="High",
                affected_content="Document structure",
                remediation="Add a descriptive H1 heading at the start",
                auto_remediatable=True
            ))

        # Check for proper list formatting
        if "- " in content and "<ul>" not in content and "- " not in content:
            issues.append(AccessibilityIssue(
                issue_id="struct_002",
                criterion="1.3.1",
                title="Improper List Formatting",
                description="Lists not properly marked up with semantic HTML",
                severity="Medium",
                affected_content="List items",
                remediation="Use <ul>/<ol> elements for lists",
                auto_remediatable=False
            ))

        return issues

    def _check_color_contrast(self, content: str) -> List[AccessibilityIssue]:
        """Check color contrast ratios"""
        issues = []

        # Look for color specifications
        if "color:" in content.lower() or "#" in content:
            issues.append(AccessibilityIssue(
                issue_id="contrast_001",
                criterion="1.4.3",
                title="Contrast Ratio Check Needed",
                description="Color values found - manual contrast verification needed",
                severity="Medium",
                affected_content="Styled text and backgrounds",
                remediation="Verify all text has 4.5:1 contrast ratio with background",
                auto_remediatable=False
            ))

        return issues

    def _check_keyboard_navigation(self, content: str) -> List[AccessibilityIssue]:
        """Check keyboard navigation support"""
        issues = []

        # Check for mouse-only interactions
        if "onclick" in content.lower() or "hover" in content.lower():
            issues.append(AccessibilityIssue(
                issue_id="keyboard_001",
                criterion="2.1.1",
                title="Keyboard Navigation Issues",
                description="Mouse-only events or hover-based interactions found",
                severity="High",
                affected_content="Interactive elements",
                remediation="Ensure all interactions work with keyboard (Tab, Enter, etc.)",
                auto_remediatable=False
            ))

        return issues

    async def _semantic_accessibility_review(self, content: str) -> List[AccessibilityIssue]:
        """Perform semantic accessibility review using LLM"""
        if not self.llm:
            return []

        try:
            from config_langchain import PromptTemplates

            prompt = PromptTemplates.CHECK_ACCESSIBILITY_PROMPT.format(
                content=content[:2000]  # Limit length
            )

            response = await self._call_llm_async(prompt)

            # Parse response for issues
            issues = self._parse_accessibility_response(response)
            return issues

        except Exception as e:
            self.logger.error(f"Semantic review failed: {str(e)}")
            return []

    async def _call_llm_async(self, prompt: str) -> str:
        """Call LLM asynchronously"""
        if not self.llm:
            raise Exception("LLM not initialized")

        response = self.llm.predict(prompt)
        return response

    def _deduplicate_issues(self, issues: List[AccessibilityIssue]) -> List[AccessibilityIssue]:
        """Remove duplicate issues"""
        seen = set()
        unique = []

        for issue in issues:
            if issue.criterion not in seen:
                unique.append(issue)
                seen.add(issue.criterion)

        return unique

    def _generate_auto_remediations(self, issues: List[AccessibilityIssue]) -> int:
        """Count auto-remediatable issues"""
        return len([i for i in issues if i.auto_remediatable])

    def _calculate_pass_rate(self, issues: List[AccessibilityIssue]) -> float:
        """Calculate pass rate (percentage of WCAG criteria met)"""
        if not issues:
            return 100.0

        total_criteria = len(self.WCAG_CRITERIA)
        criteria_with_issues = len(set(i.criterion for i in issues))

        pass_rate = ((total_criteria - criteria_with_issues) / total_criteria) * 100
        return max(0, min(100, pass_rate))

    def _generate_recommendations(self, issues: List[AccessibilityIssue]) -> List[str]:
        """Generate priority recommendations"""
        recommendations = []

        # Priority 1: Critical issues
        critical = [i for i in issues if i.severity == "Critical"]
        if critical:
            recommendations.append(f"CRITICAL: Fix {len(critical)} critical issues - {critical[0].title}")

        # Priority 2: Auto-remediatable
        auto = [i for i in issues if i.auto_remediatable]
        if auto:
            recommendations.append(f"AUTO-FIX: {len(auto)} issues can be automatically remediated")

        # Priority 3: High severity
        high = [i for i in issues if i.severity == "High"]
        if high:
            recommendations.append(f"HIGH: Address {len(high)} high-severity issues")

        # General recommendations
        recommendations.extend([
            "Ensure all images have descriptive alt text",
            "Verify color contrast ratios meet 4.5:1 standard",
            "Use semantic HTML (headings, lists, etc.)",
            "Support full keyboard navigation",
            "Add captions to videos",
            "Test with screen readers"
        ])

        return recommendations[:5]

    def _count_by_severity(self, issues: List[AccessibilityIssue]) -> Dict[str, int]:
        """Count issues by severity"""
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

        for issue in issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1

        return counts

    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length"""
        sentences = text.split(".")
        if not sentences:
            return 0

        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences) if sentences else 0

    def _parse_accessibility_response(self, response: str) -> List[AccessibilityIssue]:
        """Parse LLM accessibility review response"""
        issues = []

        # Simple parsing - in production would be more sophisticated
        if "issue" in response.lower():
            issues.append(AccessibilityIssue(
                issue_id="semantic_001",
                criterion="2.4.6",
                title="Content Clarity Issue",
                description="Content may lack sufficient context or structure",
                severity="Medium",
                affected_content="Document content",
                remediation=response[:200],
                auto_remediatable=False
            ))

        return issues

    async def remediate_content(
        self,
        content: str,
        issues: List[AccessibilityIssue]
    ) -> Tuple[str, List[str]]:
        """
        Generate remediations for accessibility issues.

        Returns:
            Tuple of (remediated_content, remediation_log)
        """
        remediated = content
        log = []

        for issue in issues:
            if issue.auto_remediatable:
                try:
                    remediated, action = self._apply_auto_remediation(remediated, issue)
                    log.append(f"✓ {action}")
                except Exception as e:
                    log.append(f"✗ Failed: {issue.title}")

        return remediated, log

    def _apply_auto_remediation(self, content: str, issue: AccessibilityIssue) -> Tuple[str, str]:
        """Apply auto-remediation for an issue"""

        if issue.issue_id == "text_001":
            # Add placeholder alt text
            remediated = content.replace("[image:", "[image:alt='Image':")
            return remediated, "Added default alt text placeholders"

        elif issue.issue_id == "struct_001":
            # Add H1 if missing
            remediated = "# Main Title\n\n" + content
            return remediated, "Added H1 heading"

        return content, "No auto-remediation available"
