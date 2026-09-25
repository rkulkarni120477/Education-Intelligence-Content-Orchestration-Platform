"""
Import Educational Standards frameworks.

This migration:
1. Creates StandardFramework entries for CCSS, NGSS, CSTA, CTE, and State Standards
2. Populates Standard records with K-12 standards
3. Assigns standards to a system tenant for shared use across all instances

Frameworks imported:
- Common Core State Standards (CCSS) - Math & ELA
- Next Generation Science Standards (NGSS) - Science
- Computer Science Standards (CSTA) - Computer Science
- Career & Technical Education (CTE) - Occupational skills
- California State Standards - Social Sciences

Sources: Local JSON files in data/standards/
"""

from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def migrate(db: Session):
    """Load all educational standards into the database."""
    try:
        from services.standards_loader import StandardsLoader

        logger.info("Starting educational standards import migration...")

        loader = StandardsLoader()
        results = loader.load_all_standards(db)

        logger.info(f"[OK] Standards import completed: {results['frameworks']} frameworks, {results['standards']} standards loaded")
        return True

    except ImportError as e:
        logger.warning(f"Skipping standards import: dependencies not available ({str(e)})")
        return True

    except Exception as e:
        logger.error(f"[FAIL] Standards import failed: {str(e)}")
        raise
