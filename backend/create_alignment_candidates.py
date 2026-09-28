#!/usr/bin/env python
"""Create sample alignment candidates for the workspace"""

from database.db import SessionLocal
from database.models import Alignment, Content, Lesson, Standard, Tenant
import uuid
from datetime import datetime

db = SessionLocal()

try:
    # Get system tenant
    system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
    if not system_tenant:
        print("[ERROR] System tenant not found")
        exit(1)

    tenant_id = system_tenant.id

    # Get sample content and lessons
    content_items = db.query(Content).filter(Content.tenant_id == tenant_id).all()
    lessons = db.query(Lesson).filter(Lesson.tenant_id == tenant_id).all()
    standards = db.query(Standard).filter(Standard.tenant_id == tenant_id).all()

    print("[INFO] Found {} content items, {} lessons, {} standards".format(
        len(content_items), len(lessons), len(standards)))

    if not content_items or not lessons or not standards:
        print("[ERROR] Not enough data to create candidates")
        exit(1)

    # Create candidates from content items to standards
    candidates_created = 0

    print("\n[STEP 1] Creating candidates from content to standards...")

    for i, content in enumerate(content_items[:4]):  # Create candidates for first 4 content items
        # Match content to 2 standards
        for j in range(2):
            standard_idx = (i * 2 + j) % len(standards)
            standard = standards[standard_idx]

            # Check if this alignment already exists
            existing = db.query(Alignment).filter(
                Alignment.tenant_id == tenant_id,
                Alignment.source_type == 'content',
                Alignment.source_id == content.id,
                Alignment.standard_id == standard.id
            ).first()

            if not existing:
                confidence = 0.75 + (j * 0.1)  # Vary confidence
                alignment = Alignment(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    source_type='content',
                    source_id=content.id,
                    standard_id=standard.id,
                    status='candidate',
                    confidence=min(0.95, confidence),
                    score=85 + (j * 5),
                    evidence=["Content title matches standard domain", "Subject area alignment"],
                    target_type='standard',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(alignment)
                candidates_created += 1

    db.commit()
    print("[OK] Created {} content-to-standard candidates".format(candidates_created))

    # Create candidates from lessons to standards
    print("\n[STEP 2] Creating candidates from lessons to standards...")

    lesson_candidates = 0
    for i, lesson in enumerate(lessons[:3]):  # Create candidates for first 3 lessons
        # Match lesson to 2 standards
        for j in range(2):
            standard_idx = (i * 2 + j + 5) % len(standards)
            standard = standards[standard_idx]

            # Check if this alignment already exists
            existing = db.query(Alignment).filter(
                Alignment.tenant_id == tenant_id,
                Alignment.source_type == 'lesson',
                Alignment.source_id == lesson.id,
                Alignment.standard_id == standard.id
            ).first()

            if not existing:
                confidence = 0.80 + (j * 0.05)
                alignment = Alignment(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    source_type='lesson',
                    source_id=lesson.id,
                    standard_id=standard.id,
                    status='candidate',
                    confidence=min(0.95, confidence),
                    score=88 + (j * 3),
                    evidence=["Learning objectives match standard", "Grade level alignment confirmed"],
                    target_type='standard',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(alignment)
                lesson_candidates += 1

    db.commit()
    print("[OK] Created {} lesson-to-standard candidates".format(lesson_candidates))

    # Print verification
    print("\n" + "=" * 70)
    print("VERIFICATION:")
    print("=" * 70)

    all_alignments = db.query(Alignment).filter(Alignment.tenant_id == tenant_id).all()

    candidate_count = len([a for a in all_alignments if a.status == 'candidate'])
    approved_count = len([a for a in all_alignments if a.status == 'approved'])
    rejected_count = len([a for a in all_alignments if a.status == 'rejected'])

    print("\nAlignment Status Summary:")
    print("  Candidates (pending): {}".format(candidate_count))
    print("  Approved: {}".format(approved_count))
    print("  Rejected: {}".format(rejected_count))
    print("  Total: {}".format(len(all_alignments)))

    if candidate_count > 0:
        avg_confidence = sum(a.confidence for a in all_alignments if a.status == 'candidate') / candidate_count
        print("\nAverage Confidence (Candidates): {:.0%}".format(avg_confidence))

except Exception as e:
    print("[ERROR] {}".format(str(e)))
    import traceback
    traceback.print_exc()
finally:
    db.close()
