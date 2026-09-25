"""
Data Access API Routes - Content, Curriculum, and Alignment
Provides database-backed endpoints with proper tenant isolation.
Standards endpoints are handled by api/standards.py router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from database.db import get_db
from database.models import (
    Content, Curriculum, CurriculumUnit, LearningObjective
)
from auth.tenant_context import get_current_tenant_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["data-access"])


# ===== CONTENT LIBRARY ENDPOINTS =====

@router.get("/content")
async def list_content(
    page: int = 0,
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all content from database with proper tenant filtering."""
    try:
        tenant_id = get_current_tenant_id()
        logger.info(f"[GET /content] tenant_id={tenant_id}, page={page}, skip={skip}, limit={limit}")

        # The UI uses one-based page numbers; preserve skip for page-zero callers.
        actual_skip = ((page - 1) * limit) if page > 0 else skip

        query = db.query(Content).filter(Content.tenant_id == tenant_id)
        logger.info(f"[GET /content] Filtered by tenant_id")

        if status_filter:
            query = query.filter(Content.status == status_filter)
            logger.info(f"[GET /content] Applied status filter: {status_filter}")

        total = query.count()
        logger.info(f"[GET /content] Total count: {total}")

        content_items = query.order_by(Content.created_at.desc()).offset(actual_skip).limit(limit).all()
        logger.info(f"[GET /content] Retrieved {len(content_items)} items")

        return {
            "status": "success",
            "total": total,
            "pages": (total + limit - 1) // limit if limit > 0 else 0,
            "items": [
                {
                    "id": c.id,
                    "tenant_id": c.tenant_id,
                    "title": c.title,
                    "content_type": c.content_type,
                    "source_url": c.source,
                    "status": c.status,
                    "version": c.version,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in content_items
            ],
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"[GET /content] Error: {str(e)}", exc_info=True)
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
                "type": content.content_type,
                "source": content.source,
                "status": content.status,
                "version": content.version,
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

def _iso(dt):
    return dt.isoformat() if dt else None


def _curriculum_dict(c: Curriculum) -> Dict[str, Any]:
    return {
        "id": c.id,
        "tenant_id": c.tenant_id,
        "name": c.name,
        "description": c.description or "",
        "version": c.version,
        "grade": c.grade,
        "subject": c.subject,
        "status": c.status,
        "created_at": _iso(c.created_at),
        "updated_at": _iso(c.updated_at),
    }


def _unit_dict(u: CurriculumUnit) -> Dict[str, Any]:
    return {
        "id": u.id,
        "tenant_id": u.tenant_id,
        "curriculum_id": u.curriculum_id,
        "parent_id": u.parent_id,
        "title": u.title,
        "description": u.description,
        "sequence": u.sequence,
        "created_at": _iso(u.created_at),
        "updated_at": _iso(u.updated_at),
    }


def _objective_dict(o: LearningObjective) -> Dict[str, Any]:
    return {
        "id": o.id,
        "tenant_id": o.tenant_id,
        "unit_id": o.unit_id,
        "objective": o.objective,
        "cognitive_level": o.cognitive_level,
        "created_at": _iso(o.created_at),
        "updated_at": _iso(o.updated_at),
    }


def _get_curriculum_or_404(db: Session, curriculum_id: str, tenant_id: str) -> Curriculum:
    curriculum = db.query(Curriculum).filter(
        Curriculum.id == curriculum_id,
        Curriculum.tenant_id == tenant_id,
    ).first()
    if not curriculum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curriculum not found")
    return curriculum


@router.get("/curricula", tags=["curriculum"])
async def list_curricula(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    tenant_id = get_current_tenant_id()
    curricula = (
        db.query(Curriculum)
        .filter(Curriculum.tenant_id == tenant_id)
        .order_by(Curriculum.created_at.desc())
        .all()
    )
    return [_curriculum_dict(c) for c in curricula]


@router.get("/curricula/{curriculum_id}", tags=["curriculum"])
async def get_curriculum(curriculum_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    tenant_id = get_current_tenant_id()
    return _curriculum_dict(_get_curriculum_or_404(db, curriculum_id, tenant_id))


@router.get("/curricula/{curriculum_id}/units", tags=["curriculum"])
async def list_curriculum_units(curriculum_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    tenant_id = get_current_tenant_id()
    _get_curriculum_or_404(db, curriculum_id, tenant_id)
    units = (
        db.query(CurriculumUnit)
        .filter(CurriculumUnit.curriculum_id == curriculum_id, CurriculumUnit.tenant_id == tenant_id)
        .order_by(CurriculumUnit.sequence)
        .all()
    )
    return [_unit_dict(u) for u in units]


@router.get("/curricula/{curriculum_id}/structure", tags=["curriculum"])
async def get_curriculum_structure(curriculum_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    tenant_id = get_current_tenant_id()
    curriculum = _get_curriculum_or_404(db, curriculum_id, tenant_id)
    units = (
        db.query(CurriculumUnit)
        .filter(CurriculumUnit.curriculum_id == curriculum_id, CurriculumUnit.tenant_id == tenant_id)
        .order_by(CurriculumUnit.sequence)
        .all()
    )
    unit_ids = [u.id for u in units]
    objectives = (
        db.query(LearningObjective)
        .filter(LearningObjective.unit_id.in_(unit_ids), LearningObjective.tenant_id == tenant_id)
        .all()
        if unit_ids else []
    )
    return {
        "curriculum": _curriculum_dict(curriculum),
        "units": [_unit_dict(u) for u in units],
        "objectives": [_objective_dict(o) for o in objectives],
    }


@router.get("/curriculum-units/{unit_id}/objectives", tags=["curriculum"])
async def list_unit_objectives(unit_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    tenant_id = get_current_tenant_id()
    objectives = (
        db.query(LearningObjective)
        .filter(LearningObjective.unit_id == unit_id, LearningObjective.tenant_id == tenant_id)
        .all()
    )
    return [_objective_dict(o) for o in objectives]


@router.get("/learning-objectives", tags=["curriculum"])
async def list_learning_objectives(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    tenant_id = get_current_tenant_id()
    objectives = db.query(LearningObjective).filter(LearningObjective.tenant_id == tenant_id).all()
    return [_objective_dict(o) for o in objectives]
