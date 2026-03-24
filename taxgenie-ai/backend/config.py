"""
TaxGenie AI - Configuration Settings
Loads all settings from environment variables with defaults for development.
"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # App
    APP_ENV: Literal["development", "production"] = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "pdf"

    # LLM API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # LLM Models
    PDF_PARSER_MODEL: str = "gpt-4o"
    DEDUCTION_FINDER_MODEL: str = "claude-3-5-sonnet-20241022"
    REGIME_ADVISOR_MODEL: str = "gpt-4o"
    INVESTMENT_MODEL: str = "gpt-4o"
    EXPLAINER_MODEL: str = "claude-3-5-sonnet-20241022"
    CHAT_MODEL: str = "claude-3-5-sonnet-20241022"

    # Vector DB
    VECTOR_DB_TYPE: str = "chromadb"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "taxgenie-knowledge"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_SESSION_TTL: int = 86400

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Rate Limiting
    MAX_REQUESTS_PER_HOUR: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
