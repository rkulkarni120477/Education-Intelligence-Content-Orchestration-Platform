"""
Common Core State Standards (CCSS) loader.

Loads CCSS K-12 standards from local JSON files.
Standards are loaded into StandardFramework and Standard models.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from database.models import StandardFramework, Standard, Tenant
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

LOCAL_CCSS_PATH = Path(__file__).parent.parent / "data" / "ccss"


class CCSSLoader:
    """Loads Common Core State Standards into the database."""

    def __init__(self, tenant_id: Optional[str] = None):
        """Initialize loader with optional tenant_id (defaults to system tenant)."""
        self.tenant_id = tenant_id

    def get_or_create_system_tenant(self, db: Session) -> str:
        """Get or create the system tenant for shared standards."""
        system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
        if system_tenant:
            logger.info(f"Using existing system tenant: {system_tenant.id}")
            return system_tenant.id

        system_tenant = Tenant(
            id=str(uuid.uuid4()),
            name="System",
            slug="system",
            type="system",
            status="active"
        )
        db.add(system_tenant)
        db.commit()
        logger.info(f"Created system tenant: {system_tenant.id}")
        return system_tenant.id

    def load_local_standards(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load CCSS standards from local JSON file."""
        standards_file = LOCAL_CCSS_PATH / "standards.json"

        if not standards_file.exists():
            logger.error(f"Standards file not found: {standards_file}")
            return {"Mathematics": [], "English Language Arts": []}

        try:
            with open(standards_file, 'r') as f:
                data = json.load(f)

            standards_by_subject = data.get("standards", {})
            logger.info(f"Loaded standards from {standards_file}")
            logger.info(f"  Math standards: {len(standards_by_subject.get('Mathematics', []))}")
            logger.info(f"  ELA standards: {len(standards_by_subject.get('English Language Arts', []))}")

            return standards_by_subject

        except Exception as e:
            logger.error(f"Failed to load local standards: {str(e)}")
            return {"Mathematics": [], "English Language Arts": []}

    def parse_grade_from_code(self, code: str) -> Optional[str]:
        """Extract grade level from standard code."""
        # CCSS codes are like "K.CC.A.1", "1.NBT.A.1", "11-12.A-SSE.A.1"
        parts = code.split('.')
        if parts:
            grade_part = parts[0]
            grade_mapping = {
                'K': 'K', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
                '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
                '11': '11-12', '11-12': '11-12'
            }
            return grade_mapping.get(grade_part)
        return None

    def load_ccss_into_db(self, db: Session, batch_size: int = 50) -> Dict[str, int]:
        """Load CCSS standards into the database."""
        if not self.tenant_id:
            self.tenant_id = self.get_or_create_system_tenant(db)

        # Load standards from local file
        standards_by_subject = self.load_local_standards()

        if not any(standards_by_subject.values()):
            logger.warning("No standards loaded from file")
            return {"frameworks": 0, "standards": 0}

        # Create frameworks
        frameworks = self._create_frameworks(db)

        standards_created = 0

        # Load Math standards
        if frameworks.get('Mathematics') and standards_by_subject.get("Mathematics"):
            logger.info(f"Loading {len(standards_by_subject['Mathematics'])} Math standards...")
            standards_created += self._load_standards_for_framework(
                db, standards_by_subject["Mathematics"], frameworks['Mathematics'], 'Mathematics', batch_size
            )

        # Load ELA standards
        if frameworks.get('English Language Arts') and standards_by_subject.get("English Language Arts"):
            logger.info(f"Loading {len(standards_by_subject['English Language Arts'])} ELA standards...")
            standards_created += self._load_standards_for_framework(
                db, standards_by_subject["English Language Arts"], frameworks['English Language Arts'], 'English Language Arts', batch_size
            )

        return {
            "frameworks": len(frameworks),
            "standards": standards_created
        }

    def _create_frameworks(self, db: Session) -> Dict[str, str]:
        """Create CCSS Math and ELA frameworks."""
        frameworks = {}

        # Math Framework
        math_fw = db.query(StandardFramework).filter(
            StandardFramework.tenant_id == self.tenant_id,
            StandardFramework.name == "Common Core State Standards - Mathematics"
        ).first()

        if not math_fw:
            math_fw = StandardFramework(
                id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                name="Common Core State Standards - Mathematics",
                authority="Common Core State Standards Initiative",
                jurisdiction="United States",
                version="2010",
                description="Standards for mathematical content and practice, K-12"
            )
            db.add(math_fw)
            db.flush()
            logger.info(f"Created Math framework: {math_fw.id}")
        else:
            logger.info(f"Using existing Math framework: {math_fw.id}")

        frameworks['Mathematics'] = math_fw.id

        # ELA Framework
        ela_fw = db.query(StandardFramework).filter(
            StandardFramework.tenant_id == self.tenant_id,
            StandardFramework.name == "Common Core State Standards - English Language Arts"
        ).first()

        if not ela_fw:
            ela_fw = StandardFramework(
                id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                name="Common Core State Standards - English Language Arts",
                authority="Common Core State Standards Initiative",
                jurisdiction="United States",
                version="2010",
                description="Standards for reading, writing, speaking, and listening, K-12"
            )
            db.add(ela_fw)
            db.flush()
            logger.info(f"Created ELA framework: {ela_fw.id}")
        else:
            logger.info(f"Using existing ELA framework: {ela_fw.id}")

        frameworks['English Language Arts'] = ela_fw.id

        db.commit()
        return frameworks

    def _load_standards_for_framework(
        self,
        db: Session,
        standards_list: List[Dict[str, Any]],
        framework_id: str,
        subject: str,
        batch_size: int = 50
    ) -> int:
        """Load standards for a specific framework."""
        created_count = 0
        skipped_count = 0

        for i, standard_data in enumerate(standards_list):
            try:
                code = standard_data.get('code')
                description = standard_data.get('description', '')

                if not code:
                    skipped_count += 1
                    continue

                # Check if standard already exists
                existing = db.query(Standard).filter(
                    Standard.tenant_id == self.tenant_id,
                    Standard.framework_id == framework_id,
                    Standard.code == code
                ).first()

                if existing:
                    skipped_count += 1
                    continue

                grade = self.parse_grade_from_code(code)

                # Parse domain from code (e.g., "CC" from "K.CC.A.1")
                domain = None
                parts = code.split('.')
                if len(parts) > 1:
                    domain = parts[1]

                standard = Standard(
                    id=str(uuid.uuid4()),
                    tenant_id=self.tenant_id,
                    framework_id=framework_id,
                    code=code,
                    description=str(description)[:1000],
                    grade=grade,
                    subject=subject,
                    domain=domain,
                    version="2010"
                )

                db.add(standard)
                created_count += 1

                # Commit in batches
                if (i + 1) % batch_size == 0:
                    db.commit()
                    logger.info(f"  Processed {i + 1}/{len(standards_list)} {subject} standards (created: {created_count}, skipped: {skipped_count})...")

            except Exception as e:
                logger.debug(f"Error loading standard {standard_data.get('code')}: {str(e)}")
                skipped_count += 1
                continue

        db.commit()
        logger.info(f"Completed {subject}: created {created_count}, skipped {skipped_count}")
        return created_count
