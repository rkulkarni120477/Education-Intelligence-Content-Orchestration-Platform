"""
Database seeding script - creates sample data for testing and development
Run with: python scripts/seed_data.py
"""

import sys
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.insert(0, '/'.join(__file__.split('/')[:-2]))

from database.db import SessionLocal, Base, engine
from database.models import (
    Tenant, User, Content, Curriculum, CurriculumUnit,
    LearningObjective, Standard, StandardFramework, Alignment
)
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_database():
    """Seed the database with sample data."""

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Clear existing data (optional - comment out if you want to preserve data)
        # db.query(Alignment).delete()
        # db.query(LearningObjective).delete()
        # db.query(CurriculumUnit).delete()
        # db.query(Curriculum).delete()
        # db.query(Content).delete()
        # db.query(Standard).delete()
        # db.query(StandardFramework).delete()
        # db.query(User).delete()
        # db.query(Tenant).delete()
        # db.commit()

        # Create sample tenant
        tenant = Tenant(
            id=str(uuid.uuid4()),
            name="Test School District",
            slug="test-school-district",
            type="district",
            status="active",
            subscription_tier="professional"
        )
        db.add(tenant)
        db.flush()
        tenant_id = tenant.id

        # Create sample user
        user = User(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            email="admin@testschool.edu",
            username="admin",
            full_name="Admin User",
            hashed_password=pwd_context.hash("admin123"),
            role="admin",
            is_active=True,
            is_admin=True,
            email_verified=True
        )
        db.add(user)
        db.flush()
        user_id = user.id

        # Create sample content
        content_items = [
            Content(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                title="Introduction to Fractions",
                content_type="lesson",
                source="curriculum",
                raw_content="This lesson covers understanding fractions, comparing fractions, and adding/subtracting fractions.",
                status="ingested",
                version=1,
                created_at=datetime.utcnow()
            ),
            Content(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                title="Water Cycle Learning Module",
                content_type="module",
                source="curriculum",
                raw_content="The water cycle consists of evaporation, condensation, and precipitation.",
                status="ingested",
                version=1,
                created_at=datetime.utcnow()
            ),
            Content(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                title="Photosynthesis Quiz",
                content_type="assessment",
                source="curriculum",
                raw_content="Test questions on photosynthesis and plant biology.",
                status="ingested",
                version=1,
                created_at=datetime.utcnow()
            ),
            Content(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                title="Revolutionary War Historical Analysis",
                content_type="lesson",
                source="curriculum",
                raw_content="Analysis of primary sources from the American Revolutionary War.",
                status="ingested",
                version=1,
                created_at=datetime.utcnow()
            ),
        ]

        for content in content_items:
            db.add(content)
        db.flush()

        # Create standard frameworks
        math_framework = StandardFramework(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name="Common Core State Standards - Mathematics",
            code="CCSS-Math",
            source="Common Core",
            version="2010",
            description="K-12 Mathematics standards"
        )
        db.add(math_framework)
        db.flush()

        science_framework = StandardFramework(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name="Next Generation Science Standards",
            code="NGSS",
            source="NGSS Lead States",
            version="2013",
            description="K-12 Science standards"
        )
        db.add(science_framework)
        db.flush()

        # Create sample standards
        standards = [
            Standard(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                framework_id=math_framework.id,
                code="4.NF.A.1",
                title="Understand fractions as division",
                description="Explain a fraction a/b as the quantity formed by a parts of size 1/b",
                level="4",
                created_at=datetime.utcnow()
            ),
            Standard(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                framework_id=science_framework.id,
                code="5-ESS2-1",
                title="Water Cycle",
                description="Develop a model to describe that matter is made of particles",
                level="5",
                created_at=datetime.utcnow()
            ),
            Standard(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                framework_id=science_framework.id,
                code="6-LS1-1",
                title="Photosynthesis and Plant Life",
                description="Conduct and describe investigations that provide evidence for how plants get the materials they need to grow",
                level="6",
                created_at=datetime.utcnow()
            ),
        ]

        for standard in standards:
            db.add(standard)
        db.flush()

        # Create sample curriculum
        curriculum = Curriculum(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name="Grade 4 Mathematics Curriculum",
            description="Complete curriculum for 4th grade math",
            subject="Mathematics",
            grade="4",
            status="draft",
            version="1.0",
            created_at=datetime.utcnow()
        )
        db.add(curriculum)
        db.flush()

        # Create curriculum units
        unit = CurriculumUnit(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            curriculum_id=curriculum.id,
            title="Fractions Unit",
            description="Understanding and working with fractions",
            sequence=1,
            created_at=datetime.utcnow()
        )
        db.add(unit)
        db.flush()

        # Create learning objective
        objective = LearningObjective(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            unit_id=unit.id,
            objective="Students will understand fractions as parts of a whole",
            cognitive_level="understand",
            created_at=datetime.utcnow()
        )
        db.add(objective)
        db.flush()

        # Create sample alignments
        alignments = [
            Alignment(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                source_type="content",
                source_id=content_items[0].id,
                target_type="standard",
                standard_id=standards[0].id,
                score=0.95,
                confidence=0.92,
                evidence=["Content directly covers fraction concepts", "Aligns with CCSS 4.NF.A.1"],
                status="approved",
                reviewed_by=user_id,
                reviewed_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            ),
            Alignment(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                source_type="content",
                source_id=content_items[1].id,
                target_type="standard",
                standard_id=standards[1].id,
                score=0.88,
                confidence=0.85,
                evidence=["Module covers water cycle process", "Aligns with NGSS 5-ESS2-1"],
                status="approved",
                reviewed_by=user_id,
                reviewed_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            ),
            Alignment(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                source_type="content",
                source_id=content_items[2].id,
                target_type="standard",
                standard_id=standards[2].id,
                score=0.91,
                confidence=0.88,
                evidence=["Assessment tests photosynthesis knowledge", "Aligns with NGSS 6-LS1-1"],
                status="candidate",
                created_at=datetime.utcnow()
            ),
            Alignment(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                source_type="objective",
                source_id=objective.id,
                target_type="standard",
                standard_id=standards[0].id,
                score=0.93,
                confidence=0.90,
                evidence=["Learning objective directly targets fraction understanding"],
                status="approved",
                reviewed_by=user_id,
                reviewed_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            ),
        ]

        for alignment in alignments:
            db.add(alignment)

        # Commit all changes
        db.commit()

        print("✅ Database seeded successfully!")
        print(f"   - Tenant: {tenant.name}")
        print(f"   - User: {user.email}")
        print(f"   - Content items: {len(content_items)}")
        print(f"   - Standards: {len(standards)}")
        print(f"   - Curriculum: {curriculum.name}")
        print(f"   - Alignments: {len(alignments)}")
        print("\n📋 Sample data is now available for testing!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
