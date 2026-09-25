"""
Import Common Core State Standards (CCSS) from the Common Standards Project API.

This migration:
1. Creates StandardFramework entries for Math and ELA
2. Populates Standard records with complete K-12 CCSS hierarchies
3. Assigns standards to a system tenant for shared use across all instances

Source: Common Standards Project API (http://api.commonstandardsproject.com/)
"""

from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def migrate(db: Session):
    """Load CCSS standards into the database."""
    try:
        from services.standards_loader import CCSSLoader

        logger.info("Starting CCSS standards import migration...")

        loader = CCSSLoader()
        results = loader.load_ccss_into_db(db)

        logger.info(f"[OK] CCSS import completed: {results['frameworks']} frameworks, {results['standards']} standards loaded")
        return True

    except ImportError as e:
        logger.warning(f"Skipping CCSS import: dependencies not available ({str(e)})")
        return True

    except Exception as e:
        logger.error(f"[FAIL] CCSS import failed: {str(e)}")
        raise
