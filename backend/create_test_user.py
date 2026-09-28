#!/usr/bin/env python
"""Create a test user for development"""

from database.db import SessionLocal
from database.models import User
from auth.auth import get_password_hash
import uuid

# Create session (skip init_db to avoid migration issues)
db = SessionLocal()

try:
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "rkulkarni@academian.com").first()

    if existing_user:
        print("[OK] User already exists: " + existing_user.email)
    else:
        # Create new test user
        test_user = User(
            id=str(uuid.uuid4()),
            email="rkulkarni@academian.com",
            username="rkulkarni",
            full_name="Rahul Kulkarni",
            hashed_password=get_password_hash("P@ssw0rd"),
            is_active=True,
            is_admin=True,
            tenant_id="default-tenant",
            organization_id="default-org"
        )
        db.add(test_user)
        db.commit()
        print("[OK] Created test user: " + test_user.email)
        print("     Username: " + test_user.username)
        print("     Password: P@ssw0rd")
        print("     Admin: " + str(test_user.is_admin))

except Exception as e:
    db.rollback()
    print("[ERROR] Error creating user: " + str(e))
    raise
finally:
    db.close()
