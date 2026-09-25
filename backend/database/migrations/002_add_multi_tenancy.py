"""
Migration: Add multi-tenancy foundation and core domain models

This migration:
1. Creates Tenant and Organization tables
2. Adds tenant_id to all existing tenant-owned tables
3. Creates core domain model tables (Standards, Curriculum, Alignment, etc.)
4. Adds appropriate constraints and indexes
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
import uuid


def migrate(db: Session):
    """Apply migration to the database."""

    try:
        # Create tenants table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS tenants (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) UNIQUE NOT NULL,
                type VARCHAR(50) DEFAULT 'school',
                status VARCHAR(50) DEFAULT 'active',
                configuration JSON DEFAULT '{}',
                subscription_tier VARCHAR(50) DEFAULT 'professional',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create organizations table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS organizations (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                type VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                UNIQUE (tenant_id, name)
            )
        """))

        # Add tenant_id columns to existing tables
        _add_column_if_not_exists(db, "users", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "users", "organization_id", "VARCHAR(36)")
        _add_column_if_not_exists(db, "users", "role", "VARCHAR(50) DEFAULT 'user'")

        _add_column_if_not_exists(db, "projects", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "workflows", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "workflow_executions", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "agent_runs", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "content", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "content", "version", "INTEGER DEFAULT 1")
        _add_column_if_not_exists(db, "content_embeddings", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "skills", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "accessibility_audits", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "audit_logs", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "curriculum_workflows", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "workflow_checkpoints", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "content_chunks", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "skill_gaps", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")
        _add_column_if_not_exists(db, "generated_content", "tenant_id", "VARCHAR(36) NOT NULL DEFAULT ''")

        # Create core domain model tables
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS concepts (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                subject VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                UNIQUE (tenant_id, name)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS standard_frameworks (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                authority VARCHAR(255),
                jurisdiction VARCHAR(255),
                version VARCHAR(50),
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                UNIQUE (tenant_id, name, version)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS standards (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                framework_id VARCHAR(36) NOT NULL,
                parent_id VARCHAR(36),
                code VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                grade VARCHAR(50),
                subject VARCHAR(100),
                domain VARCHAR(255),
                strand VARCHAR(255),
                version VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (framework_id) REFERENCES standard_frameworks(id),
                FOREIGN KEY (parent_id) REFERENCES standards(id),
                UNIQUE (tenant_id, framework_id, code)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS curricula (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                version VARCHAR(50) DEFAULT '1.0',
                grade VARCHAR(50),
                subject VARCHAR(100),
                status VARCHAR(50) DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                UNIQUE (tenant_id, name, version)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS curriculum_units (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                curriculum_id VARCHAR(36) NOT NULL,
                parent_id VARCHAR(36),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                sequence INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (curriculum_id) REFERENCES curricula(id),
                FOREIGN KEY (parent_id) REFERENCES curriculum_units(id)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS learning_objectives (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                unit_id VARCHAR(36) NOT NULL,
                objective TEXT NOT NULL,
                cognitive_level VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (unit_id) REFERENCES curriculum_units(id)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS alignments (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                source_id VARCHAR(36) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                standard_id VARCHAR(36),
                objective_id VARCHAR(36),
                score FLOAT DEFAULT 0.0,
                confidence FLOAT DEFAULT 0.0,
                evidence JSON DEFAULT '[]',
                status VARCHAR(50) DEFAULT 'candidate',
                reviewed_by VARCHAR(36),
                reviewed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (standard_id) REFERENCES standards(id),
                FOREIGN KEY (objective_id) REFERENCES learning_objectives(id),
                UNIQUE (tenant_id, source_type, source_id, standard_id)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS lessons (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                curriculum_id VARCHAR(36) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                duration_minutes INTEGER,
                grade VARCHAR(50),
                subject VARCHAR(100),
                status VARCHAR(50) DEFAULT 'draft',
                model VARCHAR(100),
                model_version VARCHAR(50),
                prompt_version VARCHAR(50),
                content JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (curriculum_id) REFERENCES curricula(id)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS activities (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                lesson_id VARCHAR(36) NOT NULL,
                type VARCHAR(100),
                title VARCHAR(255) NOT NULL,
                instructions TEXT,
                duration_minutes INTEGER,
                differentiation JSON,
                status VARCHAR(50) DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS assessments (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                title VARCHAR(255) NOT NULL,
                assessment_type VARCHAR(100),
                description TEXT,
                status VARCHAR(50) DEFAULT 'draft',
                model VARCHAR(100),
                model_version VARCHAR(50),
                prompt_version VARCHAR(50),
                blueprint JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                UNIQUE (tenant_id, title)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS assessment_items (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                assessment_id VARCHAR(36) NOT NULL,
                type VARCHAR(50),
                question TEXT NOT NULL,
                answer_key JSON,
                distractors JSON,
                rationale TEXT,
                cognitive_level VARCHAR(50),
                sequence INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (assessment_id) REFERENCES assessments(id)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_artifacts (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                artifact_type VARCHAR(50) NOT NULL,
                source_id VARCHAR(36),
                source_workflow VARCHAR(255),
                model VARCHAR(100) NOT NULL,
                model_version VARCHAR(50),
                prompt_version VARCHAR(50),
                evidence JSON DEFAULT '[]',
                confidence FLOAT DEFAULT 0.0,
                status VARCHAR(50) DEFAULT 'draft',
                content JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """))

        db.execute(text("""
            CREATE TABLE IF NOT EXISTS reviews (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(36) NOT NULL,
                artifact_id VARCHAR(36) NOT NULL,
                artifact_type VARCHAR(50) NOT NULL,
                reviewer_id VARCHAR(36) NOT NULL,
                decision VARCHAR(50) NOT NULL,
                comments TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (reviewer_id) REFERENCES users(id)
            )
        """))

        # Create indexes for performance
        _create_index_if_not_exists(db, "idx_users_tenant", "users", "tenant_id")
        _create_index_if_not_exists(db, "idx_projects_tenant", "projects", "tenant_id")
        _create_index_if_not_exists(db, "idx_workflows_tenant", "workflows", "tenant_id")
        _create_index_if_not_exists(db, "idx_content_tenant", "content", "tenant_id")
        _create_index_if_not_exists(db, "idx_standards_tenant", "standards", "tenant_id")
        _create_index_if_not_exists(db, "idx_curricula_tenant", "curricula", "tenant_id")
        _create_index_if_not_exists(db, "idx_lessons_tenant", "lessons", "tenant_id")
        _create_index_if_not_exists(db, "idx_assessments_tenant", "assessments", "tenant_id")
        _create_index_if_not_exists(db, "idx_alignments_tenant", "alignments", "tenant_id")

        db.commit()
        print("[OK] Migration completed successfully")
        return True

    except Exception as e:
        db.rollback()
        print(f"✗ Migration failed: {str(e)}")
        return False


def _add_column_if_not_exists(db: Session, table: str, column: str, column_type: str):
    """Helper to add a column if it doesn't exist."""
    try:
        db.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))
    except:
        pass  # Column already exists


def _create_index_if_not_exists(db: Session, index_name: str, table: str, column: str):
    """Helper to create an index if it doesn't exist."""
    try:
        db.execute(text(f"CREATE INDEX {index_name} ON {table}({column})"))
    except:
        pass  # Index already exists
