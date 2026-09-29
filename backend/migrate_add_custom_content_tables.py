#!/usr/bin/env python3
"""
Migration script to add custom content development tables.

Creates:
- custom_content_conversations
- custom_content_messages
- custom_content_files
"""

from sqlalchemy import text
import logging
from database.db import SessionLocal, engine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def table_exists(connection, table_name):
    """Check if a table exists in the database."""
    try:
        result = connection.execute(
            text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        )
        return result.fetchone() is not None
    except Exception:
        return False


def migrate():
    """Run the migration."""
    logger.info("Starting migration: add_custom_content_tables")

    try:
        with engine.connect() as connection:
            # Create custom_content_conversations table
            if not table_exists(connection, "custom_content_conversations"):
                logger.info("Creating custom_content_conversations table...")
                connection.execute(text("""
                    CREATE TABLE custom_content_conversations (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        is_archived BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        UNIQUE (tenant_id, user_id, id)
                    )
                """))
                connection.execute(text("CREATE INDEX idx_conversations_tenant ON custom_content_conversations(tenant_id)"))
                connection.execute(text("CREATE INDEX idx_conversations_user ON custom_content_conversations(user_id)"))
                connection.execute(text("CREATE INDEX idx_conversations_created ON custom_content_conversations(created_at)"))
                connection.commit()
                logger.info("✓ Created custom_content_conversations table")
            else:
                logger.info("✓ custom_content_conversations table already exists")

            # Create custom_content_messages table
            if not table_exists(connection, "custom_content_messages"):
                logger.info("Creating custom_content_messages table...")
                connection.execute(text("""
                    CREATE TABLE custom_content_messages (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id VARCHAR(36) NOT NULL,
                        conversation_id VARCHAR(36) NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        content TEXT NOT NULL,
                        message_type VARCHAR(50) DEFAULT 'text',
                        metadata JSON DEFAULT '{}',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                        FOREIGN KEY (conversation_id) REFERENCES custom_content_conversations(id)
                    )
                """))
                connection.execute(text("CREATE INDEX idx_messages_tenant ON custom_content_messages(tenant_id)"))
                connection.execute(text("CREATE INDEX idx_messages_conversation ON custom_content_messages(conversation_id)"))
                connection.execute(text("CREATE INDEX idx_messages_created ON custom_content_messages(created_at)"))
                connection.commit()
                logger.info("✓ Created custom_content_messages table")
            else:
                logger.info("✓ custom_content_messages table already exists")

            # Create custom_content_files table
            if not table_exists(connection, "custom_content_files"):
                logger.info("Creating custom_content_files table...")
                connection.execute(text("""
                    CREATE TABLE custom_content_files (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        conversation_id VARCHAR(36) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        file_type VARCHAR(50) NOT NULL,
                        mime_type VARCHAR(100),
                        path VARCHAR(500) NOT NULL,
                        size INTEGER DEFAULT 0,
                        content TEXT,
                        is_generated BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (conversation_id) REFERENCES custom_content_conversations(id),
                        UNIQUE (conversation_id, name)
                    )
                """))
                connection.execute(text("CREATE INDEX idx_files_tenant ON custom_content_files(tenant_id)"))
                connection.execute(text("CREATE INDEX idx_files_conversation ON custom_content_files(conversation_id)"))
                connection.execute(text("CREATE INDEX idx_files_created ON custom_content_files(created_at)"))
                connection.commit()
                logger.info("✓ Created custom_content_files table")
            else:
                logger.info("✓ custom_content_files table already exists")

        logger.info("✓ Migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
