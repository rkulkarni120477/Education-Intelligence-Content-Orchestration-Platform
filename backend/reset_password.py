from database.db import SessionLocal
from database.models import User
from auth.auth import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.email == "rkulkarni@academian.com").first()

if user:
    user.hashed_password = get_password_hash("Password123!")
    db.commit()
    print("Password reset successfully for rkulkarni@academian.com")
else:
    print("User not found")
