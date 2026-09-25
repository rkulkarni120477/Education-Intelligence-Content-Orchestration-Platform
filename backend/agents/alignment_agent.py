"""
Alignment Agent - Creates and manages content-to-standards alignments.

Responsible for:
- Generating candidate alignments
- Scoring alignments
- Managing alignment evidence
- Tracking alignment review
"""

from agents.base_agent import BaseAgent, AgentInput
from services.alignment_service import AlignmentService
from auth.tenant_context import TenantContext
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AlignmentAgent(BaseAgent):
    """Alignment generation and management agent."""

    @property
    def name(self) -> str:
        return "alignment"

    @property
    def description(self) -> str:
        return "Creates and manages content-to-standards alignments with scoring"

    @property
    def tools(self) -> List[str]:
        return [
            "create_alignment",
            "score_alignment",
            "get_alignments",
            "review_alignment",
            "calculate_coverage"
        ]

    async def _execute(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute alignment operations.

        Tasks:
        - create_alignment: Create new candidate alignment
        - score_alignment: Score an existing alignment
        - get_alignments: Retrieve alignments for source/standard
        - review_alignment: Review and approve/reject
        - calculate_coverage: Calculate alignment coverage
        """
        logger.info(f"Alignment agent executing: {agent_input.task}")

        # Set tenant context
        TenantContext.set_tenant(agent_input.tenant_id)

        try:
            task = agent_input.task
            params = agent_input.parameters

            if task == "create_alignment":
                return await self._create_alignment(params)
            elif task == "score_alignment":
                return await self._score_alignment(params)
            elif task == "get_alignments":
                return await self._get_alignments(params)
            elif task == "review_alignment":
                return await self._review_alignment(params, agent_input.user_id)
            elif task == "calculate_coverage":
                return await self._calculate_coverage(params)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown task: {task}",
                    "confidence": 0.0
                }

        except Exception as e:
            logger.error(f"Alignment agent error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
        finally:
            TenantContext.clear_tenant()

    async def _create_alignment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a candidate alignment."""
        try:
            service = AlignmentService()

            alignment = service.create_alignment(
                self.db,
                source_type=params.get("source_type"),
                source_id=params.get("source_id"),
                standard_id=params.get("standard_id"),
                objective_id=params.get("objective_id"),
                score=params.get("score", 0.0),
                confidence=params.get("confidence", 0.0),
                evidence=params.get("evidence", [])
            )

            return {
                "status": "success",
                "alignment_id": alignment.id,
                "score": alignment.score,
                "confidence": alignment.confidence,
                "status_detail": "candidate",
                "confidence_score": 0.92
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _score_alignment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Score and update an alignment."""
        alignment_id = params.get("alignment_id")
        score = params.get("score")
        confidence = params.get("confidence")
        evidence = params.get("evidence", [])

        if not alignment_id or score is None or confidence is None:
            return {
                "status": "error",
                "error": "alignment_id, score, and confidence required",
                "confidence": 0.0
            }

        try:
            service = AlignmentService()
            alignment = service.update_alignment(
                self.db,
                alignment_id,
                score=score,
                confidence=confidence,
                evidence=evidence
            )

            return {
                "status": "success",
                "alignment_id": alignment.id,
                "score": alignment.score,
                "confidence": alignment.confidence,
                "evidence_count": len(evidence),
                "confidence_score": 0.90
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _get_alignments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get alignments for a source or standard."""
        source_type = params.get("source_type")
        source_id = params.get("source_id")
        standard_id = params.get("standard_id")
        status = params.get("status")  # Optional filter

        try:
            service = AlignmentService()

            if source_type and source_id:
                alignments = service.get_alignments_for_source(
                    self.db,
                    source_type,
                    source_id,
                    status=status
                )
            elif standard_id:
                alignments = service.get_alignments_for_standard(
                    self.db,
                    standard_id,
                    status=status
                )
            else:
                return {
                    "status": "error",
                    "error": "source_type+source_id or standard_id required",
                    "confidence": 0.0
                }

            return {
                "status": "success",
                "alignments": [
                    {
                        "id": a.id,
                        "score": a.score,
                        "confidence": a.confidence,
                        "status": a.status,
                        "evidence_count": len(a.evidence or [])
                    }
                    for a in alignments
                ],
                "total": len(alignments),
                "confidence_score": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _review_alignment(self, params: Dict[str, Any], reviewer_id: str) -> Dict[str, Any]:
        """Review and approve/reject an alignment."""
        alignment_id = params.get("alignment_id")
        decision = params.get("decision")  # 'approved' or 'rejected'
        notes = params.get("notes", "")

        if not alignment_id or decision not in ["approved", "rejected"]:
            return {
                "status": "error",
                "error": "alignment_id and valid decision required",
                "confidence": 0.0
            }

        try:
            service = AlignmentService()
            alignment = service.review_alignment(
                self.db,
                alignment_id,
                decision,
                reviewer_id,
                notes
            )

            return {
                "status": "success",
                "alignment_id": alignment.id,
                "decision": alignment.status,
                "reviewed_at": alignment.reviewed_at.isoformat() if alignment.reviewed_at else None,
                "confidence_score": 0.98
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}

    async def _calculate_coverage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate alignment coverage for a source."""
        source_type = params.get("source_type")
        source_id = params.get("source_id")

        if not source_type or not source_id:
            return {
                "status": "error",
                "error": "source_type and source_id required",
                "confidence": 0.0
            }

        try:
            service = AlignmentService()
            coverage = service.calculate_alignment_coverage(
                self.db,
                source_type,
                source_id
            )

            return {
                "status": "success",
                "source_type": source_type,
                "source_id": source_id,
                "coverage": coverage,
                "confidence_score": 0.95
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "confidence": 0.0}
