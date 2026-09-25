"""Standards API endpoints - browse frameworks and standards."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from database.models import StandardFramework, Standard
from pydantic import BaseModel

router = APIRouter(prefix="/v1/standards", tags=["standards"])


# Response models
class StandardResponse(BaseModel):
    id: str
    code: str
    description: str
    grade: Optional[str] = None
    subject: Optional[str] = None
    domain: Optional[str] = None
    strand: Optional[str] = None
    version: Optional[str] = None

    class Config:
        from_attributes = True


class StandardFrameworkResponse(BaseModel):
    id: str
    name: str
    authority: Optional[str] = None
    jurisdiction: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class StandardHierarchyItem(BaseModel):
    id: str
    code: str
    label: str
    children: List["StandardHierarchyItem"] = []


StandardHierarchyItem.model_rebuild()


class StandardHierarchyResponse(BaseModel):
    framework: StandardFrameworkResponse
    standards: List[StandardResponse]
    hierarchy: List[StandardHierarchyItem]


# ==================== Framework Endpoints ====================

@router.get("/frameworks", response_model=List[StandardFrameworkResponse])
async def list_frameworks(db: Session = Depends(get_db)):
    """List all standard frameworks."""
    frameworks = db.query(StandardFramework).all()
    return frameworks


@router.get("/frameworks/{framework_id}", response_model=StandardFrameworkResponse)
async def get_framework(framework_id: str, db: Session = Depends(get_db)):
    """Get a specific standard framework."""
    framework = db.query(StandardFramework).filter(
        StandardFramework.id == framework_id
    ).first()

    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    return framework


# ==================== Standards Endpoints ====================

@router.get("/frameworks/{framework_id}/standards", response_model=List[StandardResponse])
async def get_framework_standards(
    framework_id: str,
    grade: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all standards in a framework, with optional grade/subject filtering."""
    # Verify framework exists
    framework = db.query(StandardFramework).filter(
        StandardFramework.id == framework_id
    ).first()

    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    # Query standards
    query = db.query(Standard).filter(Standard.framework_id == framework_id)

    if grade:
        query = query.filter(Standard.grade == grade)
    if subject:
        query = query.filter(Standard.subject == subject)

    standards = query.order_by(Standard.code).all()
    return standards


@router.get("/{standard_id}", response_model=StandardResponse)
async def get_standard(standard_id: str, db: Session = Depends(get_db)):
    """Get a specific standard."""
    standard = db.query(Standard).filter(Standard.id == standard_id).first()

    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")

    return standard


@router.get("/frameworks/{framework_id}/by-grade-subject", response_model=List[StandardResponse])
async def get_standards_by_grade_subject(
    framework_id: str,
    grade: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get standards filtered by grade and/or subject."""
    # Verify framework exists
    framework = db.query(StandardFramework).filter(
        StandardFramework.id == framework_id
    ).first()

    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    # Query standards
    query = db.query(Standard).filter(Standard.framework_id == framework_id)

    if grade:
        query = query.filter(Standard.grade == grade)
    if subject:
        query = query.filter(Standard.subject == subject)

    standards = query.order_by(Standard.code).all()
    return standards


@router.get("/search", response_model=List[StandardResponse])
async def search_standards(
    q: Optional[str] = Query(None),
    framework_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search standards by code or description."""
    query = db.query(Standard)

    if framework_id:
        query = query.filter(Standard.framework_id == framework_id)

    if q:
        # Search in code and description (case-insensitive)
        search_term = f"%{q.lower()}%"
        query = query.filter(
            (Standard.code.ilike(search_term)) |
            (Standard.description.ilike(search_term))
        )

    standards = query.order_by(Standard.code).limit(50).all()
    return standards


# ==================== Hierarchy Endpoints ====================

@router.get("/frameworks/{framework_id}/hierarchy", response_model=StandardHierarchyResponse)
async def get_standard_hierarchy(framework_id: str, db: Session = Depends(get_db)):
    """Get standards organized in a hierarchical structure by grade."""
    # Fetch framework
    framework = db.query(StandardFramework).filter(
        StandardFramework.id == framework_id
    ).first()

    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    # Fetch all standards
    standards = db.query(Standard).filter(
        Standard.framework_id == framework_id
    ).order_by(Standard.code).all()

    # Group by grade
    standards_by_grade = {}
    for std in standards:
        grade = std.grade or "Ungrouped"
        if grade not in standards_by_grade:
            standards_by_grade[grade] = []
        standards_by_grade[grade].append(std)

    # Build hierarchy (group by grade and domain)
    grade_order = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "9-10", "10", "11", "11-12", "12", "Ungrouped"]

    hierarchy_items = []
    for grade in grade_order:
        if grade not in standards_by_grade:
            continue

        grade_standards = standards_by_grade[grade]

        # Group by domain within grade
        domains = {}
        for std in grade_standards:
            domain = std.domain or "General"
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(std)

        # Build grade item with domain children
        domain_items = []
        for domain_name in sorted(domains.keys()):
            domain_stds = domains[domain_name]
            standard_items = [
                StandardHierarchyItem(
                    id=std.id,
                    code=std.code,
                    label=f"{std.code}: {std.description[:60]}..."
                )
                for std in domain_stds
            ]
            domain_items.append(
                StandardHierarchyItem(
                    id=f"domain_{grade}_{domain_name}",
                    code=domain_name,
                    label=f"{domain_name} ({len(domain_stds)})",
                    children=standard_items
                )
            )

        grade_item = StandardHierarchyItem(
            id=f"grade_{grade}",
            code=grade,
            label=f"Grade {grade} ({len(grade_standards)})",
            children=domain_items
        )
        hierarchy_items.append(grade_item)

    return StandardHierarchyResponse(
        framework=StandardFrameworkResponse.model_validate(framework),
        standards=[StandardResponse.model_validate(s) for s in standards],
        hierarchy=hierarchy_items
    )
