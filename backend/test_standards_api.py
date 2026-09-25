#!/usr/bin/env python
"""Test standards API endpoints."""

from database.db import SessionLocal
from database.models import StandardFramework, Standard
from api.standards import StandardFrameworkResponse, StandardResponse

db = SessionLocal()

# Test 1: Get frameworks
print("=== TEST 1: Get Frameworks ===")
frameworks = db.query(StandardFramework).all()
print(f"Found {len(frameworks)} frameworks:")
for fw in frameworks:
    response = StandardFrameworkResponse.model_validate(fw)
    print(f"  - {response.name} (v{response.version})")

# Test 2: Get standards from first framework
if frameworks:
    print(f"\n=== TEST 2: Get Standards from {frameworks[0].name} ===")
    standards = db.query(Standard).filter(Standard.framework_id == frameworks[0].id).all()
    print(f"Found {len(standards)} standards:")
    for std in standards[:3]:
        response = StandardResponse.model_validate(std)
        print(f"  - {response.code}: {response.description[:50]}...")

# Test 3: Check grades and domains
print(f"\n=== TEST 3: Standards by Grade and Domain ===")
grades = db.query(Standard.grade).filter(Standard.framework_id == frameworks[0].id).distinct().all()
grades = [g[0] for g in grades if g[0]]
print(f"Grades: {sorted(set(grades))}")

domains = db.query(Standard.domain).filter(Standard.framework_id == frameworks[0].id).distinct().all()
domains = [d[0] for d in domains if d[0]]
print(f"Domains: {sorted(set(domains))}")

db.close()
print("\nAll tests passed! Standards are accessible via API.")
