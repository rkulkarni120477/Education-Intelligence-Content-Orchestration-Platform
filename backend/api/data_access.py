"""
Data Access API Routes - Content, Curriculum, and Alignment
Provides database-backed endpoints with proper tenant isolation.
Standards endpoints are handled by api/standards.py router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from database.db import get_db
from database.models import (
    Content, ContentChunk, Curriculum, CurriculumUnit, Alignment
)
from auth.tenant_context import get_current_tenant_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["data-access"])


# ===== CONTENT LIBRARY ENDPOINTS =====

@router.get("/content")
async def list_content(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all content from database with proper tenant filtering."""
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(Content).filter(Content.tenant_id == tenant_id)

        if status:
            query = query.filter(Content.status == status)

        if subject:
            query = query.filter(Content.subject == subject)

        total = query.count()
        content_items = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()

        return {
            "status": "success",
            "total": total,
            "items": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "type": c.content_type,
                    "subject": c.subject,
                    "grade": c.grade_level,
                    "status": c.status,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in content_items
            ],
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/content/{content_id}")
async def get_content_detail(
    content_id: str,
    db: Session = Depends(get_db),
):
    """Get detailed content information."""
    try:
        tenant_id = get_current_tenant_id()

        content = db.query(Content).filter(
            Content.id == content_id,
            Content.tenant_id == tenant_id
        ).first()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        return {
            "status": "success",
            "content": {
                "id": content.id,
                "title": content.title,
                "description": content.description,
                "type": content.content_type,
                "subject": content.subject,
                "grade": content.grade_level,
                "status": content.status,
                "created_at": content.created_at.isoformat() if content.created_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== CURRICULUM ENDPOINTS =====

@router.get("/curriculum")
async def list_curriculum(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all curriculum with proper tenant filtering."""
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(Curriculum).filter(Curriculum.tenant_id == tenant_id)

        if status_filter:
            query = query.filter(Curriculum.status == status_filter)

        total = query.count()
        curriculum = query.order_by(Curriculum.created_at.desc()).offset(skip).limit(limit).all()

        return {
            "status": "success",
            "total": total,
            "items": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "subject": c.subject,
                    "grade_level": c.grade_level,
                    "status": c.status,
                    "version": c.version,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in curriculum
            ],
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing curriculum: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/curriculum/{curriculum_id}")
async def get_curriculum_detail(
    curriculum_id: str,
    db: Session = Depends(get_db),
):
    """Get curriculum with all units."""
    try:
        tenant_id = get_current_tenant_id()

        curriculum = db.query(Curriculum).filter(
            Curriculum.id == curriculum_id,
            Curriculum.tenant_id == tenant_id
        ).first()

        if not curriculum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Curriculum not found"
            )

        units = db.query(CurriculumUnit).filter(
            CurriculumUnit.curriculum_id == curriculum_id,
            CurriculumUnit.tenant_id == tenant_id
        ).order_by(CurriculumUnit.sequence).all()

        return {
            "status": "success",
            "curriculum": {
                "id": curriculum.id,
                "title": curriculum.title,
                "description": curriculum.description,
                "subject": curriculum.subject,
                "grade_level": curriculum.grade_level,
                "status": curriculum.status,
                "version": curriculum.version,
                "units": [
                    {
                        "id": u.id,
                        "title": u.title,
                        "description": u.description,
                        "sequence": u.sequence,
                        "content_id": u.content_id,
                    }
                    for u in units
                ],
                "created_at": curriculum.created_at.isoformat() if curriculum.created_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting curriculum: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== ALIGNMENT ENDPOINTS (FIXED) =====

@router.get("/alignments-list")
async def list_all_alignments(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    source_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all alignments from database with proper tenant filtering.
    Shows all statuses by default (no automatic filtering).
    """
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(Alignment).filter(Alignment.tenant_id == tenant_id)

        if status_filter:
            query = query.filter(Alignment.status == status_filter)

        if source_type:
            query = query.filter(Alignment.source_type == source_type)

        total = query.count()
        alignments = query.order_by(Alignment.confidence.desc()).offset(skip).limit(limit).all()

        return {
            "status": "success",
            "total": total,
            "items": [
                {
                    "id": a.id,
                    "source_type": a.source_type,
                    "source_id": a.source_id,
                    "target_type": a.target_type,
                    "standard_id": a.standard_id,
                    "objective_id": a.objective_id,
                    "score": float(a.score) if a.score else 0.0,
                    "confidence": float(a.confidence) if a.confidence else 0.0,
                    "evidence": a.evidence or [],
                    "status": a.status,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in alignments
            ],
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing alignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
