"""
Educational Standards Loader.

Loads multiple educational standards frameworks (CCSS, NGSS, CSTA, CTE, State Standards)
from local JSON files into StandardFramework and Standard models.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from database.models import StandardFramework, Standard, Tenant
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

STANDARDS_PATH = Path(__file__).parent.parent / "data" / "standards"

# Framework definitions: filename -> (framework_name, authority, jurisdiction)
FRAMEWORK_CONFIGS = {
    "ccss.json": {
        "Math": ("Common Core State Standards - Mathematics", "Common Core State Standards Initiative", "United States"),
        "ELA": ("Common Core State Standards - English Language Arts", "Common Core State Standards Initiative", "United States"),
    },
    "ngss.json": {
        "Science": ("Next Generation Science Standards", "NGSS Lead States", "United States"),
    },
    "csta.json": {
        "CS": ("Computer Science Standards (CSTA)", "Computer Science Teachers Association", "United States"),
    },
    "cte.json": {
        "CTE": ("Career & Technical Education Standards", "Association for Career and Technical Education", "United States"),
    },
    "ca_standards.json": {
        "CA": ("California State Standards", "California State Board of Education", "California"),
    },
}


class StandardsLoader:
    """Loads multiple educational standards frameworks from local JSON files."""

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

    def load_standards_from_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load standards from a local JSON file."""
        try:
            if not STANDARDS_PATH.exists():
                logger.warning(f"Standards directory not found: {STANDARDS_PATH}")
                return []

            file_path = STANDARDS_PATH / filename
            if not file_path.exists():
                logger.warning(f"Standards file not found: {file_path}")
                return []

            with open(file_path) as f:
                data = json.load(f)
                standards = data if isinstance(data, list) else data.get("standards", [])
                logger.info(f"Loaded {len(standards)} standards from {filename}")
                return standards

        except Exception as e:
            logger.error(f"Failed to load {filename}: {str(e)}")
            return []

    def parse_grade_from_code(self, code: str) -> Optional[str]:
        """Extract grade level from standard code."""
        # Support multiple code formats:
        # CCSS: K.CC.A.1, 1.NBT.A.1, 9-10.A-SSE.A.1, 11-12.A-SSE.A.1
        # NGSS: K-PS2-1, 1-LS1-1, 9-12-PS1-1
        # CSTA: K-AP-10, 1-AP-08, 9-12-AP-12
        # CTE: HSF-1.1, IT-2.2, 9-12 (no grade prefix)

        parts = code.split('-')
        if parts:
            grade_part = parts[0]
            grade_mapping = {
                'K': 'K', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
                '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
                '11': '11-12', '11-12': '11-12', '9-12': '9-12'
            }
            return grade_mapping.get(grade_part)

        # Fallback for CCSS-style codes (dot separated)
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

    def load_all_standards(self, db: Session) -> Dict[str, int]:
        """Load all available standards frameworks into the database."""
        if not self.tenant_id:
            self.tenant_id = self.get_or_create_system_tenant(db)

        total_frameworks = 0
        total_standards = 0

        # Load each framework
        for filename, framework_configs in FRAMEWORK_CONFIGS.items():
            standards_data = self.load_standards_from_file(filename)

            if not standards_data:
                continue

            for key, (framework_name, authority, jurisdiction) in framework_configs.items():
                logger.info(f"Loading {framework_name}...")

                # Create framework
                framework = self._create_framework(
                    db, framework_name, authority, jurisdiction, filename
                )

                # Load standards
                standards_created = self._load_standards_for_framework(
                    db, standards_data, framework.id, framework_name
                )

                total_frameworks += 1
                total_standards += standards_created

        return {
            "frameworks": total_frameworks,
            "standards": total_standards
        }

    def _create_framework(
        self,
        db: Session,
        name: str,
        authority: str,
        jurisdiction: str,
        source: str
    ) -> StandardFramework:
        """Create or get a standard framework."""
        framework = db.query(StandardFramework).filter(
            StandardFramework.tenant_id == self.tenant_id,
            StandardFramework.name == name
        ).first()

        if framework:
            logger.info(f"Using existing framework: {name}")
            return framework

        framework = StandardFramework(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            name=name,
            authority=authority,
            jurisdiction=jurisdiction,
            version="2020",
            description=f"Loaded from {source}"
        )
        db.add(framework)
        db.flush()
        logger.info(f"Created framework: {name}")
        return framework

    def _load_standards_for_framework(
        self,
        db: Session,
        standards_list: List[Dict[str, Any]],
        framework_id: str,
        framework_name: str,
        batch_size: int = 50
    ) -> int:
        """Load standards for a specific framework."""
        created_count = 0
        skipped_count = 0

        for i, standard_data in enumerate(standards_list):
            try:
                code = standard_data.get('code')
                description = standard_data.get('description', '')
                grade = standard_data.get('grade')
                subject = standard_data.get('subject', '')
                domain = standard_data.get('domain', '')

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

                # Parse grade if not provided
                if not grade:
                    grade = self.parse_grade_from_code(code)

                # Parse domain from code if not provided
                if not domain:
                    parts = code.split('-')
                    if len(parts) > 1:
                        domain = parts[1]
                    else:
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
                    version="2020"
                )

                db.add(standard)
                created_count += 1

                # Commit in batches
                if (i + 1) % batch_size == 0:
                    db.commit()
                    logger.info(f"  Processed {i + 1}/{len(standards_list)} standards (created: {created_count}, skipped: {skipped_count})...")

            except Exception as e:
                logger.debug(f"Error loading standard {standard_data.get('code')}: {str(e)}")
                skipped_count += 1
                continue

        db.commit()
        logger.info(f"Completed {framework_name}: created {created_count}, skipped {skipped_count}")
        return created_count
