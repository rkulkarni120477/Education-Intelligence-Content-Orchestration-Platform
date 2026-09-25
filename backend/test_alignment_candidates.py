#!/usr/bin/env python
"""Test loading 20 sample alignment candidates."""

from database.db import SessionLocal, init_db
from database.models import Alignment, Lesson, Standard, Tenant
from auth.tenant_context import TenantContext

# Initialize database (creates tables and runs migrations)
print("Initializing database...")
init_db()

db = SessionLocal()

try:
    # Get system tenant
    system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
    if system_tenant:
        TenantContext.set_tenant(system_tenant.id)
        tenant_id = system_tenant.id
    else:
        tenant_id = db.query(Tenant).first().id
        TenantContext.set_tenant(tenant_id)

    print(f"\n=== Alignment Workspace: Sample Candidates ===")
    print(f"Tenant: {tenant_id}\n")

    # Count alignments
    total_alignments = db.query(Alignment).filter(
        Alignment.tenant_id == tenant_id
    ).count()

    candidate_alignments = db.query(Alignment).filter(
        Alignment.tenant_id == tenant_id,
        Alignment.status == "candidate"
    ).count()

    print(f"Total alignments in database: {total_alignments}")
    print(f"Candidate alignments (ready for review): {candidate_alignments}")

    # Show sample candidates with lesson details
    print(f"\n=== Sample Alignment Candidates ===\n")

    candidates = db.query(Alignment).filter(
        Alignment.tenant_id == tenant_id,
        Alignment.status == "candidate"
    ).order_by(Alignment.confidence.desc()).limit(10).all()

    for i, alignment in enumerate(candidates, 1):
        # Get lesson title
        lesson = db.query(Lesson).filter(
            Lesson.id == alignment.source_id
        ).first()

        # Get standard code
        standard = db.query(Standard).filter(
            Standard.id == alignment.standard_id
        ).first()

        lesson_title = lesson.title if lesson else "Unknown Lesson"
        standard_code = standard.code if standard else "Unknown Standard"
        standard_subject = standard.subject if standard else "N/A"

        print(f"{i}. {lesson_title}")
        print(f"   → {standard_code} ({standard_subject})")
        print(f"   Score: {alignment.score:.2f}, Confidence: {alignment.confidence:.2f}")
        print(f"   Status: {alignment.status}")
        print()

    # Distribution analysis
    print(f"\n=== Alignment Quality Distribution ===\n")

    high_confidence = db.query(Alignment).filter(
        Alignment.tenant_id == tenant_id,
        Alignment.status == "candidate",
        Alignment.confidence >= 0.85
    ).count()

    medium_confidence = db.query(Alignment).filter(
        Alignment.tenant_id == tenant_id,
        Alignment.status == "candidate",
        Alignment.confidence >= 0.70,
        Alignment.confidence < 0.85
    ).count()

    low_confidence = db.query(Alignment).filter(
        Alignment.tenant_id == tenant_id,
        Alignment.status == "candidate",
        Alignment.confidence < 0.70
    ).count()

    print(f"High confidence (≥0.85):    {high_confidence} candidates")
    print(f"Medium confidence (0.70-0.85): {medium_confidence} candidates")
    print(f"Low confidence (<0.70):     {low_confidence} candidates")

    print(f"\nTotal candidates for review: {candidate_alignments}")

    if candidate_alignments >= 20:
        print("\n✓ Sample alignment candidates successfully created!")
        print("Ready for review in the Alignment Workspace.")
    else:
        print(f"\n⚠ Expected 20+ candidates but found {candidate_alignments}")

finally:
    db.close()
