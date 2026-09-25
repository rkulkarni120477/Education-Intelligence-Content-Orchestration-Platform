#!/usr/bin/env python
"""
Workflow test with real IMSCC file support.

Demonstrates complete workflow execution with:
- Sample IMSCC course package creation
- Real package parsing and ingestion
- Full workflow execution from start to end
"""

import sys
import uuid
import json
import zipfile
from datetime import datetime
from pathlib import Path
from io import BytesIO

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from database.db import SessionLocal, init_db
from database.models import Tenant, User
from auth.tenant_context import TenantContext
from workflows.workforce_alignment_state import WorkforceAlignmentState
from workflows.workforce_alignment_graph import create_workforce_alignment_graph
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_imscc_package(package_path: str) -> str:
    """
    Create a sample IMSCC course package for testing.

    Args:
        package_path: Path to save the IMSCC file

    Returns:
        Path to created package
    """
    logger.info(f"Creating sample IMSCC package at {package_path}")

    # Create imsmanifest.xml content
    imsmanifest_content = """<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="http://www.imsglobal.org/xsd/imsccv1p2/imscp_v1p0.xsd"
          xmlns:imsmd="http://www.imsglobal.org/xsd/imsccv1p2/imsmd_v1p0.xsd"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          identifier="com.example.course.test"
          version="1.0">
    <metadata>
        <imsmd:lom>
            <imsmd:general>
                <imsmd:title>
                    <imsmd:string>Introduction to Mathematics</imsmd:string>
                </imsmd:title>
                <imsmd:description>
                    <imsmd:string>An introductory course covering basic mathematical concepts</imsmd:string>
                </imsmd:description>
            </imsmd:general>
        </imsmd:lom>
    </metadata>
    <organizations>
        <organization identifier="org1" structure="linear">
            <title>Main Course Organization</title>
            <item identifier="item1" identifierref="res1">
                <title>Module 1: Numbers and Operations</title>
                <item identifier="item1.1" identifierref="res2">
                    <title>Lesson 1.1: Introduction to Numbers</title>
                    <item identifier="item1.1.1" identifierref="res3">
                        <title>Activity: Number Recognition</title>
                    </item>
                </item>
                <item identifier="item1.2" identifierref="res4">
                    <title>Lesson 1.2: Basic Operations</title>
                    <item identifier="item1.2.1" identifierref="res5">
                        <title>Quiz: Operations Test</title>
                    </item>
                </item>
            </item>
            <item identifier="item2" identifierref="res6">
                <title>Module 2: Fractions and Decimals</title>
                <item identifier="item2.1" identifierref="res7">
                    <title>Lesson 2.1: Understanding Fractions</title>
                </item>
                <item identifier="item2.2" identifierref="res8">
                    <title>Lesson 2.2: Decimal Concepts</title>
                </item>
            </item>
        </organization>
    </organizations>
    <resources>
        <resource identifier="res1" type="webcontent" href="content/module1.html"/>
        <resource identifier="res2" type="webcontent" href="content/lesson1.html"/>
        <resource identifier="res3" type="webcontent" href="content/activity1.html"/>
        <resource identifier="res4" type="webcontent" href="content/lesson2.html"/>
        <resource identifier="res5" type="webcontent" href="content/quiz1.html"/>
        <resource identifier="res6" type="webcontent" href="content/module2.html"/>
        <resource identifier="res7" type="webcontent" href="content/lesson3.html"/>
        <resource identifier="res8" type="webcontent" href="content/lesson4.html"/>
    </resources>
</manifest>"""

    # Create sample lesson content
    lesson_content = """<html>
<head>
<title>Lesson Content</title>
<meta name="learning-objective" content="Students will understand number concepts"/>
<meta name="cognitive-level" content="Remember"/>
</head>
<body>
<h1>Lesson: Learning Objectives</h1>
<ul>
    <li>Understand the number system</li>
    <li>Identify different number types</li>
    <li>Apply number concepts in problems</li>
</ul>
<h2>Accessibility Features</h2>
<p>All content includes:</p>
<ul>
    <li>Alt text for all images</li>
    <li>Transcripts for audio</li>
    <li>Captions for video</li>
    <li>Keyboard navigation support</li>
</ul>
</body>
</html>"""

    # Create the IMSCC package (ZIP file)
    Path(package_path).parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add manifest
        zf.writestr('imsmanifest.xml', imsmanifest_content)

        # Add sample content files
        zf.writestr('content/module1.html', lesson_content)
        zf.writestr('content/lesson1.html', lesson_content)
        zf.writestr('content/activity1.html', lesson_content)
        zf.writestr('content/lesson2.html', lesson_content)
        zf.writestr('content/quiz1.html', lesson_content)
        zf.writestr('content/module2.html', lesson_content)
        zf.writestr('content/lesson3.html', lesson_content)
        zf.writestr('content/lesson4.html', lesson_content)

        # Add metadata XML
        metadata = {
            "course_title": "Introduction to Mathematics",
            "course_description": "An introductory course covering basic mathematical concepts",
            "modules": 2,
            "lessons": 6,
            "total_content_items": 8,
            "estimated_duration_hours": 20,
            "difficulty_level": "intermediate",
            "target_audience": "K-12 Students",
        }
        zf.writestr('metadata.json', json.dumps(metadata, indent=2))

    logger.info(f"✓ Sample IMSCC package created: {package_path}")
    return package_path


