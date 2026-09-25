"""Test API endpoint directly"""
import sys
sys.path.insert(0, '/'.join(__file__.split('/')[:-1]))

from fastapi.testclient import TestClient
from app import app
from database.db import SessionLocal
from database.models import Tenant
from auth.tenant_context import TenantContext

client = TestClient(app)

db = SessionLocal()
try:
    # Get system tenant
    system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
    if not system_tenant:
        print("❌ System tenant not found")
        sys.exit(1)

    print(f"✅ Testing with system tenant: {system_tenant.id}\n")

    # Test content endpoint
    print("Testing GET /api/v1/content")
    response = client.get(
        "/api/v1/content?page=0&limit=50",
        headers={"X-Tenant-ID": system_tenant.id}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

    # Test standards endpoint
    print("Testing GET /api/v1/standards/frameworks")
    response = client.get(
        "/api/v1/standards/frameworks"
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

    # Test curriculum endpoint
    print("Testing GET /api/v1/curriculum?page=0&limit=50")
    response = client.get(
        "/api/v1/curriculum?page=0&limit=50",
        headers={"X-Tenant-ID": system_tenant.id}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

finally:
    db.close()
