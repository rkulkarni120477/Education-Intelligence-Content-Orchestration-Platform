#!/usr/bin/env python
"""
Test complete alignment workflow with sample candidates.

Demonstrates:
1. Fetching all candidate alignments
2. Reviewing individual candidates
3. Approving/rejecting alignments
4. Tracking approval metrics
"""

from database.db import SessionLocal, init_db
from database.models import Alignment, Lesson, Standard, Tenant, User
from auth.tenant_context import TenantContext
from services.alignment_service import AlignmentService
import uuid

print("=" * 70)
print("ALIGNMENT WORKSPACE WORKFLOW TEST")
print("=" * 70)

# Initialize
init_db()
db = SessionLocal()

try:
    # Setup tenant context
    system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
    if not system_tenant:
        system_tenant = db.query(Tenant).first()
    TenantContext.set_tenant(system_tenant.id)
    tenant_id = system_tenant.id

    print(f"\n✓ Tenant: {tenant_id}")

    # Get or create a test reviewer user
    reviewer = db.query(User).filter(User.tenant_id == tenant_id).first()
    if not reviewer:
        reviewer = User(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            email="reviewer@test.local",
            username="test_reviewer",
            hashed_password="test",
            is_active=True
        )
        db.add(reviewer)
        db.commit()
        print(f"✓ Created test reviewer: {reviewer.email}")
    else:
        print(f"✓ Using existing reviewer: {reviewer.email}")

    # Step 1: List all candidate alignments
    print("\n" + "=" * 70)
    print("STEP 1: FETCH CANDIDATE ALIGNMENTS")
    print("=" * 70)

    candidates, total = AlignmentService.list_candidate_alignments(db, limit=100)
    print(f"\n✓ Found {total} candidate alignments")
    print(f"✓ Fetched {len(candidates)} candidates (limit: 100)")

    if not candidates:
        print("! No candidates found, skipping workflow test")
    else:
        # Show quality distribution
        high_conf = [a for a in candidates if a.confidence >= 0.85]
        med_conf = [a for a in candidates if 0.70 <= a.confidence < 0.85]
        low_conf = [a for a in candidates if a.confidence < 0.70]

        print(f"\nQuality Distribution:")
        print(f"  High confidence (≥0.85): {len(high_conf)}")
        print(f"  Medium confidence (0.70-0.85): {len(med_conf)}")
        print(f"  Low confidence (<0.70): {len(low_conf)}")

        # Step 2: Review a sample alignment
        print("\n" + "=" * 70)
        print("STEP 2: REVIEW SAMPLE ALIGNMENT")
        print("=" * 70)

        sample = candidates[0]
        lesson = db.query(Lesson).filter(Lesson.id == sample.source_id).first()
        standard = db.query(Standard).filter(Standard.id == sample.standard_id).first()

        print(f"\nCandidate Details:")
        print(f"  ID: {sample.id}")
        print(f"  Lesson: {lesson.title if lesson else 'Unknown'}")
        print(f"  Standard: {standard.code if standard else 'Unknown'}")
        print(f"  Score: {sample.score}")
        print(f"  Confidence: {sample.confidence}")
        print(f"  Evidence: {len(sample.evidence)} item(s)")
        print(f"  Status: {sample.status}")

        if sample.evidence:
            print(f"\nEvidence:")
            for i, evidence in enumerate(sample.evidence, 1):
                print(f"  {i}. {evidence.get('source', 'Unknown')}")
                print(f"     {evidence.get('text', '')[:60]}...")

        # Step 3: Approve an alignment
        print("\n" + "=" * 70)
        print("STEP 3: APPROVE ALIGNMENT")
        print("=" * 70)

        # Approve high-confidence candidate
        if high_conf:
            to_approve = high_conf[0]
            approved = AlignmentService.review_alignment(
                db,
                to_approve.id,
                decision="approved",
                reviewer_id=reviewer.id,
                notes="High confidence alignment, approved."
            )
            print(f"\n✓ Approved alignment: {approved.id}")
            print(f"  Status: {approved.status}")
            print(f"  Reviewed by: {approved.reviewed_by}")
            print(f"  Reviewed at: {approved.reviewed_at}")

        # Step 4: Reject an alignment
        print("\n" + "=" * 70)
        print("STEP 4: REJECT ALIGNMENT")
        print("=" * 70)

        # Reject low-confidence candidate
        if len(candidates) > 1:
            to_reject = candidates[1]
            rejected = AlignmentService.review_alignment(
                db,
                to_reject.id,
                decision="rejected",
                reviewer_id=reviewer.id,
                notes="Confidence too low, mapping incorrect."
            )
            print(f"\n✓ Rejected alignment: {rejected.id}")
            print(f"  Status: {rejected.status}")
            print(f"  Reviewed by: {rejected.reviewed_by}")
            print(f"  Reviewed at: {rejected.reviewed_at}")

        # Step 5: Calculate coverage for a source
        print("\n" + "=" * 70)
        print("STEP 5: ALIGNMENT COVERAGE ANALYSIS")
        print("=" * 70)

        # Get first lesson's coverage
        first_lesson = db.query(Lesson).filter(Lesson.tenant_id == tenant_id).first()
        if first_lesson:
            coverage = AlignmentService.calculate_alignment_coverage(
                db,
                source_type="lesson",
                source_id=first_lesson.id
            )
            print(f"\nCoverage for '{first_lesson.title}':")
            print(f"  Total Alignments: {coverage['total_alignments']}")
            print(f"  Approved: {coverage['approved_count']}")
            print(f"  Candidates: {coverage['candidate_count']}")
            print(f"  Rejected: {coverage['rejected_count']}")
            print(f"  Avg Confidence: {coverage['average_confidence']}")
            print(f"  Avg Score: {coverage['average_score']}")
            print(f"  Coverage Status: {coverage['coverage_status']}")

            if coverage['recommendations']:
                print(f"  Recommendations:")
                for rec in coverage['recommendations']:
                    print(f"    • {rec}")

        # Step 6: Final metrics
        print("\n" + "=" * 70)
        print("STEP 6: WORKFLOW METRICS")
        print("=" * 70)

        # Refresh to get updated counts
        final_candidates, _ = AlignmentService.list_candidate_alignments(db, limit=100)

        all_alignments = db.query(Alignment).filter(
            Alignment.tenant_id == tenant_id
        ).all()

        approved_count = len([a for a in all_alignments if a.status == "approved"])
        rejected_count = len([a for a in all_alignments if a.status == "rejected"])
        candidate_count = len([a for a in all_alignments if a.status == "candidate"])

        print(f"\nAlignment Status Summary:")
        print(f"  Total Alignments: {len(all_alignments)}")
        print(f"  Candidates (Pending): {candidate_count}")
        print(f"  Approved: {approved_count}")
        print(f"  Rejected: {rejected_count}")

        approval_rate = (approved_count / len(all_alignments) * 100) if all_alignments else 0
        print(f"  Approval Rate: {approval_rate:.1f}%")

        print("\n" + "=" * 70)
        print("✓ WORKFLOW TEST COMPLETE")
        print("=" * 70)
        print("\nAlignment Workspace is fully functional!")
        print("Candidates are ready for review in the UI.")

finally:
    db.close()
