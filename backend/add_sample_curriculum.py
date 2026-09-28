"""Create a complete sample curriculum for the active system tenant."""

from datetime import datetime
import uuid

from database.db import SessionLocal
from database.models import Activity, Curriculum, CurriculumUnit, LearningObjective, Lesson, Tenant

CURRICULUM_NAME = "Sample Curriculum - Integrated Learning Foundations"
CURRICULUM_VERSION = "1.0"

UNITS = [
    {
        "title": "Unit 1: Foundations of Learning",
        "description": "Build routines for inquiry, collaboration, evidence gathering, and reflective learning.",
        "objectives": [
            ("Identify reliable classroom routines and explain how they support learning.", "understand"),
            ("Apply a simple inquiry process to investigate a familiar question.", "apply"),
            ("Compare personal learning strategies and select one for a new task.", "evaluate"),
        ],
        "lessons": [
            ("Learning Routines and Goal Setting", "General", 45),
            ("Asking Strong Questions", "General", 50),
        ],
    },
    {
        "title": "Unit 2: Our Changing World",
        "description": "Use observation, measurement, and data to explain patterns in the natural and human-made world.",
        "objectives": [
            ("Describe observable patterns in weather, materials, and local environments.", "understand"),
            ("Use measurements and organized data to support an explanation.", "apply"),
            ("Analyze competing explanations and identify evidence that would distinguish them.", "analyze"),
        ],
        "lessons": [
            ("Observation, Measurement, and Evidence", "Science", 50),
            ("Patterns in Data", "Science", 55),
        ],
    },
    {
        "title": "Unit 3: Communication and Community",
        "description": "Develop clear communication, perspective taking, and collaborative problem-solving skills.",
        "objectives": [
            ("Summarize the central idea and supporting details in an informational text.", "understand"),
            ("Construct a clear claim supported by relevant evidence.", "create"),
            ("Evaluate how audience and perspective influence a message.", "evaluate"),
        ],
        "lessons": [
            ("Reading for Meaning", "English Language Arts", 50),
            ("Claims, Evidence, and Audience", "English Language Arts", 55),
        ],
    },
    {
        "title": "Unit 4: Design Challenge Capstone",
        "description": "Integrate research, quantitative reasoning, communication, and reflection in an authentic project.",
        "objectives": [
            ("Plan a project with a question, milestones, resources, and success criteria.", "create"),
            ("Synthesize evidence from multiple sources into a usable product or proposal.", "create"),
            ("Defend design decisions and revise the product using feedback.", "evaluate"),
        ],
        "lessons": [
            ("Project Planning and Research", "Interdisciplinary", 55),
            ("Present, Defend, and Reflect", "Interdisciplinary", 60),
        ],
    },
]

ACTIVITY_TEMPLATES = [
    ("discussion", "Launch Discussion", "Connect the lesson topic to prior knowledge and generate questions.", 15),
    ("guided_practice", "Guided Practice", "Complete a structured practice task with peer or teacher feedback.", 25),
]


def main() -> None:
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
        if not tenant:
            raise RuntimeError("System tenant not found")

        existing = db.query(Curriculum).filter(
            Curriculum.tenant_id == tenant.id,
            Curriculum.name == CURRICULUM_NAME,
            Curriculum.version == CURRICULUM_VERSION,
        ).first()
        if existing:
            print(f"Sample curriculum already exists: {existing.id}")
            return

        curriculum = Curriculum(
            id=str(uuid.uuid4()),
            tenant_id=tenant.id,
            name=CURRICULUM_NAME,
            description="A complete sample curriculum demonstrating units, Bloom's taxonomy objectives, lessons, activities, and capstone learning.",
            version=CURRICULUM_VERSION,
            grade="K-5",
            subject="Interdisciplinary",
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(curriculum)
        db.flush()

        unit_count = objective_count = lesson_count = activity_count = 0
        for sequence, unit_data in enumerate(UNITS, start=1):
            unit = CurriculumUnit(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                curriculum_id=curriculum.id,
                title=unit_data["title"],
                description=unit_data["description"],
                sequence=sequence,
            )
            db.add(unit)
            db.flush()
            unit_count += 1

            for objective_text, cognitive_level in unit_data["objectives"]:
                db.add(LearningObjective(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    unit_id=unit.id,
                    objective=objective_text,
                    cognitive_level=cognitive_level,
                ))
                objective_count += 1

            for lesson_title, subject, duration in unit_data["lessons"]:
                lesson = Lesson(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    curriculum_id=curriculum.id,
                    title=lesson_title,
                    description=f"Sample lesson from {unit.title}.",
                    duration_minutes=duration,
                    grade="K-5",
                    subject=subject,
                    status="draft",
                    content={
                        "unit": unit.title,
                        "objectives": [objective for objective, _ in unit_data["objectives"]],
                    },
                )
                db.add(lesson)
                db.flush()
                lesson_count += 1

                for activity_type, activity_title, instructions, minutes in ACTIVITY_TEMPLATES:
                    db.add(Activity(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant.id,
                        lesson_id=lesson.id,
                        type=activity_type,
                        title=activity_title,
                        instructions=instructions,
                        duration_minutes=minutes,
                        differentiation={
                            "support": "Provide sentence starters, visuals, and worked examples.",
                            "extension": "Ask learners to justify, generalize, or create an alternative solution.",
                        },
                        status="draft",
                    ))
                    activity_count += 1

        db.commit()
        print({
            "curriculum_id": curriculum.id,
            "name": curriculum.name,
            "units": unit_count,
            "objectives": objective_count,
            "lessons": lesson_count,
            "activities": activity_count,
        })
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
