"""
Database Persistence Service for Phase 4.

Handles saving skill alignments, recommendations, gap analysis,
and coverage reports to the database.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import (
    SkillAlignment, Recommendation, GapAnalysis,
    CoverageReport, AccessibilityAudit
)
import uuid

logger = logging.getLogger(__name__)


class DatabasePersistenceService:
    """Service for persisting workflow analysis results to database."""

    @staticmethod
    def save_skill_alignments(
        session: Session,
        tenant_id: str,
        workflow_id: str,
        alignments: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Save skill alignments to database.

        Args:
            session: Database session
            tenant_id: Tenant ID
            workflow_id: Workflow execution ID
            alignments: List of alignment data dicts

        Returns:
            List of created alignment IDs
        """
        created_ids = []

        try:
            for alignment_data in alignments:
                alignment = SkillAlignment(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    workflow_id=workflow_id,
                    skill_id=alignment_data.get('skill_id', ''),
                    skill_name=alignment_data.get('skill_name', ''),
                    content_id=alignment_data.get('content_id', ''),
                    content_title=alignment_data.get('content_title', ''),
                    alignment_type=alignment_data.get('alignment_type', 'covers'),
                    proficiency_level=alignment_data.get('proficiency_level', 'intermediate'),
                    confidence=float(alignment_data.get('confidence', 0.5)),
                    evidence=alignment_data.get('evidence', []),
                    supporting_objectives=alignment_data.get('supporting_objectives', []),
                    status='candidate',
                )
                session.add(alignment)
                created_ids.append(alignment.id)

            session.commit()
            logger.info(f"✓ Saved {len(created_ids)} skill alignments for workflow {workflow_id}")

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving alignments: {str(e)}")
            raise

        return created_ids

    @staticmethod
    def save_recommendations(
        session: Session,
        tenant_id: str,
        workflow_id: str,
        recommendations: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Save recommendations to database.

        Args:
            session: Database session
            tenant_id: Tenant ID
            workflow_id: Workflow execution ID
            recommendations: List of recommendation dicts

        Returns:
            List of created recommendation IDs
        """
        created_ids = []

        try:
            for rec_data in recommendations:
                recommendation = Recommendation(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    workflow_id=workflow_id,
                    type=rec_data.get('type', 'add_content'),
                    priority=rec_data.get('priority', 'medium'),
                    title=rec_data.get('title', ''),
                    description=rec_data.get('description', ''),
                    rationale=rec_data.get('rationale', ''),
                    implementation_steps=rec_data.get('implementation_steps', []),
                    affected_skills=rec_data.get('affected_skills', []),
                    estimated_effort=rec_data.get('estimated_effort', 'medium'),
                    expected_impact=rec_data.get('expected_impact'),
                    status='proposed',
                )
                session.add(recommendation)
                created_ids.append(recommendation.id)

            session.commit()
            logger.info(f"✓ Saved {len(created_ids)} recommendations for workflow {workflow_id}")

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving recommendations: {str(e)}")
            raise

        return created_ids

    @staticmethod
    def save_gap_analysis(
        session: Session,
        tenant_id: str,
        workflow_id: str,
        gaps: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Save gap analysis results to database.

        Args:
            session: Database session
            tenant_id: Tenant ID
            workflow_id: Workflow execution ID
            gaps: List of gap analysis dicts

        Returns:
            List of created gap analysis IDs
        """
        created_ids = []

        try:
            for gap_data in gaps:
                gap = GapAnalysis(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    workflow_id=workflow_id,
                    skill_id=gap_data.get('skill_id', ''),
                    skill_name=gap_data.get('skill_name', ''),
                    required_proficiency=gap_data.get('required_proficiency', 'intermediate'),
                    current_coverage=float(gap_data.get('current_coverage', 0.0)),
                    gap_severity=gap_data.get('gap_severity', 'medium'),
                    gap_description=gap_data.get('gap_description', ''),
                    recommendations=gap_data.get('recommendations', []),
                    status='identified',
                )
                session.add(gap)
                created_ids.append(gap.id)

            session.commit()
            logger.info(f"✓ Saved {len(created_ids)} gap analyses for workflow {workflow_id}")

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving gap analyses: {str(e)}")
            raise

        return created_ids

    @staticmethod
    def save_coverage_report(
        session: Session,
        tenant_id: str,
        workflow_id: str,
        coverage_data: Dict[str, Any],
    ) -> str:
        """
        Save coverage report to database.

        Args:
            session: Database session
            tenant_id: Tenant ID
            workflow_id: Workflow execution ID
            coverage_data: Coverage metrics dict

        Returns:
            Created report ID
        """
        try:
            report = CoverageReport(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                workflow_id=workflow_id,
                total_skills=coverage_data.get('total_skills', 0),
                total_content_items=coverage_data.get('total_content_items', 0),
                total_alignments=coverage_data.get('total_alignments', 0),
                covered_skills=coverage_data.get('covered_skills', []),
                partially_covered_skills=coverage_data.get('partially_covered_skills', []),
                uncovered_skills=coverage_data.get('uncovered_skills', []),
                coverage_by_skill=coverage_data.get('coverage_by_skill', {}),
                overall_coverage=float(coverage_data.get('overall_coverage', 0.0)),
                alignment_confidence=float(coverage_data.get('alignment_confidence', 0.0)),
                status='generated',
            )
            session.add(report)
            session.commit()

            logger.info(f"✓ Saved coverage report for workflow {workflow_id}")
            return report.id

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving coverage report: {str(e)}")
            raise

    @staticmethod
    def save_accessibility_audit(
        session: Session,
        tenant_id: str,
        workflow_id: str,
        audit_data: Dict[str, Any],
    ) -> str:
        """
        Save accessibility audit to database.

        Args:
            session: Database session
            tenant_id: Tenant ID
            workflow_id: Workflow execution ID
            audit_data: Audit findings dict

        Returns:
            Created audit ID
        """
        try:
            audit = AccessibilityAudit(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                workflow_id=workflow_id,
                scope=audit_data.get('scope', 'wcag-2.1-aa'),
                total_findings=audit_data.get('total_findings', 0),
                critical_issues=audit_data.get('critical_issues', 0),
                high_issues=audit_data.get('high_issues', 0),
                medium_issues=audit_data.get('medium_issues', 0),
                low_issues=audit_data.get('low_issues', 0),
                findings=audit_data.get('findings', []),
                remediation_steps=audit_data.get('remediation_steps', []),
                status='completed',
            )
            session.add(audit)
            session.commit()

            logger.info(f"✓ Saved accessibility audit for workflow {workflow_id}")
            return audit.id

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving accessibility audit: {str(e)}")
            raise

    @staticmethod
    def approve_alignment(
        session: Session,
        alignment_id: str,
        reviewed_by: str,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Approve a skill alignment.

        Args:
            session: Database session
            alignment_id: Alignment ID
            reviewed_by: User ID approving
            notes: Optional review notes

        Returns:
            True if successful
        """
        try:
            alignment = session.query(SkillAlignment).filter(
                SkillAlignment.id == alignment_id
            ).first()

            if not alignment:
                raise ValueError(f"Alignment {alignment_id} not found")

            alignment.status = 'approved'
            alignment.reviewed_by = reviewed_by
            alignment.reviewed_at = datetime.utcnow()
            alignment.review_notes = notes
            session.commit()

            logger.info(f"✓ Approved alignment {alignment_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error approving alignment: {str(e)}")
            raise

    @staticmethod
    def approve_recommendation(
        session: Session,
        recommendation_id: str,
        approved_by: str,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Approve a recommendation.

        Args:
            session: Database session
            recommendation_id: Recommendation ID
            approved_by: User ID approving
            notes: Optional approval notes

        Returns:
            True if successful
        """
        try:
            recommendation = session.query(Recommendation).filter(
                Recommendation.id == recommendation_id
            ).first()

            if not recommendation:
                raise ValueError(f"Recommendation {recommendation_id} not found")

            recommendation.status = 'approved'
            recommendation.approved_by = approved_by
            recommendation.approved_at = datetime.utcnow()
            recommendation.approval_notes = notes
            session.commit()

            logger.info(f"✓ Approved recommendation {recommendation_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error approving recommendation: {str(e)}")
            raise
