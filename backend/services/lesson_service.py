"""
Lesson and Assessment generation service.

Manages lesson and assessment creation, generation, and publishing.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models import Lesson, Activity, Assessment, AssessmentItem, Curriculum
from auth.tenant_context import get_current_tenant_id
from typing import List, Optional, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class LessonService:
    """Service for lesson management."""

    @staticmethod
    def create_lesson(
        db: Session,
        curriculum_id: str,
        title: str,
        grade: str = None,
        subject: str = None,
        duration_minutes: int = None,
        description: str = None,
        content: Dict = None
    ) -> Lesson:
        """Create a new lesson."""
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

        lesson = Lesson(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            curriculum_id=curriculum_id,
            title=title,
            grade=grade or curriculum.grade,
            subject=subject or curriculum.subject,
            duration_minutes=duration_minutes,
            description=description,
            content=content or {},
            status="draft"
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        logger.info(f"Created lesson: {lesson.id} ({title})")
        return lesson

    @staticmethod
    def add_activity_to_lesson(
        db: Session,
        lesson_id: str,
        type: str,
        title: str,
        instructions: str = None,
        duration_minutes: int = None,
        differentiation: Dict = None
    ) -> Activity:
        """Add an activity to a lesson."""
        tenant_id = get_current_tenant_id()

        # Verify lesson exists
        lesson = db.query(Lesson).filter(
            and_(
                Lesson.id == lesson_id,
                Lesson.tenant_id == tenant_id
            )
        ).first()

        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        activity = Activity(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            lesson_id=lesson_id,
            type=type,
            title=title,
            instructions=instructions,
            duration_minutes=duration_minutes,
            differentiation=differentiation or {},
            status="draft"
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        logger.info(f"Created activity: {activity.id}")
        return activity

    @staticmethod
    def get_lesson(db: Session, lesson_id: str) -> Lesson:
        """Get a lesson by ID."""
        tenant_id = get_current_tenant_id()

        lesson = db.query(Lesson).filter(
            and_(
                Lesson.id == lesson_id,
                Lesson.tenant_id == tenant_id
            )
        ).first()

        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        return lesson

    @staticmethod
    def list_lessons(
        db: Session,
        curriculum_id: str = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Lesson], int]:
        """List lessons for a curriculum."""
        tenant_id = get_current_tenant_id()

        query = db.query(Lesson).filter(Lesson.tenant_id == tenant_id)

        if curriculum_id:
            query = query.filter(Lesson.curriculum_id == curriculum_id)

        total = query.count()
        lessons = query.order_by(Lesson.created_at.desc()).offset(skip).limit(limit).all()

        return lessons, total

    @staticmethod
    def publish_lesson(db: Session, lesson_id: str) -> Lesson:
        """Publish a lesson (move from draft to published)."""
        lesson = LessonService.get_lesson(db, lesson_id)
        lesson.status = "published"
        db.commit()
        db.refresh(lesson)
        logger.info(f"Published lesson: {lesson_id}")
        return lesson

    @staticmethod
    def update_lesson_content(
        db: Session,
        lesson_id: str,
        content: Dict[str, Any]
    ) -> Lesson:
        """Update lesson content."""
        lesson = LessonService.get_lesson(db, lesson_id)
        lesson.content = content
        db.commit()
        db.refresh(lesson)
        return lesson


class AssessmentService:
    """Service for assessment management."""

    @staticmethod
    def create_assessment(
        db: Session,
        title: str,
        assessment_type: str,  # formative, summative, diagnostic, benchmark
        description: str = None,
        blueprint: Dict = None
    ) -> Assessment:
        """Create a new assessment."""
        tenant_id = get_current_tenant_id()

        # Check if assessment already exists
        existing = db.query(Assessment).filter(
            and_(
                Assessment.tenant_id == tenant_id,
                Assessment.title == title
            )
        ).first()

        if existing:
            raise ValueError(f"Assessment '{title}' already exists")

        assessment = Assessment(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            title=title,
            assessment_type=assessment_type,
            description=description,
            blueprint=blueprint or {},
            status="draft"
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        logger.info(f"Created assessment: {assessment.id} ({title})")
        return assessment

    @staticmethod
    def add_item_to_assessment(
        db: Session,
        assessment_id: str,
        type: str,  # multiple_choice, short_answer, essay, etc.
        question: str,
        answer_key: Dict = None,
        cognitive_level: str = None,
        distractors: List[str] = None,
        rationale: str = None,
        sequence: int = None
    ) -> AssessmentItem:
        """Add an item (question) to an assessment."""
        tenant_id = get_current_tenant_id()

        # Verify assessment exists
        assessment = db.query(Assessment).filter(
            and_(
                Assessment.id == assessment_id,
                Assessment.tenant_id == tenant_id
            )
        ).first()

        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Auto-sequence if not provided
        if sequence is None:
            max_seq = db.query(AssessmentItem).filter(
                AssessmentItem.assessment_id == assessment_id
            ).count()
            sequence = max_seq + 1

        item = AssessmentItem(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            assessment_id=assessment_id,
            type=type,
            question=question,
            answer_key=answer_key or {},
            distractors=distractors or [],
            rationale=rationale,
            cognitive_level=cognitive_level,
            sequence=sequence
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info(f"Created assessment item: {item.id}")
        return item

    @staticmethod
    def get_assessment(db: Session, assessment_id: str) -> Assessment:
        """Get an assessment by ID."""
        tenant_id = get_current_tenant_id()

        assessment = db.query(Assessment).filter(
            and_(
                Assessment.id == assessment_id,
                Assessment.tenant_id == tenant_id
            )
        ).first()

        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        return assessment

    @staticmethod
    def list_assessments(
        db: Session,
        assessment_type: str = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Assessment], int]:
        """List assessments."""
        tenant_id = get_current_tenant_id()

        query = db.query(Assessment).filter(Assessment.tenant_id == tenant_id)

        if assessment_type:
            query = query.filter(Assessment.assessment_type == assessment_type)

        total = query.count()
        assessments = query.order_by(Assessment.created_at.desc()).offset(skip).limit(limit).all()

        return assessments, total

    @staticmethod
    def publish_assessment(db: Session, assessment_id: str) -> Assessment:
        """Publish an assessment."""
        assessment = AssessmentService.get_assessment(db, assessment_id)
        assessment.status = "published"
        db.commit()
        db.refresh(assessment)
        logger.info(f"Published assessment: {assessment_id}")
        return assessment

    @staticmethod
    def update_blueprint(
        db: Session,
        assessment_id: str,
        blueprint: Dict[str, Any]
    ) -> Assessment:
        """Update the assessment blueprint (structure/metadata)."""
        assessment = AssessmentService.get_assessment(db, assessment_id)
        assessment.blueprint = blueprint
        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def validate_assessment(db: Session, assessment_id: str) -> Dict[str, Any]:
        """
        Validate an assessment for quality and completeness.

        Returns validation results with issues and recommendations.
        """
        assessment = AssessmentService.get_assessment(db, assessment_id)
        issues = []
        warnings = []

        # Check items exist
        if len(assessment.items) == 0:
            issues.append("Assessment has no items")

        # Check item completeness
        for item in assessment.items:
            if not item.question:
                issues.append(f"Item {item.sequence} has no question")
            if not item.answer_key:
                warnings.append(f"Item {item.sequence} has no answer key")
            if item.type == "multiple_choice" and not item.distractors:
                warnings.append(f"MC Item {item.sequence} has no distractors")

        # Check cognitive level distribution
        cognitive_levels = [item.cognitive_level for item in assessment.items if item.cognitive_level]
        if not cognitive_levels:
            warnings.append("No cognitive levels specified for items")

        return {
            "assessment_id": assessment_id,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "item_count": len(assessment.items),
            "cognitive_level_coverage": len(set(cognitive_levels)) if cognitive_levels else 0
        }