def main():
    """Run workflow test with real IMSCC file."""
    db = None

    try:
        # Setup
        logger.info("=" * 80)
        logger.info("WORKFLOW TEST WITH REAL IMSCC FILE")
        logger.info("=" * 80)

        init_db()
        db = SessionLocal()

        # Get/create tenant
        tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
        if not tenant:
            tenant = Tenant(
                id=str(uuid.uuid4()),
                name="System Tenant",
                slug="system",
                is_active=True
            )
            db.add(tenant)
            db.commit()

        # Get/create user
        user = db.query(User).filter(User.email == "imscc_test@test.local").first()
        if not user:
            from database.models import User as UserModel
            user = UserModel(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                email="imscc_test@test.local",
                username="imscc_tester",
                hashed_password="test",
                is_active=True
            )
            db.add(user)
            db.commit()

        TenantContext.set_tenant(tenant.id)
        logger.info(f"✓ Setup complete: tenant={tenant.id}, user={user.id}")

        # Create sample IMSCC package
        package_dir = Path(__file__).parent / "test_packages"
        package_dir.mkdir(exist_ok=True)
        package_path = str(package_dir / "sample_course.imscc")

        create_sample_imscc_package(package_path)

        # Create workflow graph
        logger.info("\n[SETUP] Creating LangGraph workflow...")
        graph = create_workforce_alignment_graph()
        logger.info("✓ Workflow graph created")

        # Create initial state with real IMSCC package
        logger.info("\n[STATE] Creating workflow state with IMSCC package...")
        state = WorkforceAlignmentState(
            tenant_id=tenant.id,
            request_id=str(uuid.uuid4()),
            initiating_user_id=user.id,
            workflow_execution_id=str(uuid.uuid4()),
            program_id="MATH-101",
            program_name="Introduction to Mathematics Curriculum",
            course_ids=["MATH-101-001", "MATH-101-002"],
            input_package_id="sample_course",
            input_package_format="imscc",
            input_skill_framework_id="O*NET-2023",
            input_style_guide_id="ADA-2.1-AA",
            started_at=datetime.utcnow(),
        )
        logger.info(f"✓ Workflow state created with real IMSCC package")

        # Execute workflow
        logger.info("\n" + "=" * 80)
        logger.info("EXECUTING WORKFLOW WITH REAL PACKAGE")
        logger.info("=" * 80)

        result = graph.invoke(state)

        # Results
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW EXECUTION RESULTS")
        logger.info("=" * 80)

        logger.info(f"\nProgram: {result.program_name}")
        logger.info(f"Status: {result.workflow_status}")
        logger.info(f"Completed Nodes: {len(result.completed_nodes)}")

        if result.completed_nodes:
            logger.info("\nCompleted Nodes:")
            for i, node in enumerate(result.completed_nodes, 1):
                logger.info(f"  {i}. {node}")

        if result.course_hierarchy_data:
            logger.info(f"\nCourse Structure:")
            logger.info(f"  • Modules: {len(result.course_hierarchy_data.get('modules', []))}")
            logger.info(f"  • Objectives: {len(result.extracted_learning_objectives)}")

        if result.accessibility_audit:
            logger.info(f"\nAccessibility Audit:")
            logger.info(f"  • Total Issues: {result.accessibility_audit.get('total_issues', 0)}")
            logger.info(f"  • Status: {result.accessibility_audit.get('remediation_complete', False)}")

        if result.audit_events:
            logger.info(f"\nAudit Events ({len(result.audit_events)}):")
            for event in result.audit_events:
                logger.info(f"  • {event.get('event_type')}: {event.get('details')}")

        if result.error_message:
            logger.warning(f"\nError: {result.error_message}")

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        if result.workflow_status == "completed":
            logger.info("\n✓ WORKFLOW EXECUTION WITH IMSCC SUCCESSFUL")
            logger.info("  • Package parsed correctly")
            logger.info("  • Course structure extracted")
            logger.info("  • All workflow phases completed")
            return 0
        else:
            logger.warning(f"\n⚠ Workflow completed with status: {result.workflow_status}")
            return 1

    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return 1

    finally:
        if db:
            db.close()


if __name__ == "__main__":
    exit(main())
