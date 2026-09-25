from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Academian Agentic Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./academian_platform.db"
    DATABASE_ECHO: bool = False

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # LangChain Configuration
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7

    # Vector Store
    VECTOR_STORE_TYPE: str = "chroma"  # faiss, chroma, or milvus
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    # Features
    ENABLE_HUMAN_REVIEW: bool = True
    ENABLE_MONITORING: bool = True
    MAX_CONCURRENT_AGENTS: int = 5

    # Timeouts
    AGENT_TIMEOUT: int = 300  # seconds
    WORKFLOW_TIMEOUT: int = 600  # seconds

    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str = "noreply@academian.com"
    SENDER_PASSWORD: str = ""
    SENDER_NAME: str = "Academian"

    # Frontend URLs
    FRONTEND_URL: str = "http://localhost:3002"
    PASSWORD_RESET_URL: str = "http://localhost:3002/auth/reset-password"
    EMAIL_VERIFICATION_URL: str = "http://localhost:3002/auth/verify-email"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


def get_database_path():
    """Get the path to the SQLite database file"""
    return Path(__file__).parent.parent / "data" / "academian_platform.db"
