#!/usr/bin/env python
"""Add missing standards and create new frameworks"""

from database.db import SessionLocal
from database.models import StandardFramework, Standard, Tenant
import uuid

db = SessionLocal()

try:
    # Get system tenant
    system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
    if not system_tenant:
        print("[ERROR] System tenant not found")
        exit(1)

    tenant_id = system_tenant.id

    # 1. ADD ENGLISH STANDARDS TO EXISTING FRAMEWORK
    print("[STEP 1] Adding English Language Arts standards...")
    english_fw = db.query(StandardFramework).filter(
        StandardFramework.name == "English Standards"
    ).first()

    if english_fw:
        english_standards = [
            ("K.RF.A.1", "Demonstrate understanding of spoken words, syllables, and sounds", "K", "English Language Arts"),
            ("1.RF.A.1", "Demonstrate understanding of syllables and sounds", "1", "English Language Arts"),
            ("2.RF.A.1", "Know and apply phonics decoding skills", "2", "English Language Arts"),
            ("3.L.A.1", "Demonstrate command of conventions of standard English", "3", "English Language Arts"),
            ("4.L.A.1", "Demonstrate command of conventions of standard English grammar", "4", "English Language Arts"),
            ("5.L.A.1", "Demonstrate command of conventions of standard English grammar", "5", "English Language Arts"),
        ]

        created = 0
        for code, description, grade, subject in english_standards:
            existing = db.query(Standard).filter(
                Standard.framework_id == english_fw.id,
                Standard.code == code
            ).first()
            if not existing:
                std = Standard(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    framework_id=english_fw.id,
                    code=code,
                    description=description,
                    grade=grade,
                    subject=subject,
                    domain=code.split('.')[0] if '.' in code else code.split('-')[0],
                    version="2020"
                )
                db.add(std)
                created += 1

        db.commit()
        print("[OK] Added {} English standards".format(created))
    else:
        print("[ERROR] English Standards framework not found")

    # 2. CREATE STATE STANDARDS FRAMEWORK
    print("\n[STEP 2] Creating State Standards framework...")
    state_fw = StandardFramework(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name="State Standards",
        authority="State Departments of Education",
        jurisdiction="United States",
        version="2023"
    )
    db.add(state_fw)
    db.commit()

    state_standards = [
        ("CA.ELA.K.1", "California ELA Standard Grade K", "K", "English Language Arts"),
        ("CA.MATH.1.1", "California Math Standard Grade 1", "1", "Mathematics"),
        ("TX.ELA.2.1", "Texas ELA Standard Grade 2", "2", "English Language Arts"),
        ("TX.MATH.3.1", "Texas Math Standard Grade 3", "3", "Mathematics"),
        ("NY.ELA.4.1", "New York ELA Standard Grade 4", "4", "English Language Arts"),
        ("NY.SCIENCE.5.1", "New York Science Standard Grade 5", "5", "Science"),
    ]

    created = 0
    for code, description, grade, subject in state_standards:
        std = Standard(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            framework_id=state_fw.id,
            code=code,
            description=description,
            grade=grade,
            subject=subject,
            domain=code.split('.')[1] if '.' in code else "State",
            version="2023"
        )
        db.add(std)
        created += 1

    db.commit()
    print("[OK] Created State Standards framework with {} standards".format(created))

    # 3. CREATE CSTA FRAMEWORK
    print("\n[STEP 3] Creating Computer Science Standards (CSTA) framework...")
    csta_fw = StandardFramework(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name="Computer Science Standards (CSTA)",
        authority="Computer Science Teachers Association",
        jurisdiction="United States",
        version="2017"
    )
    db.add(csta_fw)
    db.commit()

    csta_standards = [
        ("K-AP-10", "Identify ways people use computers", "K", "Computer Science"),
        ("1-AP-08", "Model sharing of information in everyday situations", "1", "Computer Science"),
        ("2-AP-10", "Model the way programs store and retrieve information", "2", "Computer Science"),
        ("3-AP-16", "Design and iteratively develop computational artifacts", "3", "Computer Science"),
        ("4-AP-13", "Create procedures with parameters and return values", "4", "Computer Science"),
        ("5-AP-12", "Create and name variables that store single values", "5", "Computer Science"),
        ("6-12-AP-20", "Evaluate and refine computational artifacts", "6-12", "Computer Science"),
    ]

    created = 0
    for code, description, grade, subject in csta_standards:
        std = Standard(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            framework_id=csta_fw.id,
            code=code,
            description=description,
            grade=grade,
            subject=subject,
            domain="Computer Science",
            version="2017"
        )
        db.add(std)
        created += 1

    db.commit()
    print("[OK] Created CSTA framework with {} standards".format(created))

    # 4. CREATE CTE FRAMEWORK
    print("\n[STEP 4] Creating Career & Technical Education (CTE) framework...")
    cte_fw = StandardFramework(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name="Career & Technical Education (CTE)",
        authority="Association for Career and Technical Education",
        jurisdiction="United States",
        version="2020"
    )
    db.add(cte_fw)
    db.commit()

    cte_standards = [
        ("HSF-1.1", "Health Science Foundation Level 1", "9-12", "Health Sciences"),
        ("IT-2.2", "Information Technology Level 2", "9-12", "Information Technology"),
        ("BUS-1.3", "Business Administration Level 1", "9-12", "Business"),
        ("MAG-2.1", "Manufacturing Level 2", "9-12", "Manufacturing"),
        ("AGR-1.2", "Agriculture Level 1", "9-12", "Agriculture"),
        ("HOS-2.3", "Hospitality and Tourism Level 2", "9-12", "Hospitality"),
    ]

    created = 0
    for code, description, grade, subject in cte_standards:
        std = Standard(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            framework_id=cte_fw.id,
            code=code,
            description=description,
            grade=grade,
            subject=subject,
            domain=code.split('-')[0],
            version="2020"
        )
        db.add(std)
        created += 1

    db.commit()
    print("[OK] Created CTE framework with {} standards".format(created))

    # VERIFY ALL FRAMEWORKS
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION:")
    print("=" * 70)

    all_frameworks = db.query(StandardFramework).all()
    total_standards = 0

    for fw in all_frameworks:
        count = db.query(Standard).filter(Standard.framework_id == fw.id).count()
        total_standards += count
        status = "OK" if count > 0 else "!"
        print("\n[{}] {}".format(status, fw.name))
        print("   Standards: {}".format(count))
        print("   Authority: {}".format(fw.authority))

    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print("Total Frameworks: {}".format(len(all_frameworks)))
    print("Total Standards: {}".format(total_standards))

except Exception as e:
    print("[ERROR] {}".format(str(e)))
    import traceback
    traceback.print_exc()
finally:
    db.close()
