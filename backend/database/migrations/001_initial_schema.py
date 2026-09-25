"""
Initial schema migration.

This creates the base tables from the SQLAlchemy models.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


def migrate(db: Session):
    """Apply initial migration."""
    # This is handled by Base.metadata.create_all() in init_db()
    print("[OK] Initial schema created from SQLAlchemy models")
    return True
