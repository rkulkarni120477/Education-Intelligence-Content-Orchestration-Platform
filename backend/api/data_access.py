"""
Data Access API Routes - Content Library, Standards, Curriculum, and Alignment
Fixes for displaying existing data with proper tenant isolation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from database.db import get_db
from database.models import (
    Content, ContentChunk, StandardFramework, Standard,
    Curriculum, CurriculumUnit, Alignment, CurriculumWorkflow
)
from auth.tenant_context import get_current_tenant_id
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/data", tags=["data-access"])


# ===== CONTENT LIBRARY ENDPOINTS =====

@router.get("/content")
async def list_content(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all content from the content library with proper tenant filtering.
    """
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
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
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
    """Get detailed content information including chunks."""
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

        chunks = db.query(ContentChunk).filter(
            ContentChunk.content_id == content_id,
            ContentChunk.tenant_id == tenant_id
        ).all()

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
                "source_url": content.source_url,
                "created_at": content.created_at.isoformat() if content.created_at else None,
                "chunks": [
                    {
                        "id": ch.id,
                        "title": ch.title,
                        "text": ch.text,
                        "position": ch.position,
                    }
                    for ch in chunks
                ]
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


# ===== STANDARDS ENDPOINTS =====

@router.get("/standards")
async def list_standards(
    skip: int = 0,
    limit: int = 50,
    framework_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all standards with proper tenant filtering."""
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(Standard).filter(Standard.tenant_id == tenant_id)

        if framework_id:
            query = query.filter(Standard.framework_id == framework_id)

        total = query.count()
        standards = query.order_by(Standard.code).offset(skip).limit(limit).all()

        return {
            "status": "success",
            "total": total,
            "items": [
                {
                    "id": s.id,
                    "code": s.code,
                    "title": s.title,
                    "description": s.description,
                    "framework_id": s.framework_id,
                    "level": s.level,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in standards
            ],
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing standards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/standards/frameworks")
async def list_frameworks(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all standard frameworks."""
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(StandardFramework).filter(
            StandardFramework.tenant_id == tenant_id
        )

        total = query.count()
        frameworks = query.order_by(StandardFramework.name).offset(skip).limit(limit).all()

        return {
            "status": "success",
            "total": total,
            "items": [
                {
                    "id": f.id,
                    "name": f.name,
                    "code": f.code,
                    "description": f.description,
                    "source": f.source,
                    "version": f.version,
                    "created_at": f.created_at.isoformat() if f.created_at else None,
                }
                for f in frameworks
            ],
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing frameworks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== CURRICULUM ENDPOINTS =====

@router.get("/curriculum")
async def list_curriculum(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all curriculum with proper tenant filtering."""
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(Curriculum).filter(Curriculum.tenant_id == tenant_id)

        if status:
            query = query.filter(Curriculum.status == status)

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

@router.get("/alignments")
async def list_alignments(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    source_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all alignments with proper tenant filtering.
    FIXED: Shows all statuses by default, not just 'candidate'
    """
    try:
        tenant_id = get_current_tenant_id()

        query = db.query(Alignment).filter(Alignment.tenant_id == tenant_id)

        # Only filter by status if explicitly provided
        if status:
            query = query.filter(Alignment.status == status)

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
                    "reviewed_at": a.reviewed_at.isoformat() if a.reviewed_at else None,
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


@router.get("/alignments/{alignment_id}")
async def get_alignment(
    alignment_id: str,
    db: Session = Depends(get_db),
):
    """Get alignment details."""
    try:
        tenant_id = get_current_tenant_id()

        alignment = db.query(Alignment).filter(
            Alignment.id == alignment_id,
            Alignment.tenant_id == tenant_id
        ).first()

        if not alignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alignment not found"
            )

        return {
            "status": "success",
            "alignment": {
                "id": alignment.id,
                "source_type": alignment.source_type,
                "source_id": alignment.source_id,
                "target_type": alignment.target_type,
                "standard_id": alignment.standard_id,
                "objective_id": alignment.objective_id,
                "score": float(alignment.score) if alignment.score else 0.0,
                "confidence": float(alignment.confidence) if alignment.confidence else 0.0,
                "evidence": alignment.evidence or [],
                "status": alignment.status,
                "created_at": alignment.created_at.isoformat() if alignment.created_at else None,
                "reviewed_at": alignment.reviewed_at.isoformat() if alignment.reviewed_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
