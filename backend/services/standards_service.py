"""
Standards intelligence service.

Manages standard frameworks, standards, and their relationships.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models import StandardFramework, Standard
from auth.tenant_context import get_current_tenant_id
from typing import List, Optional, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class StandardsService:
    """Service for standards management and intelligence."""

    @staticmethod
    def create_framework(
        db: Session,
        name: str,
        authority: str,
        jurisdiction: str,
        version: str = "1.0",
        description: str = None
    ) -> StandardFramework:
        """Create a new standards framework."""
        tenant_id = get_current_tenant_id()

        # Check if framework already exists
        existing = db.query(StandardFramework).filter(
            and_(
                StandardFramework.tenant_id == tenant_id,
                StandardFramework.name == name,
                StandardFramework.version == version
            )
        ).first()

        if existing:
            raise ValueError(f"Framework '{name}' v{version} already exists in this tenant")

        framework = StandardFramework(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            authority=authority,
            jurisdiction=jurisdiction,
            version=version,
            description=description
        )
        db.add(framework)
        db.commit()
        db.refresh(framework)
        logger.info(f"Created framework: {framework.id} ({name} v{version})")
        return framework

    @staticmethod
    def create_standard(
        db: Session,
        framework_id: str,
        code: str,
        description: str,
        grade: str = None,
        subject: str = None,
        domain: str = None,
        strand: str = None,
        parent_id: str = None
    ) -> Standard:
        """Create a new standard within a framework."""
        tenant_id = get_current_tenant_id()

        # Verify framework exists and belongs to tenant
        framework = db.query(StandardFramework).filter(
            and_(
                StandardFramework.id == framework_id,
                StandardFramework.tenant_id == tenant_id
            )
        ).first()

        if not framework:
            raise ValueError(f"Framework {framework_id} not found in this tenant")

        # Verify parent exists if provided
        if parent_id:
            parent = db.query(Standard).filter(
                and_(
                    Standard.id == parent_id,
                    Standard.tenant_id == tenant_id,
                    Standard.framework_id == framework_id
                )
            ).first()
            if not parent:
                raise ValueError(f"Parent standard {parent_id} not found")

        # Check if standard already exists
        existing = db.query(Standard).filter(
            and_(
                Standard.tenant_id == tenant_id,
                Standard.framework_id == framework_id,
                Standard.code == code
            )
        ).first()

        if existing:
            raise ValueError(f"Standard {code} already exists in this framework")

        standard = Standard(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            framework_id=framework_id,
            parent_id=parent_id,
            code=code,
            description=description,
            grade=grade,
            subject=subject,
            domain=domain,
            strand=strand,
            version=framework.version
        )
        db.add(standard)
        db.commit()
        db.refresh(standard)
        logger.info(f"Created standard: {standard.id} ({code})")
        return standard

    @staticmethod
    def get_framework(db: Session, framework_id: str) -> StandardFramework:
        """Get a framework by ID."""
        tenant_id = get_current_tenant_id()

        framework = db.query(StandardFramework).filter(
            and_(
                StandardFramework.id == framework_id,
                StandardFramework.tenant_id == tenant_id
            )
        ).first()

        if not framework:
            raise ValueError(f"Framework {framework_id} not found")

        return framework

    @staticmethod
    def list_frameworks(db: Session, skip: int = 0, limit: int = 50) -> tuple[List[StandardFramework], int]:
        """List all frameworks for the tenant."""
        tenant_id = get_current_tenant_id()

        total = db.query(StandardFramework).filter(
            StandardFramework.tenant_id == tenant_id
        ).count()

        frameworks = db.query(StandardFramework).filter(
            StandardFramework.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

        return frameworks, total

    @staticmethod
    def list_standards(
        db: Session,
        framework_id: str = None,
        grade: str = None,
        subject: str = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Standard], int]:
        """List standards with optional filtering."""
        tenant_id = get_current_tenant_id()

        query = db.query(Standard).filter(Standard.tenant_id == tenant_id)

        if framework_id:
            query = query.filter(Standard.framework_id == framework_id)
        if grade:
            query = query.filter(Standard.grade == grade)
        if subject:
            query = query.filter(Standard.subject == subject)

        total = query.count()
        standards = query.offset(skip).limit(limit).all()

        return standards, total

    @staticmethod
    def search_standards(
        db: Session,
        query_text: str,
        framework_id: str = None,
        limit: int = 20
    ) -> List[Standard]:
        """Search standards by text (code or description)."""
        tenant_id = get_current_tenant_id()

        query = db.query(Standard).filter(
            and_(
                Standard.tenant_id == tenant_id,
                Standard.code.ilike(f"%{query_text}%") |
                Standard.description.ilike(f"%{query_text}%")
            )
        )

        if framework_id:
            query = query.filter(Standard.framework_id == framework_id)

        return query.limit(limit).all()

    @staticmethod
    def get_standard_hierarchy(db: Session, standard_id: str) -> Dict[str, Any]:
        """Get the full hierarchy of a standard (parent and children)."""
        tenant_id = get_current_tenant_id()

        standard = db.query(Standard).filter(
            and_(
                Standard.id == standard_id,
                Standard.tenant_id == tenant_id
            )
        ).first()

        if not standard:
            raise ValueError(f"Standard {standard_id} not found")

        # Get parent chain
        parents = []
        current = standard
        while current.parent_id:
            current = db.query(Standard).filter(
                Standard.id == current.parent_id
            ).first()
            if current:
                parents.insert(0, current)

        # Get children
        children = db.query(Standard).filter(
            and_(
                Standard.tenant_id == tenant_id,
                Standard.parent_id == standard_id
            )
        ).all()

        return {
            "standard": standard,
            "parents": parents,
            "children": children
        }

    @staticmethod
    def get_standards_by_grade_subject(
        db: Session,
        grade: str,
        subject: str,
        framework_id: str = None
    ) -> List[Standard]:
        """Get all standards for a specific grade and subject."""
        tenant_id = get_current_tenant_id()

        query = db.query(Standard).filter(
            and_(
                Standard.tenant_id == tenant_id,
                Standard.grade == grade,
                Standard.subject == subject
            )
        )

        if framework_id:
            query = query.filter(Standard.framework_id == framework_id)

        return query.all()
