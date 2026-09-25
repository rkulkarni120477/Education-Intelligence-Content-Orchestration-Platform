"""
Workforce Alignment Workflow - Phase 1 Foundation Migration.

This migration creates the database schema for:
1. Workforce skill framework and skill models
2. Skill proficiency rubrics
3. Workforce roles and role-skill requirements
4. Requirements profiles for capturing institution needs
5. Requirement edit audit trail

These tables support the foundation for skill mapping, coverage analysis,
and recommendations in the workforce alignment workflow.
"""

from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def migrate(db: Session):
    """Create workforce alignment workflow foundation tables."""
    try:
        from database.models import Base, SkillFramework, WorkforceSkill, SkillProficiencyRubric, WorkforceRole, RoleSkillRequirement, RequirementsProfile, RequirementEdit

        logger.info("Starting workforce alignment foundation migration...")

        # Create tables via SQLAlchemy
        Base.metadata.create_all(db.bind, tables=[
            SkillFramework.__table__,
            WorkforceSkill.__table__,
            SkillProficiencyRubric.__table__,
            WorkforceRole.__table__,
            RoleSkillRequirement.__table__,
            RequirementsProfile.__table__,
            RequirementEdit.__table__,
        ])

        logger.info("[OK] Workforce alignment foundation tables created successfully")
        return True

    except Exception as e:
        logger.error(f"[FAIL] Workforce alignment migration failed: {str(e)}")
        raise
