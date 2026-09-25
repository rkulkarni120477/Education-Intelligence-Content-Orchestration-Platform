from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Use database URL from centralized settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DATABASE_ECHO
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations(db: Session):
    """Run all pending migrations."""
    import importlib
    from pathlib import Path

    migrations_dir = Path(__file__).parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.py"))

    for migration_file in migration_files:
        if migration_file.name.startswith("__"):
            continue

        module_name = migration_file.stem
        try:
            spec = importlib.util.spec_from_file_location(
                f"migrations.{module_name}",
                migration_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'migrate'):
                logger.info(f"Running migration: {module_name}")
                module.migrate(db)
        except Exception as e:
            logger.error(f"Failed to run migration {module_name}: {str(e)}")
            raise


def init_db():
    """Initialize database with all tables and migrations."""
    from .models import Base
    import importlib.util

    # Create all tables from models first
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized: {SQLALCHEMY_DATABASE_URL}")

    # Run migrations
    db = SessionLocal()
    try:
        run_migrations(db)
    finally:
        db.close()

    # Add any missing columns (backward compatibility)
    with engine.begin() as connection:
        inspector = inspect(connection)
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue

            existing_columns = {
                column["name"] for column in inspector.get_columns(table.name)
            }
            for column in table.columns:
                if column.name in existing_columns:
                    continue

                try:
                    column_type = column.type.compile(dialect=connection.dialect)
                    connection.execute(
                        text(
                            f'ALTER TABLE "{table.name}" '
                            f'ADD COLUMN "{column.name}" {column_type}'
                        )
                    )
                except Exception as e:
                    logger.debug(f"Could not add column {column.name} to {table.name}: {str(e)}")

    logger.info("Database initialization completed successfully")


def get_session() -> Session:
    """Get a database session"""
    return SessionLocal()
