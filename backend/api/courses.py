"""
Course Management API Endpoints

Implements CRUD operations for:
- Courses
- Units
- Lessons
- Learning Objectives
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database.db import get_db
# Note: Core models now defined in database.models
# from database.content_models import (
#     Course, Unit, Lesson, LearningObjective,
#     ContentStatus
# )

router = APIRouter(prefix="/courses", tags=["courses"])


# ==================== REQUEST/RESPONSE MODELS ====================

class LearningObjectiveCreate(dict):
    """Learning objective input"""
    objective_text: str
    bloom_level: Optional[str] = None
    success_criteria: Optional[str] = None


class CourseCreate(dict):
    """Course creation request"""
    name: str
    grade_level: str
    subject: str
    description: Optional[str] = None
    state_jurisdiction: Optional[str] = None
    duration_hours: Optional[int] = None
    target_learner: Optional[str] = None
    learning_goals: Optional[str] = None
    prerequisites: Optional[str] = None
    instructional_model: Optional[str] = None
    assessment_approach: Optional[str] = None


class CourseUpdate(dict):
    """Course update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    grade_level: Optional[str] = None
    subject: Optional[str] = None
    duration_hours: Optional[int] = None
    learning_goals: Optional[str] = None
    status: Optional[str] = None


class CourseResponse(dict):
    """Course response model"""
    id: str
    name: str
    grade_level: str
    subject: str
    description: Optional[str]
    status: str
    version: int
    created_at: str
    updated_at: str


class UnitCreate(dict):
    """Unit creation request"""
    name: str
    description: Optional[str] = None
    sequence_number: int
    duration_hours: Optional[int] = None
    learning_objective_ids: Optional[List[str]] = None
    standard_ids: Optional[List[str]] = None


class UnitResponse(dict):
    """Unit response model"""
    id: str
    course_id: str
    name: str
    sequence_number: int
    description: Optional[str]
    status: str
    version: int


class LessonCreate(dict):
    """Lesson creation request"""
    unit_id: str
    name: str
    description: Optional[str] = None
    sequence_number: Optional[int] = None
    duration_minutes: Optional[int] = None
    grade_level: Optional[str] = None
    instructional_strategy: Optional[str] = None
    learning_objective_ids: Optional[List[str]] = None
    standard_ids: Optional[List[str]] = None
    materials: Optional[str] = None
    teaching_sequence: Optional[str] = None
    common_misconceptions: Optional[str] = None


class LessonResponse(dict):
    """Lesson response model"""
    id: str
    unit_id: str
    name: str
    description: Optional[str]
    duration_minutes: Optional[int]
    status: str
    version: int
    learning_objective_ids: List[str]
    standard_ids: List[str]


# ==================== COURSE ENDPOINTS ====================

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: dict,
    current_user_id: str = "user_id",  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Create a new course"""
    try:
        course = Course(
            id=str(uuid.uuid4()),
            name=course_data.get("name"),
            grade_level=course_data.get("grade_level"),
            subject=course_data.get("subject"),
            description=course_data.get("description"),
            state_jurisdiction=course_data.get("state_jurisdiction"),
            duration_hours=course_data.get("duration_hours"),
            target_learner=course_data.get("target_learner"),
            learning_goals=course_data.get("learning_goals"),
            prerequisites=course_data.get("prerequisites"),
            instructional_model=course_data.get("instructional_model"),
            assessment_approach=course_data.get("assessment_approach"),
            created_by=current_user_id,
            status="draft",
            version=1
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        return {
            "id": course.id,
            "name": course.name,
            "grade_level": course.grade_level,
            "subject": course.subject,
            "description": course.description,
            "status": course.status,
            "version": course.version,
            "created_at": course.created_at.isoformat(),
            "updated_at": course.updated_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{course_id}", response_model=dict)
async def get_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    """Get course with units and lessons"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get units with lessons
    units = db.query(Unit).filter(Unit.course_id == course_id).order_by(Unit.sequence_number).all()

    units_data = []
    for unit in units:
        lessons = db.query(Lesson).filter(Lesson.unit_id == unit.id).order_by(Lesson.sequence_number).all()

        units_data.append({
            "id": unit.id,
            "name": unit.name,
            "sequence_number": unit.sequence_number,
            "description": unit.description,
            "duration_hours": unit.duration_hours,
            "status": unit.status,
            "lessons": [
                {
                    "id": lesson.id,
                    "name": lesson.name,
                    "sequence_number": lesson.sequence_number,
                    "status": lesson.status
                }
                for lesson in lessons
            ]
        })

    return {
        "id": course.id,
        "name": course.name,
        "grade_level": course.grade_level,
        "subject": course.subject,
        "description": course.description,
        "status": course.status,
        "version": course.version,
        "units": units_data,
        "created_at": course.created_at.isoformat(),
        "updated_at": course.updated_at.isoformat()
    }


