#!/usr/bin/env python
"""Add profile_photo column to users table"""

from database.db import engine
from sqlalchemy import text

try:
    with engine.begin() as connection:
        # Try to add the column
        try:
            connection.execute(text(
                'ALTER TABLE users ADD COLUMN profile_photo VARCHAR(500)'
            ))
            print("[OK] Added profile_photo column to users table")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                print("[OK] profile_photo column already exists")
            else:
                raise

except Exception as e:
    print("[ERROR] Error adding column: " + str(e))
    import traceback
    traceback.print_exc()
    raise
