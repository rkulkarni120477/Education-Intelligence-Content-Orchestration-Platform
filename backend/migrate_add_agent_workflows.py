#!/usr/bin/env python3
"""
Migration script to add agent workflow execution columns to Workflow table.

This script adds:
- assigned_agents: JSON list of agent IDs that can execute this workflow
- execution_trigger: trigger type (manual, event-driven, scheduled)
- is_automatable: boolean flag indicating if workflow can be auto-executed
"""

from sqlalchemy import text
import logging
from database.db import SessionLocal, engine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_column_exists(connection, table_name, column_name):
    """Check if a column exists in a table."""
    try:
        # For SQLite
        result = connection.execute(
            text(f"PRAGMA table_info({table_name})")
        )
        columns = [row[1] for row in result.fetchall()]
        return column_name in columns
    except Exception:
        # For other databases, try a different approach
        try:
            connection.execute(
                text(f"SELECT {column_name} FROM {table_name} LIMIT 1")
            )
            return True
        except Exception:
            return False


def add_column_if_not_exists(connection, table_name, column_name, column_def):
    """Add a column if it doesn't already exist."""
    if not check_column_exists(connection, table_name, column_name):
        logger.info(f"Adding column {table_name}.{column_name}")
        try:
            connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_def}"))
            connection.commit()
            logger.info(f"✓ Successfully added {column_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding column {column_name}: {str(e)}")
            connection.rollback()
            return False
    else:
        logger.info(f"Column {table_name}.{column_name} already exists")
        return True


def migrate():
    """Run the migration."""
    logger.info("Starting migration: add_agent_workflows")

    try:
        with engine.connect() as connection:
            # Add assigned_agents column
            add_column_if_not_exists(
                connection,
                "workflows",
                "assigned_agents",
                "assigned_agents JSON DEFAULT '[]'",
            )

            # Add execution_trigger column
            add_column_if_not_exists(
                connection,
                "workflows",
                "execution_trigger",
                "execution_trigger VARCHAR(50) DEFAULT 'manual'",
            )

            # Add is_automatable column
            add_column_if_not_exists(
                connection,
                "workflows",
                "is_automatable",
                "is_automatable BOOLEAN DEFAULT FALSE",
            )

            # Also update AgentRun table to use workflow_execution_id instead of execution_id
            if check_column_exists(connection, "agent_runs", "execution_id"):
                logger.info("Checking AgentRun table for column rename...")
                try:
                    # For SQLite, we need to rename the column using a more complex procedure
                    # Try to add new column first
                    if not check_column_exists(
                        connection, "agent_runs", "workflow_execution_id"
                    ):
                        # Copy data and rename
                        connection.execute(
                            text(
                                """
                            ALTER TABLE agent_runs ADD COLUMN workflow_execution_id VARCHAR(36)
                            """
                            )
                        )
                        connection.execute(
                            text(
                                """
                            UPDATE agent_runs SET workflow_execution_id = execution_id
                            """
                            )
                        )
                        connection.commit()
                        logger.info(
                            "✓ Successfully migrated execution_id to workflow_execution_id"
                        )
                except Exception as e:
                    logger.warning(
                        f"Could not migrate AgentRun column: {str(e)}"
                    )
                    connection.rollback()

        logger.info("✓ Migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
