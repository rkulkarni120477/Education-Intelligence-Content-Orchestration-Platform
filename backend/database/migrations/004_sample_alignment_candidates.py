"""
Create 20 sample alignment candidates for Alignment Workspace.

This migration creates sample lessons/content and generates 20 alignment
candidates linking them to existing standards. These candidates are ready
for review in the Alignment Workspace.

Sample candidates cover:
- Multiple source types (lesson, content, objective)
- Various subject areas and grade levels
- High, medium, and low confidence scores
- Complete status='candidate' for Alignment Workspace review
"""

from sqlalchemy.orm import Session
from database.models import Lesson, Alignment, Standard, Curriculum, Tenant
import logging
import uuid
from datetime import datetime
import random

logger = logging.getLogger(__name__)


def migrate(db: Session):
    """Create 20 sample alignment candidates for Alignment Workspace."""
    try:
        # Get system tenant or first available tenant
        system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
        if not system_tenant:
            system_tenant = db.query(Tenant).first()

        if not system_tenant:
            logger.warning("No tenant found, skipping sample alignments")
            return True

        tenant_id = system_tenant.id
        logger.info(f"Creating sample alignments for tenant: {tenant_id}")

        # Create a sample curriculum if it doesn't exist
        sample_curriculum = db.query(Curriculum).filter(
            Curriculum.tenant_id == tenant_id,
            Curriculum.name == "Sample Curriculum - Alignment Workspace"
        ).first()

        if not sample_curriculum:
            sample_curriculum = Curriculum(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                name="Sample Curriculum - Alignment Workspace",
                description="Sample curriculum with alignment candidates for workspace demo",
                version="1.0",
                grade="K-12",
                subject="Mixed",
                status="active"
            )
            db.add(sample_curriculum)
            db.flush()
            logger.info(f"Created sample curriculum: {sample_curriculum.id}")

        # Create 5 sample lessons as alignment sources
        sample_lessons = []
        lesson_titles = [
            "Introduction to Addition",
            "States of Matter",
            "American Revolution",
            "Introduction to Python",
            "Literary Devices in Poetry"
        ]

        for title in lesson_titles:
            lesson = Lesson(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                curriculum_id=sample_curriculum.id,
                title=title,
                description=f"Sample lesson for demonstrating alignment: {title}",
                duration_minutes=45,
                grade="3-5" if "Addition" in title else ("4-6" if "Matter" in title else ("8-10" if "Revolution" in title else ("9-12" if "Python" in title else "9-12"))),
                subject="Math" if "Addition" in title else ("Science" if "Matter" in title else ("Social Studies" if "Revolution" in title else ("Computer Science" if "Python" in title else "English Language Arts"))),
                status="draft",
                content={
                    "title": title,
                    "objectives": [
                        f"Learn about {title.lower()}",
                        "Understand key concepts",
                        "Apply knowledge to examples"
                    ],
                    "activities": ["Discussion", "Guided Practice", "Assessment"]
                }
            )
            db.add(lesson)
            sample_lessons.append(lesson)

        db.flush()
        logger.info(f"Created {len(sample_lessons)} sample lessons")

        # Get available standards for alignment
        standards = db.query(Standard).filter(
            Standard.tenant_id == tenant_id
        ).limit(100).all()

        if not standards:
            logger.warning("No standards found, cannot create alignments")
            return True

        logger.info(f"Found {len(standards)} standards for alignment")

        # Create 20 sample alignment candidates
        alignment_count = 0

        # Distribution of alignments across different quality levels
        quality_scores = [
            (0.95, 0.92),  # High confidence, high score (excellent)
            (0.90, 0.88),  # High confidence, high score
            (0.85, 0.80),  # Medium-high confidence
            (0.78, 0.75),  # Medium confidence
            (0.70, 0.68),  # Medium confidence, acceptable
            (0.65, 0.62),  # Medium-low confidence
            (0.60, 0.55),  # Lower confidence, needs review
        ]

        # Sample alignment metadata with evidence
        evidence_templates = [
            {
                "source": "Curriculum document",
                "page": 1,
                "text": "This lesson directly addresses the standard learning objectives."
            },
            {
                "source": "Learning outcome assessment",
                "page": None,
                "text": "Student mastery of this standard is assessed in the final project."
            },
            {
                "source": "Instructional materials",
                "page": 2,
                "text": "The lesson activities are designed to meet this standard."
            },
            {
                "source": "Grade-level expectations",
                "page": 1,
                "text": "This content aligns with grade-level achievement goals."
            },
            {
                "source": "Curriculum map",
                "page": 3,
                "text": "Clear mapping between lesson content and standard requirements."
            },
        ]

        created_alignments = []

        # Create alignments across different lessons and standards
        for i in range(20):
            # Select lesson, standard, and quality level
            lesson = sample_lessons[i % len(sample_lessons)]
            standard = random.choice(standards)
            score, confidence = random.choice(quality_scores)
            evidence = [random.choice(evidence_templates)]

            # Check if alignment already exists to avoid duplicates
            existing = db.query(Alignment).filter(
                Alignment.tenant_id == tenant_id,
                Alignment.source_type == "lesson",
                Alignment.source_id == lesson.id,
                Alignment.standard_id == standard.id
            ).first()

            if existing:
                # Skip if already exists
                continue

            alignment = Alignment(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                source_type="lesson",
                source_id=lesson.id,
                target_type="standard",
                standard_id=standard.id,
                score=score,
                confidence=confidence,
                evidence=evidence,
                status="candidate",  # All are candidates for Alignment Workspace review
                created_at=datetime.utcnow()
            )

            db.add(alignment)
            created_alignments.append({
                "lesson": lesson.title,
                "standard": standard.code,
                "score": round(score, 2),
                "confidence": round(confidence, 2),
                "status": "candidate"
            })

            alignment_count += 1

        db.commit()

        logger.info(f"Created {alignment_count} sample alignment candidates")

        # Log details
        for alignment in created_alignments[:5]:  # Log first 5 as sample
            logger.info(f"  {alignment['lesson']} → {alignment['standard']} (score={alignment['score']}, confidence={alignment['confidence']})")

        if alignment_count > 5:
            logger.info(f"  ... and {alignment_count - 5} more alignments")

        return True

    except ImportError as e:
        logger.warning(f"Skipping sample alignments: dependencies not available ({str(e)})")
        return True

    except Exception as e:
        logger.error(f"[FAIL] Sample alignments creation failed: {str(e)}")
        raise
