from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Education Intelligence & Content Orchestration Platform"
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

    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUFWN0VIUEdDVkhVWVVYRkM0JTJGMjAyNjA5MjglMkZhcC1zb3V0aC0xJTJGYmVkcm9jayUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwOTI4VDEyMTA1MFomWC1BbXotRXhwaXJlcz00MzIwMCZYLUFtei1TZWN1cml0eS1Ub2tlbj1JUW9KYjNKcFoybHVYMlZqRUd3YUNtRndMWE52ZFhSb0xURWlSakJFQWlBbmpuRnFwblVyMWdpRTQ4ZklqejN5UGg1a25Ia2tHdEIxY0NXbkFUTUEyUUlnUiUyRmpPenZaUjluNjFVS0dvZVJWOWJUTyUyQlY0SzNyYkcwdU5pSVN2VHNXVG9xZ0FNSU5SQURHZ3cwTVRBME5UTTBPRGMzT0RZaURIMlNvSUZNJTJGYVZ0MUJmNEV5cmRBblUlMkJQcDdoOE85JTJGem13dk1ZN0Jyc0ZobThvM0tXS3kxaTdNVkolMkZab3JVSWdTZVZNSUZRejZQVjZpU2dQa1JtWHJDUiUyQm8lMkI1Q3NkaGtzY1NhNG94cjBIUmphVG5zbHowMTh3ZDM5ZmZEdXp6eXI3ZTMzN3plY3p0NXBrbGVhQ0h1MjB0dmM1JTJGNnBMck4lMkZjVjZDenptUVklMkZDbGdRZFQlMkZZcWlJN2JGcG9PQzNveEcwMFlHUEpDZkdOUU9HcXFLTDR1WiUyRnJYNkhnMiUyRnY5dGxHQmM3ZGdqJTJCSGE2UndacCUyQnBLS0ZLbXFPMENFVzY2cDFnRGFwRDYwend1alEwRU9vJTJGQnV0TU15V1VaN05zS3lwJTJCa1NCRDZIY0FOMzY0cDV6dzNtUUdFdXFMN1hrTTF5Sk1YWUVpYiUyRlZyTDBRRFFOeFpYNjVTd1B3NCUyQjRrNUNmZXRQNnQ1aUxkV0VZaUZZcyUyRm9YcG1iZXBxOExDMGFWZmwlMkZ5ajYlMkY2NEJJa3VwRjM4b1h1RDVyWHo4dFl0NzFLeWc4aDJZYWFoazBzOEVBTFludENlQ01kVlIxZiUyQmE1emdkZ2haSHVwaWRXVFk4dXZta2NxSEJKZ3pNYUlzRWc1bUVIdXZsY3d1YzdvMVFZNmtBSk01MkkxVVlKVXVZbmk0eWNITVMlMkY1UzJDRUFabkR3UjJCR0E2cG91WjhPS2wzS0FvU0FCWTV1WDNvRVNCTm5CUWJoS0VLRWFTbGNpbXNvZDYyZWRidmtMd1hnbjJNdmpSVFRuZkVNcUdlZ2o5TVM2b0h2ZTFrTE50MmhEanlTNEI3ODJwVDhyemVwOEFyZnAlMkJubUtkaktReTRMZWdNZzJQWWxtNGlCSk5MeDFJZFZLYzZEYTV6bGpVSVZGdnBaQVdua2NvNWNpQUx2am1RM3Y3dVZBYkMyZk05Unpqa2VZbk1iZlFrQ1preFplNHhLUEVyeVByMG9mMlRNeEtxNmsycmp2TGFkUmF6RkRGcHczOWdXd3M3T3NDbDQ4d09hVmJFTWp1emxuaHhUWEx1Y1B1bmFmJTJGTzN3cjFMJTJGaVV0U0xTdTlsazN2OUN2enpTOUZYem9hRVQ1WWYxQmpJc25HVCUyRlBDeGJFM1BKV2clM0QlM0QmWC1BbXotU2lnbmF0dXJlPWExY2MwZmE3NzJjMjYzMGZmNTJiYTFmNGZkY2MzNjMwNDJlYmI4MDJmOGI4YjkxY2JmOGJkN2VlMDZjZWQyMzMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JlZlcnNpb249MQ==

    # LLM Configuration (AWS Bedrock)
    LLM_PROVIDER: str = "bedrock"  # Options: bedrock, openai
    LLM_MODEL: str = "anthropic.claude-opus-5-sonnet-20241022-v2:0"
    LLM_TEMPERATURE: float = 0.7

    # LangChain Configuration (Legacy)
    OPENAI_API_KEY: Optional[str] = None

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
