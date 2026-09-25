"""
Skill Mapping & Recommendations API Routes (Phase 4).

Endpoints for managing skill alignments, recommendations, gap analysis,
and coverage reports.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from database.db import get_db
from auth.tenant_context import get_current_tenant_id
from database.models import (
    SkillAlignment, Recommendation, GapAnalysis, CoverageReport,
    AccessibilityAudit
)
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/skill-mapping", tags=["skill-mapping"])


# ===== REQUEST/RESPONSE MODELS =====

class SkillAlignmentResponse(BaseModel):
    """Response model for a skill alignment."""
    id: str
    skill_id: str
    skill_name: str
    content_id: str
    content_title: str
    alignment_type: str
    proficiency_level: str
    confidence: float
    evidence: List[Dict[str, str]]
    status: str


class RecommendationResponse(BaseModel):
    """Response model for a recommendation."""
    id: str
    type: str
    priority: str
    title: str
    description: str
    rationale: str
    implementation_steps: List[str]
    affected_skills: List[str]
    estimated_effort: str
    expected_impact: Optional[str]
    status: str


class CoverageReportResponse(BaseModel):
    """Response model for coverage report."""
    id: str
    total_skills: int
    total_alignments: int
    covered_skills: List[str]
    partially_covered_skills: List[str]
    uncovered_skills: List[str]
    overall_coverage: float
    alignment_confidence: float


class GapAnalysisResponse(BaseModel):
    """Response model for gap analysis."""
    id: str
    skill_id: str
    skill_name: str
    required_proficiency: str
    current_coverage: float
    gap_severity: str
    gap_description: str
    recommendations: List[Dict[str, str]]


class ApproveAlignmentRequest(BaseModel):
    """Request to approve a skill alignment."""
    approval_notes: Optional[str] = Field(None, description="Notes on approval")


class ApproveRecommendationRequest(BaseModel):
    """Request to approve a recommendation."""
    approval_notes: Optional[str] = Field(None, description="Notes on approval")


class UpdateRecommendationRequest(BaseModel):
    """Request to update a recommendation."""
    status: Optional[str] = Field(None, description="New status")
    implementation_notes: Optional[str] = Field(None, description="Implementation notes")


# ===== SKILL ALIGNMENT ENDPOINTS =====

@router.get("/workflows/{workflow_id}/alignments")
async def get_skill_alignments(
    workflow_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all skill alignments for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(SkillAlignment).filter(
            SkillAlignment.tenant_id == tenant_id,
            SkillAlignment.workflow_id == workflow_id,
        )

        if status:
            query = query.filter(SkillAlignment.status == status)

        alignments = query.all()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "alignments": [
                {
                    "id": a.id,
                    "skill_id": a.skill_id,
                    "skill_name": a.skill_name,
                    "content_id": a.content_id,
                    "content_title": a.content_title,
                    "alignment_type": a.alignment_type,
                    "proficiency_level": a.proficiency_level,
                    "confidence": a.confidence,
                    "status": a.status,
                }
                for a in alignments
            ],
            "total": len(alignments),
        }

    except Exception as e:
        logger.error(f"Error getting alignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/workflows/{workflow_id}/alignments/{alignment_id}/approve")
async def approve_alignment(
    workflow_id: str,
    alignment_id: str,
    request: ApproveAlignmentRequest,
    db: Session = Depends(get_db),
):
    """Approve a skill alignment."""
    try:
        tenant_id = get_current_tenant_id()

        alignment = db.query(SkillAlignment).filter(
            SkillAlignment.id == alignment_id,
            SkillAlignment.tenant_id == tenant_id,
            SkillAlignment.workflow_id == workflow_id,
        ).first()

        if not alignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alignment not found"
            )

        alignment.status = "approved"
        alignment.reviewed_at = datetime.utcnow()
        alignment.review_notes = request.approval_notes
        db.commit()

        logger.info(f"✓ Alignment {alignment_id} approved")

        return {
            "status": "success",
            "message": "Alignment approved",
            "alignment_id": alignment_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving alignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== RECOMMENDATION ENDPOINTS =====

@router.get("/workflows/{workflow_id}/recommendations")
async def get_recommendations(
    workflow_id: str,
    priority: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all recommendations for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(Recommendation).filter(
            Recommendation.tenant_id == tenant_id,
            Recommendation.workflow_id == workflow_id,
        )

        if priority:
            query = query.filter(Recommendation.priority == priority)

        if status_filter:
            query = query.filter(Recommendation.status == status_filter)

        recommendations = query.order_by(
            Recommendation.priority.asc(),
        ).all()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "recommendations": [
                {
                    "id": r.id,
                    "type": r.type,
                    "priority": r.priority,
                    "title": r.title,
                    "description": r.description,
                    "rationale": r.rationale,
                    "affected_skills": r.affected_skills,
                    "estimated_effort": r.estimated_effort,
                    "status": r.status,
                }
                for r in recommendations
            ],
            "total": len(recommendations),
        }

    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/workflows/{workflow_id}/recommendations/{recommendation_id}/approve")
async def approve_recommendation(
    workflow_id: str,
    recommendation_id: str,
    request: ApproveRecommendationRequest,
    db: Session = Depends(get_db),
):
    """Approve a recommendation."""
    try:
        tenant_id = get_current_tenant_id()

        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id,
            Recommendation.tenant_id == tenant_id,
            Recommendation.workflow_id == workflow_id,
        ).first()

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )

        recommendation.status = "approved"
        recommendation.approved_at = datetime.utcnow()
        recommendation.approval_notes = request.approval_notes
        db.commit()

        logger.info(f"✓ Recommendation {recommendation_id} approved")

        return {
            "status": "success",
            "message": "Recommendation approved",
            "recommendation_id": recommendation_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving recommendation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/workflows/{workflow_id}/recommendations/{recommendation_id}")
async def update_recommendation(
    workflow_id: str,
    recommendation_id: str,
    request: UpdateRecommendationRequest,
    db: Session = Depends(get_db),
):
    """Update a recommendation's status or notes."""
    try:
        tenant_id = get_current_tenant_id()

        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id,
            Recommendation.tenant_id == tenant_id,
            Recommendation.workflow_id == workflow_id,
        ).first()

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )

        if request.status:
            recommendation.status = request.status

        if request.implementation_notes:
            recommendation.implementation_notes = request.implementation_notes
            recommendation.implemented_at = datetime.utcnow()

        db.commit()

        return {
            "status": "success",
            "message": "Recommendation updated",
            "recommendation_id": recommendation_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating recommendation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== GAP ANALYSIS ENDPOINTS =====

@router.get("/workflows/{workflow_id}/gaps")
async def get_gap_analysis(
    workflow_id: str,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all identified gaps for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(GapAnalysis).filter(
            GapAnalysis.tenant_id == tenant_id,
            GapAnalysis.workflow_id == workflow_id,
        )

        if severity:
            query = query.filter(GapAnalysis.gap_severity == severity)

        gaps = query.order_by(GapAnalysis.gap_severity.asc()).all()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "gaps": [
                {
                    "id": g.id,
                    "skill_id": g.skill_id,
                    "skill_name": g.skill_name,
                    "required_proficiency": g.required_proficiency,
                    "current_coverage": g.current_coverage,
                    "gap_severity": g.gap_severity,
                    "gap_description": g.gap_description,
                    "recommendations": g.recommendations,
                }
                for g in gaps
            ],
            "total": len(gaps),
        }

    except Exception as e:
        logger.error(f"Error getting gaps: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== COVERAGE REPORT ENDPOINTS =====

@router.get("/workflows/{workflow_id}/coverage")
async def get_coverage_report(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """Get skill coverage report for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        report = db.query(CoverageReport).filter(
            CoverageReport.tenant_id == tenant_id,
            CoverageReport.workflow_id == workflow_id,
        ).order_by(CoverageReport.created_at.desc()).first()

        if not report:
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "coverage": None,
                "message": "No coverage report generated yet",
            }

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "coverage": {
                "id": report.id,
                "total_skills": report.total_skills,
                "total_alignments": report.total_alignments,
                "covered_skills": report.covered_skills,
                "partially_covered_skills": report.partially_covered_skills,
                "uncovered_skills": report.uncovered_skills,
                "overall_coverage": report.overall_coverage,
                "alignment_confidence": report.alignment_confidence,
                "coverage_by_skill": report.coverage_by_skill,
            }
        }

    except Exception as e:
        logger.error(f"Error getting coverage report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== ACCESSIBILITY AUDIT ENDPOINTS =====

@router.get("/workflows/{workflow_id}/accessibility")
async def get_accessibility_audit(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """Get accessibility audit for a workflow."""
    try:
        tenant_id = get_current_tenant_id()

        audit = db.query(AccessibilityAudit).filter(
            AccessibilityAudit.tenant_id == tenant_id,
            AccessibilityAudit.workflow_id == workflow_id,
        ).order_by(AccessibilityAudit.created_at.desc()).first()

        if not audit:
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "audit": None,
                "message": "No accessibility audit performed yet",
            }

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "audit": {
                "id": audit.id,
                "scope": audit.scope,
                "total_findings": audit.total_findings,
                "critical_issues": audit.critical_issues,
                "high_issues": audit.high_issues,
                "medium_issues": audit.medium_issues,
                "low_issues": audit.low_issues,
                "findings": audit.findings,
                "remediation_complete": audit.remediation_complete,
                "status": audit.status,
            }
        }

    except Exception as e:
        logger.error(f"Error getting accessibility audit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
