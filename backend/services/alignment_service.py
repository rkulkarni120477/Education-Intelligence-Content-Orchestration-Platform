"""
Alignment engine service.

Manages content-to-standards and objective-to-standards alignments.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
from database.models import Alignment, Standard, LearningObjective, User
from auth.tenant_context import get_current_tenant_id
from typing import List, Optional, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class AlignmentService:
    """Service for managing and scoring alignments."""

    @staticmethod
    def create_alignment(
        db: Session,
        source_type: str,
        source_id: str,
        standard_id: str = None,
        objective_id: str = None,
        score: float = 0.0,
        confidence: float = 0.0,
        evidence: List[Dict] = None
    ) -> Alignment:
        """
        Create a candidate alignment.

        Args:
            source_type: 'content', 'objective', 'lesson', 'assessment'
            source_id: ID of the source item
            standard_id: ID of the standard (for content/lesson/assessment)
            objective_id: ID of the objective (for content/lesson/assessment)
            score: Alignment score (0-1)
            confidence: Confidence score (0-1)
            evidence: List of supporting evidence/sources
        """
        tenant_id = get_current_tenant_id()

        # Verify standard or objective exists
        if standard_id:
            standard = db.query(Standard).filter(
                and_(
                    Standard.id == standard_id,
                    Standard.tenant_id == tenant_id
                )
            ).first()
            if not standard:
                raise ValueError(f"Standard {standard_id} not found")

        if objective_id:
            objective = db.query(LearningObjective).filter(
                and_(
                    LearningObjective.id == objective_id,
                    LearningObjective.tenant_id == tenant_id
                )
            ).first()
            if not objective:
                raise ValueError(f"Objective {objective_id} not found")

        # Check if alignment already exists
        existing = db.query(Alignment).filter(
            and_(
                Alignment.tenant_id == tenant_id,
                Alignment.source_type == source_type,
                Alignment.source_id == source_id,
                Alignment.standard_id == standard_id,
                Alignment.objective_id == objective_id
            )
        ).first()

        if existing:
            # Update existing instead
            return AlignmentService.update_alignment(
                db,
                existing.id,
                score=score,
                confidence=confidence,
                evidence=evidence
            )

        alignment = Alignment(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            source_type=source_type,
            source_id=source_id,
            target_type="standard" if standard_id else "objective",
            standard_id=standard_id,
            objective_id=objective_id,
            score=score,
            confidence=confidence,
            evidence=evidence or [],
            status="candidate"
        )
        db.add(alignment)
        db.commit()
        db.refresh(alignment)
        logger.info(f"Created alignment: {alignment.id}")
        return alignment

    @staticmethod
    def update_alignment(
        db: Session,
        alignment_id: str,
        score: float = None,
        confidence: float = None,
        evidence: List[Dict] = None,
        status: str = None
    ) -> Alignment:
        """Update an alignment's score, confidence, and evidence."""
        tenant_id = get_current_tenant_id()

        alignment = db.query(Alignment).filter(
            and_(
                Alignment.id == alignment_id,
                Alignment.tenant_id == tenant_id
            )
        ).first()

        if not alignment:
            raise ValueError(f"Alignment {alignment_id} not found")

        if score is not None:
            alignment.score = max(0.0, min(1.0, score))  # Clamp to 0-1

        if confidence is not None:
            alignment.confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1

        if evidence is not None:
            alignment.evidence = evidence

        if status is not None:
            alignment.status = status

        db.commit()
        db.refresh(alignment)
        return alignment

    @staticmethod
    def review_alignment(
        db: Session,
        alignment_id: str,
        decision: str,  # 'approved', 'rejected'
        reviewer_id: str,
        notes: str = None
    ) -> Alignment:
        """Review and approve/reject an alignment."""
        tenant_id = get_current_tenant_id()

        alignment = db.query(Alignment).filter(
            and_(
                Alignment.id == alignment_id,
                Alignment.tenant_id == tenant_id
            )
        ).first()

        if not alignment:
            raise ValueError(f"Alignment {alignment_id} not found")

        # Verify reviewer exists
        reviewer = db.query(User).filter(
            and_(
                User.id == reviewer_id,
                User.tenant_id == tenant_id
            )
        ).first()

        if not reviewer:
            raise ValueError(f"Reviewer {reviewer_id} not found in tenant")

        alignment.status = "approved" if decision == "approved" else "rejected"
        alignment.reviewed_by = reviewer_id
        alignment.reviewed_at = datetime.utcnow()

        db.commit()
        db.refresh(alignment)
        logger.info(f"Reviewed alignment {alignment_id}: {alignment.status}")
        return alignment

    @staticmethod
    def get_alignments_for_source(
        db: Session,
        source_type: str,
        source_id: str,
        status: str = None
    ) -> List[Alignment]:
        """Get all alignments for a content source."""
        tenant_id = get_current_tenant_id()

        query = db.query(Alignment).filter(
            and_(
                Alignment.tenant_id == tenant_id,
                Alignment.source_type == source_type,
                Alignment.source_id == source_id
            )
        )

        if status:
            query = query.filter(Alignment.status == status)

        return query.all()

    @staticmethod
    def get_alignments_for_standard(
        db: Session,
        standard_id: str,
        status: str = None
    ) -> List[Alignment]:
        """Get all alignments for a standard."""
        tenant_id = get_current_tenant_id()

        query = db.query(Alignment).filter(
            and_(
                Alignment.tenant_id == tenant_id,
                Alignment.standard_id == standard_id
            )
        )

        if status:
            query = query.filter(Alignment.status == status)

        return query.all()

    @staticmethod
    def get_alignments_for_objective(
        db: Session,
        objective_id: str,
        status: str = None
    ) -> List[Alignment]:
        """Get all alignments for a learning objective."""
        tenant_id = get_current_tenant_id()

        query = db.query(Alignment).filter(
            and_(
                Alignment.tenant_id == tenant_id,
                Alignment.objective_id == objective_id
            )
        )

        if status:
            query = query.filter(Alignment.status == status)

        return query.all()

    @staticmethod
    def list_candidate_alignments(
        db: Session,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Alignment], int]:
        """List all candidate alignments awaiting review."""
        tenant_id = get_current_tenant_id()

        total = db.query(Alignment).filter(
            and_(
                Alignment.tenant_id == tenant_id,
                Alignment.status == "candidate"
            )
        ).count()

        alignments = db.query(Alignment).filter(
            and_(
                Alignment.tenant_id == tenant_id,
                Alignment.status == "candidate"
            )
        ).order_by(Alignment.confidence.desc()).offset(skip).limit(limit).all()

        return alignments, total

    @staticmethod
    def bulk_create_alignments(
        db: Session,
        alignments_data: List[Dict[str, Any]]
    ) -> List[Alignment]:
        """Create multiple alignments at once."""
        created = []
        for alignment_data in alignments_data:
            try:
                alignment = AlignmentService.create_alignment(db, **alignment_data)
                created.append(alignment)
            except Exception as e:
                logger.error(f"Failed to create alignment: {str(e)}")
                continue

        return created

    @staticmethod
    def calculate_alignment_coverage(
        db: Session,
        source_type: str,
        source_id: str
    ) -> Dict[str, Any]:
        """
        Calculate alignment coverage for a source.

        Returns coverage statistics and recommendations.
        """
        tenant_id = get_current_tenant_id()

        alignments = db.query(Alignment).filter(
            and_(
                Alignment.tenant_id == tenant_id,
                Alignment.source_type == source_type,
                Alignment.source_id == source_id
            )
        ).all()

        if not alignments:
            return {
                "total_alignments": 0,
                "approved_count": 0,
                "candidate_count": 0,
                "rejected_count": 0,
                "average_confidence": 0.0,
                "average_score": 0.0,
                "coverage_status": "no_alignments"
            }

        approved = [a for a in alignments if a.status == "approved"]
        candidate = [a for a in alignments if a.status == "candidate"]
        rejected = [a for a in alignments if a.status == "rejected"]

        avg_confidence = (
            sum(a.confidence for a in alignments) / len(alignments)
            if alignments else 0.0
        )
        avg_score = (
            sum(a.score for a in alignments) / len(alignments)
            if alignments else 0.0
        )

        # Determine coverage status
        if len(approved) == 0:
            coverage_status = "no_alignments"
        elif len(approved) > 0 and len(candidate) == 0:
            coverage_status = "complete"
        elif len(candidate) > 0:
            coverage_status = "pending_review"
        else:
            coverage_status = "unknown"

        return {
            "total_alignments": len(alignments),
            "approved_count": len(approved),
            "candidate_count": len(candidate),
            "rejected_count": len(rejected),
            "average_confidence": round(avg_confidence, 3),
            "average_score": round(avg_score, 3),
            "coverage_status": coverage_status,
            "recommendations": AlignmentService._generate_recommendations(
                alignments, avg_confidence, approved
            )
        }

    @staticmethod
    def _generate_recommendations(
        alignments: List[Alignment],
        avg_confidence: float,
        approved: List[Alignment]
    ) -> List[str]:
        """Generate recommendations based on alignment metrics."""
        recommendations = []

        if len(approved) == 0:
            recommendations.append("No approved alignments yet. Start by reviewing candidate alignments.")

        if avg_confidence < 0.7:
            recommendations.append("Average confidence is low. Consider using stronger source content.")

        if len(alignments) < 3:
            recommendations.append("Only a few alignments created. Add more to improve coverage.")

        return recommendations
