from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, Optional, List
import logging
from sqlalchemy.orm import Session
from database.models import AccessibilityAudit, Content

logger = logging.getLogger(__name__)

# WCAG 2.1 Accessibility Guidelines
WCAG_GUIDELINES = {
    "A": [
        "Ensure all images have alt text",
        "Ensure video has captions",
        "Maintain color contrast ratio 4.5:1 for text",
        "Ensure keyboard navigation possible",
        "No auto-playing media",
        "Avoid flashing content"
    ],
    "AA": [
        "Enhanced color contrast 7:1",
        "Audio descriptions for video",
        "Resizable text support",
        "Focus indicators visible",
        "Language of page identified",
        "Labels for form inputs"
    ],
    "AAA": [
        "Extended descriptions",
        "Sign language for video",
        "Maximum color contrast",
        "Animation can be paused",
        "Multiple navigation methods",
        "Reading time indicators"
    ]
}


class AccessibilityAgent(BaseAgent):
    """Accessibility Audit & Remediation Agent - WCAG compliance"""

    def __init__(self, db: Session):
        super().__init__("accessibility", db)

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process accessibility audit and remediation tasks"""
        try:
            action = agent_input.data.get("action", "audit")

            if action == "audit":
                return await self._audit_content(agent_input)
            elif action == "identify_issues":
                return await self._identify_issues(agent_input)
            elif action == "generate_remediation":
                return await self._generate_remediation(agent_input)
            elif action == "validate_accessibility":
                return await self._validate_accessibility(agent_input)
            else:
                return AgentOutput(
                    status="failed",
                    data={},
                    errors=[f"Unknown action: {action}"]
                )
        except Exception as e:
            logger.error(f"Accessibility Agent error: {e}")
            return AgentOutput(
                status="failed",
                data={},
                errors=[str(e)]
            )

    async def _audit_content(self, agent_input: AgentInput) -> AgentOutput:
        """Perform accessibility audit on content"""
        content_id = agent_input.data.get("content_id")
        wcag_level = agent_input.data.get("wcag_level", "AA")

        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Content not found: {content_id}"]
            )

        # Perform audit
        issues = self._check_wcag_compliance(content, wcag_level)

        audit = AccessibilityAudit(
            content_id=content_id,
            wcag_level=wcag_level,
            issues=issues,
            status="pending" if issues else "compliant"
        )
        self.db.add(audit)
        self.db.commit()

        return AgentOutput(
            status="success" if not issues else "requires_review",
            data={
                "content_id": content_id,
                "audit_id": audit.id,
                "wcag_level": wcag_level,
                "issues_found": len(issues),
                "compliant": len(issues) == 0,
                "issues": issues
            },
            requires_human_review=len(issues) > 0,
            review_reason="Accessibility issues found" if issues else None
        )

    async def _identify_issues(self, agent_input: AgentInput) -> AgentOutput:
        """Identify accessibility issues"""
        content_id = agent_input.data.get("content_id")
        wcag_level = agent_input.data.get("wcag_level", "AA")

        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Content not found: {content_id}"]
            )

        issues = self._analyze_content_accessibility(content, wcag_level)

        return AgentOutput(
            status="success",
            data={
                "content_id": content_id,
                "wcag_level": wcag_level,
                "total_issues": len(issues),
                "issues_by_severity": self._categorize_by_severity(issues),
                "issues": issues
            }
        )

    async def _generate_remediation(self, agent_input: AgentInput) -> AgentOutput:
        """Generate remediation recommendations"""
        content_id = agent_input.data.get("content_id")
        audit_id = agent_input.data.get("audit_id")

        audit = self.db.query(AccessibilityAudit).filter(
            AccessibilityAudit.id == audit_id
        ).first()

        if not audit:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Audit not found: {audit_id}"]
            )

        remediation_steps = []
        for issue in audit.issues:
            remediation_steps.append({
                "issue": issue,
                "recommendation": self._get_remediation_for_issue(issue),
                "priority": self._get_issue_priority(issue)
            })

        # Update audit with recommendations
        audit.recommendations = remediation_steps
        audit.status = "reviewed"
        self.db.commit()

        return AgentOutput(
            status="success",
            data={
                "audit_id": audit_id,
                "content_id": content_id,
                "remediation_steps": remediation_steps,
                "total_steps": len(remediation_steps)
            }
        )

    async def _validate_accessibility(self, agent_input: AgentInput) -> AgentOutput:
        """Validate accessibility compliance after remediation"""
        content_id = agent_input.data.get("content_id")
        wcag_level = agent_input.data.get("wcag_level", "AA")

        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Content not found: {content_id}"]
            )

        issues = self._check_wcag_compliance(content, wcag_level)

        validation_result = {
            "content_id": content_id,
            "wcag_level": wcag_level,
            "compliant": len(issues) == 0,
            "remaining_issues": len(issues),
            "certification_eligible": len(issues) == 0
        }

        # Update content metadata
        if not content.metadata:
            content.metadata = {}
        content.metadata["wcag_validated"] = len(issues) == 0
        content.metadata["wcag_level"] = wcag_level
        self.db.commit()

        return AgentOutput(
            status="success",
            data=validation_result
        )

    def _check_wcag_compliance(self, content: Content, wcag_level: str = "AA") -> List[str]:
        """Check WCAG compliance"""
        issues = []
        content_lower = content.raw_content.lower() if content.raw_content else ""

        # Check basic requirements
        if wcag_level in ["A", "AA", "AAA"]:
            if "<img" in content.raw_content and "alt=" not in content_lower:
                issues.append("Images missing alt text")

            if "<video" in content.raw_content:
                if "<track" not in content.raw_content:
                    issues.append("Video missing captions")

            if "autoplay" in content_lower:
                issues.append("Auto-playing media detected")

        return issues

    def _analyze_content_accessibility(self, content: Content, wcag_level: str) -> List[Dict[str, Any]]:
        """Analyze content for accessibility issues"""
        issues = []
        checks = WCAG_GUIDELINES.get(wcag_level, [])

        for check in checks:
            if self._should_flag_issue(content, check):
                issues.append({
                    "issue": check,
                    "severity": "high" if wcag_level == "AAA" else "medium"
                })

        return issues

    def _categorize_by_severity(self, issues: List[Dict]) -> Dict[str, int]:
        """Categorize issues by severity"""
        return {
            "critical": sum(1 for i in issues if i.get("severity") == "critical"),
            "high": sum(1 for i in issues if i.get("severity") == "high"),
            "medium": sum(1 for i in issues if i.get("severity") == "medium"),
            "low": sum(1 for i in issues if i.get("severity") == "low")
        }

    def _get_remediation_for_issue(self, issue: str) -> str:
        """Get remediation steps for an issue"""
        remediations = {
            "Images missing alt text": "Add descriptive alt text to all images. Alt text should describe the image content and purpose.",
            "Video missing captions": "Add captions and transcripts for all video content.",
            "Auto-playing media detected": "Disable autoplay or require user interaction before media starts.",
            "Color contrast": "Adjust colors to meet WCAG contrast ratio requirements (4.5:1 for AA, 7:1 for AAA).",
            "Keyboard navigation": "Ensure all interactive elements are reachable via keyboard."
        }

        return remediations.get(issue, f"Please review and remediate: {issue}")

    def _get_issue_priority(self, issue: str) -> str:
        """Get priority level for an issue"""
        critical_issues = ["missing alt text", "video missing captions", "no keyboard navigation"]
        return "critical" if any(ci in issue.lower() for ci in critical_issues) else "high"

    def _should_flag_issue(self, content: Content, check: str) -> bool:
        """Determine if a check should flag an issue"""
        # Simplified check - in production this would be more sophisticated
        raw_lower = (content.raw_content or "").lower()
        check_lower = check.lower()

        if "alt text" in check_lower and "<img" in content.raw_content and "alt=" not in raw_lower:
            return True

        return False
