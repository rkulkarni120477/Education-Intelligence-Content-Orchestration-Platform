#!/usr/bin/env python
"""Reset user password for development"""

from database.db import SessionLocal
from database.models import User
from auth.auth import get_password_hash

# Create session
db = SessionLocal()

try:
    # Find user
    user = db.query(User).filter(User.email == "rkulkarni@academian.com").first()

    if not user:
        print("[ERROR] User not found")
    else:
        # Update password
        user.hashed_password = get_password_hash("P@ssw0rd")
        user.is_active = True
        user.is_admin = True
        db.commit()
        print("[OK] Password reset for: " + user.email)
        print("     New password: P@ssw0rd")

except Exception as e:
    db.rollback()
    print("[ERROR] Error resetting password: " + str(e))
    raise
finally:
    db.close()
