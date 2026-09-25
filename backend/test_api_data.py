"""Test if API endpoints return data"""
import sys
sys.path.insert(0, '/'.join(__file__.split('/')[:-1]))

from database.db import SessionLocal
from database.models import Content, Tenant, User, Curriculum, Standard, StandardFramework, Alignment

db = SessionLocal()

try:
    # Check tenants
    tenants = db.query(Tenant).all()
    print(f"✅ Tenants: {len(tenants)}")
    for tenant in tenants:
        print(f"   - ID: {tenant.id}, Slug: {tenant.slug}, Name: {tenant.name}")

    if not tenants:
        print("❌ No tenants found!")
        sys.exit(1)

    system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
    if system_tenant:
        print(f"\n✅ System tenant found: {system_tenant.id}")

        # Check content
        content_items = db.query(Content).filter(Content.tenant_id == system_tenant.id).all()
        print(f"✅ Content items: {len(content_items)}")
        for item in content_items:
            print(f"   - {item.title} (status: {item.status}, tenant: {item.tenant_id})")

        # Check standards
        standards = db.query(Standard).filter(Standard.tenant_id == system_tenant.id).all()
        print(f"✅ Standards: {len(standards)}")
        for std in standards:
            print(f"   - {std.code}: {std.description[:50]}...")

        # Check curriculum
        curricula = db.query(Curriculum).filter(Curriculum.tenant_id == system_tenant.id).all()
        print(f"✅ Curriculum: {len(curricula)}")
        for curr in curricula:
            print(f"   - {curr.name} ({curr.subject})")

        # Check alignments
        alignments = db.query(Alignment).filter(Alignment.tenant_id == system_tenant.id).all()
        print(f"✅ Alignments: {len(alignments)}")
        for align in alignments:
            print(f"   - {align.source_type}:{align.source_id} -> {align.target_type}:{align.standard_id} (status: {align.status})")
    else:
        print("❌ System tenant not found!")

finally:
    db.close()
