#!/usr/bin/env python
"""Test alignment API endpoint directly."""

import json
from fastapi.testclient import TestClient
from app import app
from database.db import SessionLocal, init_db
from database.models import Tenant
from auth.tenant_context import TenantContext

# Initialize DB
init_db()
db = SessionLocal()

# Get tenant
system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
TenantContext.set_tenant(system_tenant.id)
tenant_id = system_tenant.id

print(f"Testing API with Tenant ID: {tenant_id}\n")

# Create test client
try:
    client = TestClient(app)
except TypeError:
    # Fallback for older TestClient API
    from starlette.testclient import TestClient as StarletteTestClient
    client = StarletteTestClient(app)

# Test 1: Get candidates with status parameter
print("=" * 70)
print("TEST 1: GET /api/v1/alignments?status=candidate")
print("=" * 70)

response = client.get(
    "/api/v1/alignments?status=candidate&limit=5",
    headers={"X-Tenant-ID": tenant_id}
)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Response Type: {type(data)}")

    if isinstance(data, dict):
        print(f"Response Keys: {list(data.keys())}")

        if "alignments" in data:
            alignments = data['alignments']
            print(f"\n✓ Total candidates returned: {len(alignments)}")

            if alignments:
                print(f"\nFirst 3 candidates:")
                for i, alignment in enumerate(alignments[:3], 1):
                    print(f"\n  {i}. ID: {alignment.get('id')}")
                    print(f"     Source Type: {alignment.get('source_type')}")
                    print(f"     Standard ID: {alignment.get('standard_id')}")
                    print(f"     Score: {alignment.get('score')}")
                    print(f"     Confidence: {alignment.get('confidence')}")
                    print(f"     Status: {alignment.get('status')}")

                print("\n✓ API is working correctly!")
        else:
            print("! Response has no 'alignments' key")
            print(f"Response: {json.dumps(data, indent=2)}")

    elif isinstance(data, list):
        print(f"\n✓ Response is a list with {len(data)} items")
        if data:
            print(f"\nFirst alignment:")
            print(json.dumps(data[0], indent=2))
else:
    print(f"! API returned error: {response.text}")

# Test 2: Get without status filter (should default to candidate)
print("\n" + "=" * 70)
print("TEST 2: GET /api/v1/alignments (no status, should default to candidate)")
print("=" * 70)

response = client.get(
    "/api/v1/alignments?limit=5",
    headers={"X-Tenant-ID": tenant_id}
)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()

    if isinstance(data, dict) and "alignments" in data:
        alignments = data['alignments']
        print(f"✓ Total candidates returned: {len(alignments)}")

        if alignments:
            print(f"\nFirst candidate status: {alignments[0].get('status')}")
            if alignments[0].get('status') == 'candidate':
                print("✓ Status defaults to 'candidate' correctly")
else:
    print(f"! API returned error: {response.text}")

print("\n" + "=" * 70)
print("✓ API ENDPOINT TEST COMPLETE")
print("=" * 70)

db.close()
