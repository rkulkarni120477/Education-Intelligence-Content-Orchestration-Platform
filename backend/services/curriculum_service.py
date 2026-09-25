"""
Curriculum intelligence service.

Manages curricula, units, and learning objectives.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models import Curriculum, CurriculumUnit, LearningObjective
from auth.tenant_context import get_current_tenant_id
from typing import List, Optional, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class CurriculumService:
    """Service for curriculum management and intelligence."""

    @staticmethod
    def create_curriculum(
        db: Session,
        name: str,
        grade: str = None,
        subject: str = None,
        description: str = None,
        version: str = "1.0"
    ) -> Curriculum:
        """Create a new curriculum."""
        tenant_id = get_current_tenant_id()

        # Check if curriculum already exists
        existing = db.query(Curriculum).filter(
            and_(
                Curriculum.tenant_id == tenant_id,
                Curriculum.name == name,
                Curriculum.version == version
            )
        ).first()

        if existing:
            raise ValueError(f"Curriculum '{name}' v{version} already exists")

        curriculum = Curriculum(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            grade=grade,
            subject=subject,
            description=description,
            version=version,
            status="draft"
        )
        db.add(curriculum)
        db.commit()
        db.refresh(curriculum)
        logger.info(f"Created curriculum: {curriculum.id} ({name})")
        return curriculum

    @staticmethod
    def create_unit(
        db: Session,
        curriculum_id: str,
        title: str,
        description: str = None,
        sequence: int = None,
        parent_id: str = None
    ) -> CurriculumUnit:
        """Create a unit within a curriculum."""
        tenant_id = get_current_tenant_id()

        # Verify curriculum exists
        curriculum = db.query(Curriculum).filter(
            and_(
                Curriculum.id == curriculum_id,
                Curriculum.tenant_id == tenant_id
            )
        ).first()

        if not curriculum:
            raise ValueError(f"Curriculum {curriculum_id} not found")

        # Verify parent exists if provided
        if parent_id:
            parent = db.query(CurriculumUnit).filter(
                and_(
                    CurriculumUnit.id == parent_id,
                    CurriculumUnit.tenant_id == tenant_id,
                    CurriculumUnit.curriculum_id == curriculum_id
                )
            ).first()
            if not parent:
                raise ValueError(f"Parent unit {parent_id} not found")

        unit = CurriculumUnit(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            curriculum_id=curriculum_id,
            parent_id=parent_id,
            title=title,
            description=description,
            sequence=sequence or 0
        )
        db.add(unit)
        db.commit()
        db.refresh(unit)
        logger.info(f"Created unit: {unit.id} ({title})")
        return unit

    @staticmethod
    def create_objective(
        db: Session,
        unit_id: str,
        objective: str,
        cognitive_level: str = None
    ) -> LearningObjective:
        """Create a learning objective within a unit."""
        tenant_id = get_current_tenant_id()

        # Verify unit exists
        unit = db.query(CurriculumUnit).filter(
            and_(
                CurriculumUnit.id == unit_id,
                CurriculumUnit.tenant_id == tenant_id
            )
        ).first()

        if not unit:
            raise ValueError(f"Unit {unit_id} not found")

        obj = LearningObjective(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            unit_id=unit_id,
            objective=objective,
            cognitive_level=cognitive_level
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        logger.info(f"Created objective: {obj.id}")
        return obj

    @staticmethod
    def get_curriculum(db: Session, curriculum_id: str) -> Curriculum:
        """Get a curriculum by ID."""
        tenant_id = get_current_tenant_id()

        curriculum = db.query(Curriculum).filter(
            and_(
                Curriculum.id == curriculum_id,
                Curriculum.tenant_id == tenant_id
            )
        ).first()

        if not curriculum:
            raise ValueError(f"Curriculum {curriculum_id} not found")

        return curriculum

    @staticmethod
    def get_curriculum_structure(db: Session, curriculum_id: str) -> Dict[str, Any]:
        """Get the full structure of a curriculum (units, objectives, etc)."""
        tenant_id = get_current_tenant_id()

        curriculum = CurriculumService.get_curriculum(db, curriculum_id)

        # Get all units
        units = db.query(CurriculumUnit).filter(
            and_(
                CurriculumUnit.tenant_id == tenant_id,
                CurriculumUnit.curriculum_id == curriculum_id,
                CurriculumUnit.parent_id == None  # Top-level only
            )
        ).order_by(CurriculumUnit.sequence).all()

        # Build structure with nested units and objectives
        def build_unit_structure(unit):
            children = db.query(CurriculumUnit).filter(
                and_(
                    CurriculumUnit.tenant_id == tenant_id,
                    CurriculumUnit.parent_id == unit.id
                )
            ).order_by(CurriculumUnit.sequence).all()

            objectives = db.query(LearningObjective).filter(
                and_(
                    LearningObjective.tenant_id == tenant_id,
                    LearningObjective.unit_id == unit.id
                )
            ).all()

            return {
                "unit": unit,
                "objectives": objectives,
                "children": [build_unit_structure(child) for child in children]
            }

        return {
            "curriculum": curriculum,
            "units": [build_unit_structure(unit) for unit in units]
        }

    @staticmethod
    def list_curricula(db: Session, skip: int = 0, limit: int = 50) -> tuple[List[Curriculum], int]:
        """List all curricula for the tenant."""
        tenant_id = get_current_tenant_id()

        total = db.query(Curriculum).filter(
            Curriculum.tenant_id == tenant_id
        ).count()

        curricula = db.query(Curriculum).filter(
            Curriculum.tenant_id == tenant_id
        ).order_by(Curriculum.created_at.desc()).offset(skip).limit(limit).all()

        return curricula, total

    @staticmethod
    def get_objectives_for_unit(db: Session, unit_id: str) -> List[LearningObjective]:
        """Get all objectives for a unit."""
        tenant_id = get_current_tenant_id()

        objectives = db.query(LearningObjective).filter(
            and_(
                LearningObjective.tenant_id == tenant_id,
                LearningObjective.unit_id == unit_id
            )
        ).all()

        return objectives

    @staticmethod
    def analyze_curriculum_coverage(
        db: Session,
        curriculum_id: str,
        framework_id: str
    ) -> Dict[str, Any]:
        """
        Analyze curriculum coverage against a standards framework.

        Returns:
        - covered_standards: Standards with alignments
        - uncovered_standards: Standards without alignments
        - coverage_percentage: % of standards covered
        """
        from database.models import Standard, Alignment

        tenant_id = get_current_tenant_id()

        # Get all objectives in curriculum
        objectives = db.query(LearningObjective).filter(
            and_(
                LearningObjective.tenant_id == tenant_id,
                CurriculumUnit.curriculum_id == curriculum_id
            )
        ).join(CurriculumUnit).all()

        objective_ids = [obj.id for obj in objectives]

        # Get standards from framework
        standards = db.query(Standard).filter(
            and_(
                Standard.tenant_id == tenant_id,
                Standard.framework_id == framework_id
            )
        ).all()

        # Find covered standards (with approved alignments)
        covered_standard_ids = db.query(Standard.id).join(
            Alignment,
            and_(
                Alignment.standard_id == Standard.id,
                Alignment.status == "approved",
                Alignment.objective_id.in_(objective_ids)
            )
        ).distinct().all()

        covered_ids = {std[0] for std in covered_standard_ids}
        all_ids = {std.id for std in standards}
        uncovered_ids = all_ids - covered_ids

        coverage_percentage = (len(covered_ids) / len(all_ids) * 100) if all_ids else 0

        return {
            "covered_standards": [s for s in standards if s.id in covered_ids],
            "uncovered_standards": [s for s in standards if s.id in uncovered_ids],
            "coverage_percentage": coverage_percentage,
            "total_standards": len(all_ids),
            "covered_count": len(covered_ids),
            "uncovered_count": len(uncovered_ids)
        }
