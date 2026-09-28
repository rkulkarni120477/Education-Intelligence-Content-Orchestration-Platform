"""Add personal profile fields to users."""

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session


def migrate(db: Session):
    """Add missing profile columns without changing existing user records."""
    inspector = inspect(db.bind)
    if not inspector.has_table("users"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    column_definitions = {
        "first_name": "VARCHAR(100)",
        "last_name": "VARCHAR(100)",
        "age": "INTEGER",
        "date_of_birth": "DATE",
        "city": "VARCHAR(150)",
        "state": "VARCHAR(150)",
        "country": "VARCHAR(100)",
        "address": "TEXT",
        "zip_code": "VARCHAR(20)",
        "mobile_number": "VARCHAR(30)",
    }

    for column_name, column_type in column_definitions.items():
        if column_name not in existing_columns:
            db.execute(text(f'ALTER TABLE users ADD COLUMN "{column_name}" {column_type}'))

    db.commit()