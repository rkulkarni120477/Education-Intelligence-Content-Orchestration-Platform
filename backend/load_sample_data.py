#!/usr/bin/env python
"""Load sample data into the platform"""

from database.db import SessionLocal
from database.models import (
    StandardFramework, Standard, Lesson, Alignment,
    Curriculum, Tenant, User
)
import uuid

db = SessionLocal()

try:
    # Get system tenant
    system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
    print(f"[OK] Using system tenant: {system_tenant.id}")

    # Create/get test user
    user = db.query(User).filter(User.email == "rkulkarni@academian.com").first()
    if user:
        print(f"[OK] User already exists: {user.email}")
    else:
        user = User(
            id=str(uuid.uuid4()),
            tenant_id=system_tenant.id,
            email="rkulkarni@academian.com",
            username="rkulkarni",
            hashed_password="scrypt:32768:8:1$QnyOfVN5c7OX5dVU$36d1ac8dcc69e5c65a6def0c0c1d1f9e7c6a6c5a",
            first_name="Rahul",
            last_name="Sudhakar",
            full_name="Rahul Sudhakar",
            is_active=True,
            role="admin"
        )
        db.add(user)
        db.commit()
        print(f"[OK] Created user: {user.email}")

    # Create/get standard frameworks
    frameworks_data = [
        ("Math Standards", "Common Core"),
        ("English Standards", "Common Core"),
        ("Science Standards", "NGSS"),
    ]

    framework_ids = {}
    for name, authority in frameworks_data:
        fw = db.query(StandardFramework).filter(
            StandardFramework.tenant_id == system_tenant.id,
            StandardFramework.name == name
        ).first()
        if not fw:
            fw = StandardFramework(
                id=str(uuid.uuid4()),
                tenant_id=system_tenant.id,
                name=name,
                authority=authority,
                jurisdiction="United States",
            )
            db.add(fw)
        framework_ids[name] = fw.id
    db.commit()
    print(f"[OK] Frameworks: {len(framework_ids)} ready")

    # Create/get standards
    standards_data = [
        ("K.CC.A.1", "Count to 100 by ones and tens", "K", "Math", "Math Standards"),
        ("K.CC.A.2", "Count forward beginning", "K", "Math", "Math Standards"),
        ("1.NBT.A.1", "Understand place value", "1", "Math", "Math Standards"),
        ("K-PS2-1", "Investigations about forces", "K", "Science", "Science Standards"),
        ("1-LS1-1", "Design solutions for problems", "1", "Science", "Science Standards"),
    ]

    created_standards = 0
    for code, description, grade, subject, framework_name in standards_data:
        existing = db.query(Standard).filter(
            Standard.tenant_id == system_tenant.id,
            Standard.code == code
        ).first()
        if not existing:
            standard = Standard(
                id=str(uuid.uuid4()),
                tenant_id=system_tenant.id,
                framework_id=framework_ids[framework_name],
                code=code,
                description=description,
                grade=grade,
                subject=subject,
                domain=code.split('-')[0] if '-' in code else code.split('.')[0],
                version="2020"
            )
            db.add(standard)
            created_standards += 1
    db.commit()
    total_standards = db.query(Standard).filter(Standard.tenant_id == system_tenant.id).count()
    print(f"[OK] Standards: {created_standards} created, {total_standards} total")

    # Create/get curriculum
    curriculum = db.query(Curriculum).filter(
        Curriculum.tenant_id == system_tenant.id,
        Curriculum.name == "Sample Curriculum"
    ).first()
    if not curriculum:
        curriculum = Curriculum(
            id=str(uuid.uuid4()),
            tenant_id=system_tenant.id,
            name="Sample Curriculum",
            grade="K-5",
            subject="Multi-Subject",
            status="active"
        )
        db.add(curriculum)
        db.commit()
    print(f"[OK] Curriculum: {curriculum.name}")

    # Create/get lessons
    lessons_data = [
        ("Introduction to Counting", "K", "Math"),
        ("Place Value Basics", "1", "Math"),
        ("Sound and Vibration", "K", "Science"),
        ("Life Cycles", "3", "Science"),
    ]

    created_lessons = 0
    for title, grade, subject in lessons_data:
        existing = db.query(Lesson).filter(
            Lesson.tenant_id == system_tenant.id,
            Lesson.title == title
        ).first()
        if not existing:
            lesson = Lesson(
                id=str(uuid.uuid4()),
                tenant_id=system_tenant.id,
                curriculum_id=curriculum.id,
                title=title,
                grade=grade,
                subject=subject,
                duration_minutes=45,
                status="published"
            )
            db.add(lesson)
            created_lessons += 1
    db.commit()
    total_lessons = db.query(Lesson).filter(Lesson.tenant_id == system_tenant.id).count()
    print(f"[OK] Lessons: {created_lessons} created, {total_lessons} total")

    # Create alignments (lesson to standard)
    standards_list = db.query(Standard).filter(Standard.tenant_id == system_tenant.id).all()
    lessons_list = db.query(Lesson).filter(Lesson.tenant_id == system_tenant.id).all()

    created_alignments = 0
    for i, lesson in enumerate(lessons_list[:4]):
        if i < len(standards_list):
            existing = db.query(Alignment).filter(
                Alignment.tenant_id == system_tenant.id,
                Alignment.source_id == lesson.id,
                Alignment.standard_id == standards_list[i].id
            ).first()
            if not existing:
                alignment = Alignment(
                    id=str(uuid.uuid4()),
                    tenant_id=system_tenant.id,
                    source_type="lesson",
                    source_id=lesson.id,
                    target_type="standard",
                    standard_id=standards_list[i].id,
                    confidence=0.85,
                    status="approved"
                )
                db.add(alignment)
                created_alignments += 1
    db.commit()
    total_alignments = db.query(Alignment).filter(Alignment.tenant_id == system_tenant.id).count()
    print(f"[OK] Alignments: {created_alignments} created, {total_alignments} total")

    # Final summary
    print("\n[SUCCESS] All Data Loaded:")
    print(f"  Standards Frameworks: {db.query(StandardFramework).filter(StandardFramework.tenant_id == system_tenant.id).count()}")
    print(f"  Standards: {total_standards}")
    print(f"  Curriculum: {db.query(Curriculum).filter(Curriculum.tenant_id == system_tenant.id).count()}")
    print(f"  Lessons: {total_lessons}")
    print(f"  Alignments: {total_alignments}")

except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
