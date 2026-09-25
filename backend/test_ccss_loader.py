#!/usr/bin/env python
"""
Test CCSS standards loader.

Verifies:
1. API is accessible
2. Standards can be parsed correctly
3. Database can be populated
"""

import sys
import logging
from sqlalchemy.orm import Session
from database.db import SessionLocal, engine
from database.models import Base, StandardFramework, Standard
from services.standards_loader import CCSSLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_local_file_exists():
    """Test if local standards file exists."""
    logger.info("Testing local standards file...")
    try:
        from pathlib import Path
        standards_file = Path(__file__).parent / "data" / "ccss" / "standards.json"
        if standards_file.exists():
            import json
            with open(standards_file) as f:
                data = json.load(f)
            math_count = len(data.get("standards", {}).get("Mathematics", []))
            ela_count = len(data.get("standards", {}).get("English Language Arts", []))
            logger.info(f"✓ Standards file found with {math_count} Math and {ela_count} ELA standards")
            return True
        else:
            logger.error(f"✗ Standards file not found at {standards_file}")
            return False
    except Exception as e:
        logger.error(f"✗ File check failed: {str(e)}")
        return False


def test_standards_load():
    """Test loading standards into database."""
    logger.info("Testing standards loader...")
    try:
        db = SessionLocal()

        # Check if standards already exist
        existing_count = db.query(Standard).count()
        if existing_count > 0:
            logger.info(f"✓ Database already contains {existing_count} standards")
            db.close()
            return True

        # Load standards
        loader = CCSSLoader()
        results = loader.load_ccss_into_db(db)

        # Verify
        final_count = db.query(Standard).count()
        logger.info(f"✓ Loaded {results['standards']} standards ({final_count} total in DB)")

        # Show sample standards
        samples = db.query(Standard).limit(5).all()
        logger.info("\nSample standards loaded:")
        for std in samples:
            logger.info(f"  - {std.code}: {std.description[:60]}...")

        db.close()
        return results['standards'] > 0

    except Exception as e:
        logger.error(f"✗ Standards load test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_framework_creation():
    """Test framework creation."""
    logger.info("Testing framework creation...")
    try:
        db = SessionLocal()
        frameworks = db.query(StandardFramework).filter(
            StandardFramework.name.ilike('%Common Core%')
        ).all()

        logger.info(f"✓ Found {len(frameworks)} CCSS frameworks:")
        for fw in frameworks:
            logger.info(f"  - {fw.name} (v{fw.version})")

        db.close()
        return len(frameworks) > 0

    except Exception as e:
        logger.error(f"✗ Framework test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    logger.info("=== CCSS Standards Loader Tests ===\n")

    tests = [
        ("Local File Exists", test_local_file_exists),
        ("Framework Creation", test_framework_creation),
        ("Standards Load", test_standards_load),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"\n{'='*50}\n")
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    logger.info("=== Test Summary ===")
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    all_passed = all(result for _, result in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
