#!/usr/bin/env python
"""Update profile photo for user"""

from database.db import SessionLocal
from database.models import User
import os
import shutil

# Create session
db = SessionLocal()

try:
    # Find user
    user = db.query(User).filter(User.email == "rkulkarni@academian.com").first()

    if not user:
        print("[ERROR] User not found")
    else:
        # Create uploads directory
        uploads_dir = "data/uploads/profiles"
        os.makedirs(uploads_dir, exist_ok=True)

        # Source image path (the new photo)
        source_image = r"C:\Users\RAHULS~1\AppData\Local\Temp\claude\c--Users-RahulSudhakar-source-repos-Education-Intelligence---Content-Orchestration-Platform\2e00c0fc-7d1d-4daf-9fd0-96b93404f44b\images\30.png"

        # Destination path
        filename = user.id + "_profile.png"
        dest_image = os.path.join(uploads_dir, filename)

        # Remove old photo if it exists
        if os.path.exists(dest_image):
            os.remove(dest_image)
            print("[OK] Removed old profile photo")

        # Copy new image
        shutil.copy2(source_image, dest_image)

        # Update user profile photo
        user.profile_photo = dest_image
        db.commit()

        print("[OK] Profile photo updated for: " + user.email)
        print("     Photo path: " + dest_image)
        print("     File size: " + str(os.path.getsize(dest_image)) + " bytes")

except Exception as e:
    db.rollback()
    print("[ERROR] Error updating photo: " + str(e))
    import traceback
    traceback.print_exc()
    raise
finally:
    db.close()
