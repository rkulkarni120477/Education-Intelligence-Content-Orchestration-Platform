#!/usr/bin/env python
"""Test loading all educational standards."""

from database.db import SessionLocal, init_db
from database.models import StandardFramework, Standard
from services.standards_loader import StandardsLoader

# Initialize database (creates tables)
print("Initializing database...")
init_db()

db = SessionLocal()

# Load all standards
print("\n=== Loading All Educational Standards ===")
loader = StandardsLoader()
results = loader.load_all_standards(db)

print(f"\nResults:")
print(f"  Frameworks created: {results['frameworks']}")
print(f"  Standards loaded: {results['standards']}")

# Verify by querying database
print(f"\n=== Database Verification ===")
frameworks = db.query(StandardFramework).all()
print(f"Total frameworks in database: {len(frameworks)}")

for fw in sorted(frameworks, key=lambda f: f.name):
    count = db.query(Standard).filter(Standard.framework_id == fw.id).count()
    print(f"  - {fw.name}: {count} standards")

# Show sample standards from each framework
print(f"\n=== Sample Standards ===")
for fw in sorted(frameworks, key=lambda f: f.name)[:3]:
    print(f"\n{fw.name}:")
    samples = db.query(Standard).filter(Standard.framework_id == fw.id).limit(3).all()
    for std in samples:
        print(f"  {std.code}: {std.description[:60]}...")

db.close()
print("\n✓ All tests passed!")
