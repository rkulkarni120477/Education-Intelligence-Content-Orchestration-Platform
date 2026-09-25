"""
Database migration for Phase 4: Skill Mappings, Recommendations, and Accessibility.

Creates tables for:
- SkillAlignment: Skill-to-content mappings
- GapAnalysis: Skill coverage gaps
- Recommendation: Curriculum improvements
- CoverageReport: Overall skill coverage
- AccessibilityAudit: Accessibility findings and remediation
"""

from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, Boolean, Text, JSON, Float, ForeignKey, UniqueConstraint
from datetime import datetime
import uuid


def upgrade(sqlalchemy_uri: str):
    """Apply migration - create Phase 4 tables."""
    from sqlalchemy import create_engine

    engine = create_engine(sqlalchemy_uri)
    metadata = MetaData()

    # SkillAlignment table
    skill_alignments = Table(
        'skill_alignments',
        metadata,
        Column('id', String(36), primary_key=True),
        Column('tenant_id', String(36), ForeignKey('tenants.id'), nullable=False, index=True),
        Column('workflow_id', String(36), ForeignKey('workflow_executions.id'), nullable=False, index=True),
        Column('skill_id', String(36), ForeignKey('workforce_skills.id'), nullable=False),
        Column('skill_name', String(255), nullable=False),
        Column('content_id', String(255), nullable=False),
        Column('content_title', String(255), nullable=False),
        Column('alignment_type', String(50), nullable=False),
        Column('proficiency_level', String(50), nullable=False),
        Column('confidence', Float, default=0.5),
        Column('evidence', JSON, default=[]),
        Column('supporting_objectives', JSON, default=[]),
        Column('status', String(50), default='candidate'),
        Column('reviewed_by', String(36), ForeignKey('users.id'), nullable=True),
        Column('reviewed_at', DateTime, nullable=True),
        Column('review_notes', Text, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow, index=True),
        Column('updated_at', DateTime, default=datetime.utcnow),
        UniqueConstraint('tenant_id', 'workflow_id', 'skill_id', 'content_id', name='uq_alignment'),
    )

    # GapAnalysis table
    gap_analyses = Table(
        'gap_analyses',
        metadata,
        Column('id', String(36), primary_key=True),
        Column('tenant_id', String(36), ForeignKey('tenants.id'), nullable=False, index=True),
        Column('workflow_id', String(36), ForeignKey('workflow_executions.id'), nullable=False, index=True),
        Column('skill_id', String(36), ForeignKey('workforce_skills.id'), nullable=False),
        Column('skill_name', String(255), nullable=False),
        Column('required_proficiency', String(50), nullable=False),
        Column('current_coverage', Float, default=0.0),
        Column('gap_severity', String(50), nullable=False),
        Column('gap_description', Text, nullable=False),
        Column('recommendations', JSON, default=[]),
        Column('status', String(50), default='identified'),
        Column('reviewed_by', String(36), ForeignKey('users.id'), nullable=True),
        Column('reviewed_at', DateTime, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow, index=True),
        Column('updated_at', DateTime, default=datetime.utcnow),
    )

    # Recommendation table
    recommendations = Table(
        'recommendations',
        metadata,
        Column('id', String(36), primary_key=True),
        Column('tenant_id', String(36), ForeignKey('tenants.id'), nullable=False, index=True),
        Column('workflow_id', String(36), ForeignKey('workflow_executions.id'), nullable=False, index=True),
        Column('type', String(50), nullable=False),
        Column('priority', String(50), nullable=False),
        Column('title', String(255), nullable=False),
        Column('description', Text, nullable=False),
        Column('rationale', Text, nullable=False),
        Column('implementation_steps', JSON, default=[]),
        Column('affected_skills', JSON, default=[]),
        Column('estimated_effort', String(50), nullable=False),
        Column('expected_impact', Text, nullable=True),
        Column('status', String(50), default='proposed'),
        Column('approved_by', String(36), ForeignKey('users.id'), nullable=True),
        Column('approved_at', DateTime, nullable=True),
        Column('approval_notes', Text, nullable=True),
        Column('implementation_notes', Text, nullable=True),
        Column('implemented_at', DateTime, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow, index=True),
        Column('updated_at', DateTime, default=datetime.utcnow),
    )

    # CoverageReport table
    coverage_reports = Table(
        'coverage_reports',
        metadata,
        Column('id', String(36), primary_key=True),
        Column('tenant_id', String(36), ForeignKey('tenants.id'), nullable=False, index=True),
        Column('workflow_id', String(36), ForeignKey('workflow_executions.id'), nullable=False, index=True),
        Column('total_skills', Integer, default=0),
        Column('total_content_items', Integer, default=0),
        Column('total_alignments', Integer, default=0),
        Column('covered_skills', JSON, default=[]),
        Column('partially_covered_skills', JSON, default=[]),
        Column('uncovered_skills', JSON, default=[]),
        Column('coverage_by_skill', JSON, default={}),
        Column('overall_coverage', Float, default=0.0),
        Column('alignment_confidence', Float, default=0.0),
        Column('status', String(50), default='generated'),
        Column('reviewed_by', String(36), ForeignKey('users.id'), nullable=True),
        Column('reviewed_at', DateTime, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow, index=True),
        Column('updated_at', DateTime, default=datetime.utcnow),
    )

    # AccessibilityAudit table
    accessibility_audits = Table(
        'accessibility_audits',
        metadata,
        Column('id', String(36), primary_key=True),
        Column('tenant_id', String(36), ForeignKey('tenants.id'), nullable=False, index=True),
        Column('workflow_id', String(36), ForeignKey('workflow_executions.id'), nullable=False, index=True),
        Column('scope', String(100), default='wcag-2.1-aa'),
        Column('total_findings', Integer, default=0),
        Column('critical_issues', Integer, default=0),
        Column('high_issues', Integer, default=0),
        Column('medium_issues', Integer, default=0),
        Column('low_issues', Integer, default=0),
        Column('findings', JSON, default=[]),
        Column('remediation_steps', JSON, default=[]),
        Column('status', String(50), default='completed'),
        Column('remediation_complete', Boolean, default=False),
        Column('remediation_verified_by', String(36), ForeignKey('users.id'), nullable=True),
        Column('remediation_verified_at', DateTime, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow, index=True),
        Column('updated_at', DateTime, default=datetime.utcnow),
    )

    # Create all tables
    metadata.create_all(engine)
    print("✓ Phase 4 tables created: SkillAlignment, GapAnalysis, Recommendation, CoverageReport, AccessibilityAudit")


def downgrade(sqlalchemy_uri: str):
    """Rollback migration - drop Phase 4 tables."""
    from sqlalchemy import create_engine, MetaData, inspect

    engine = create_engine(sqlalchemy_uri)
    inspector = inspect(engine)

    tables_to_drop = [
        'accessibility_audits',
        'coverage_reports',
        'recommendations',
        'gap_analyses',
        'skill_alignments',
    ]

    with engine.connect() as conn:
        for table_name in tables_to_drop:
            if table_name in inspector.get_table_names():
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"✓ Dropped table: {table_name}")
        conn.commit()