@router.put("/{course_id}", response_model=dict)
async def update_course(
    course_id: str,
    course_data: dict,
    db: Session = Depends(get_db)
):
    """Update course metadata"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Update fields
    if "name" in course_data:
        course.name = course_data["name"]
    if "description" in course_data:
        course.description = course_data["description"]
    if "grade_level" in course_data:
        course.grade_level = course_data["grade_level"]
    if "subject" in course_data:
        course.subject = course_data["subject"]
    if "duration_hours" in course_data:
        course.duration_hours = course_data["duration_hours"]
    if "learning_goals" in course_data:
        course.learning_goals = course_data["learning_goals"]
    if "status" in course_data:
        course.status = course_data["status"]

    course.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(course)

    return {
        "id": course.id,
        "name": course.name,
        "grade_level": course.grade_level,
        "subject": course.subject,
        "status": course.status,
        "updated_at": course.updated_at.isoformat()
    }


@router.get("", response_model=dict)
async def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    current_user_id: str = "user_id",  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """List user's courses with pagination"""
    courses = db.query(Course).filter(
        Course.created_by == current_user_id
    ).offset(skip).limit(limit).all()

    total = db.query(Course).filter(Course.created_by == current_user_id).count()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "courses": [
            {
                "id": c.id,
                "name": c.name,
                "grade_level": c.grade_level,
                "subject": c.subject,
                "status": c.status,
                "version": c.version,
                "created_at": c.created_at.isoformat()
            }
            for c in courses
        ]
    }


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    """Archive course (soft delete)"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.status = "archived"
    db.commit()

    return None


# ==================== UNIT ENDPOINTS ====================

@router.post("/{course_id}/units", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_unit(
    course_id: str,
    unit_data: dict,
    current_user_id: str = "user_id",
    db: Session = Depends(get_db)
):
    """Create unit in course"""
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    unit = Unit(
        id=str(uuid.uuid4()),
        course_id=course_id,
        name=unit_data.get("name"),
        description=unit_data.get("description"),
        sequence_number=unit_data.get("sequence_number", 1),
        duration_hours=unit_data.get("duration_hours"),
        learning_objective_ids=unit_data.get("learning_objective_ids", []),
        standard_ids=unit_data.get("standard_ids", []),
        created_by=current_user_id,
        status="draft",
        version=1
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)

    return {
        "id": unit.id,
        "course_id": unit.course_id,
        "name": unit.name,
        "sequence_number": unit.sequence_number,
        "status": unit.status,
        "created_at": unit.created_at.isoformat()
    }


@router.put("/{course_id}/units/{unit_id}", response_model=dict)
async def update_unit(
    course_id: str,
    unit_id: str,
    unit_data: dict,
    db: Session = Depends(get_db)
):
    """Update unit"""
    unit = db.query(Unit).filter(
        Unit.id == unit_id,
        Unit.course_id == course_id
    ).first()

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    if "name" in unit_data:
        unit.name = unit_data["name"]
    if "description" in unit_data:
        unit.description = unit_data["description"]
    if "sequence_number" in unit_data:
        unit.sequence_number = unit_data["sequence_number"]
    if "duration_hours" in unit_data:
        unit.duration_hours = unit_data["duration_hours"]
    if "status" in unit_data:
        unit.status = unit_data["status"]

    unit.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(unit)

    return {
        "id": unit.id,
        "name": unit.name,
        "status": unit.status,
        "updated_at": unit.updated_at.isoformat()
    }


@router.delete("/{course_id}/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unit(
    course_id: str,
    unit_id: str,
    db: Session = Depends(get_db)
):
    """Delete unit"""
    unit = db.query(Unit).filter(
        Unit.id == unit_id,
        Unit.course_id == course_id
    ).first()

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    db.delete(unit)
    db.commit()
    return None


# ==================== LESSON ENDPOINTS ====================

@router.post("/{course_id}/units/{unit_id}/lessons", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: str,
    unit_id: str,
    lesson_data: dict,
    current_user_id: str = "user_id",
    db: Session = Depends(get_db)
):
    """Create lesson in unit"""
    # Verify unit exists
    unit = db.query(Unit).filter(
        Unit.id == unit_id,
        Unit.course_id == course_id
    ).first()

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    lesson = Lesson(
        id=str(uuid.uuid4()),
        unit_id=unit_id,
        name=lesson_data.get("name"),
        description=lesson_data.get("description"),
        sequence_number=lesson_data.get("sequence_number"),
        duration_minutes=lesson_data.get("duration_minutes"),
        grade_level=lesson_data.get("grade_level"),
        learning_objective_ids=lesson_data.get("learning_objective_ids", []),
        standard_ids=lesson_data.get("standard_ids", []),
        instructional_strategy=lesson_data.get("instructional_strategy"),
        materials=lesson_data.get("materials"),
        teaching_sequence=lesson_data.get("teaching_sequence"),
        common_misconceptions=lesson_data.get("common_misconceptions"),
        created_by=current_user_id,
        status="draft",
        version=1
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return {
        "id": lesson.id,
        "unit_id": lesson.unit_id,
        "name": lesson.name,
        "sequence_number": lesson.sequence_number,
        "status": lesson.status,
        "created_at": lesson.created_at.isoformat()
    }


@router.get("/{course_id}/units/{unit_id}/lessons/{lesson_id}", response_model=dict)
async def get_lesson(
    course_id: str,
    unit_id: str,
    lesson_id: str,
    db: Session = Depends(get_db)
):
    """Get lesson details"""
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.unit_id == unit_id
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return {
        "id": lesson.id,
        "unit_id": lesson.unit_id,
        "name": lesson.name,
        "description": lesson.description,
        "duration_minutes": lesson.duration_minutes,
        "grade_level": lesson.grade_level,
        "instructional_strategy": lesson.instructional_strategy,
        "materials": lesson.materials,
        "teaching_sequence": lesson.teaching_sequence,
        "common_misconceptions": lesson.common_misconceptions,
        "learning_objective_ids": lesson.learning_objective_ids,
        "standard_ids": lesson.standard_ids,
        "status": lesson.status,
        "version": lesson.version,
        "created_at": lesson.created_at.isoformat(),
        "updated_at": lesson.updated_at.isoformat()
    }


@router.put("/{course_id}/units/{unit_id}/lessons/{lesson_id}", response_model=dict)
async def update_lesson(
    course_id: str,
    unit_id: str,
    lesson_id: str,
    lesson_data: dict,
    db: Session = Depends(get_db)
):
    """Update lesson"""
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.unit_id == unit_id
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Update fields
    for field in ["name", "description", "duration_minutes", "instructional_strategy",
                  "materials", "teaching_sequence", "common_misconceptions", "status"]:
        if field in lesson_data:
            setattr(lesson, field, lesson_data[field])

    if "learning_objective_ids" in lesson_data:
        lesson.learning_objective_ids = lesson_data["learning_objective_ids"]
    if "standard_ids" in lesson_data:
        lesson.standard_ids = lesson_data["standard_ids"]

    lesson.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lesson)

    return {
        "id": lesson.id,
        "name": lesson.name,
        "status": lesson.status,
        "version": lesson.version,
        "updated_at": lesson.updated_at.isoformat()
    }


@router.delete("/{course_id}/units/{unit_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    course_id: str,
    unit_id: str,
    lesson_id: str,
    db: Session = Depends(get_db)
):
    """Delete lesson"""
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.unit_id == unit_id
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db.delete(lesson)
    db.commit()
    return None
