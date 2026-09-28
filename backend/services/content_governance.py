"""Content governance checks and approval recommendations."""

from pathlib import Path
from typing import Any, Dict

from database.models import Content


class ContentGovernanceAgent:
    """Recommend whether indexed content is ready for human approval."""

    name = "Content Governance Agent"

    @staticmethod
    def review(content: Content) -> Dict[str, Any]:
        metadata = content.content_metadata or {}
        checks = {
            "source_file_exists": bool(content.source and Path(content.source).is_file()),
            "has_extracted_text": bool(content.raw_content and content.raw_content.strip()),
            "has_title": bool(content.title and content.title.strip()),
            "has_subject": bool(metadata.get("subject")),
            "has_grade": bool(metadata.get("grade")),
        }
        passed = sum(checks.values())
        recommendation = "approve" if passed == len(checks) else "review"

        return {
            "agent": ContentGovernanceAgent.name,
            "recommendation": recommendation,
            "confidence": round(passed / len(checks), 2),
            "checks": checks,
            "reason": (
                "All automated governance checks passed. Human approval is required."
                if recommendation == "approve"
                else "One or more governance checks require human review."
            ),
        }
