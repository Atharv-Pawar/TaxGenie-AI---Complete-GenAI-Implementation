"""
TaxGenie AI - Configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None
    PINECONE_API_KEY: Optional[str] = None
    
    # Model Configuration
    PRIMARY_MODEL: str = "gpt-4o"
    VISION_MODEL: str = "gpt-4o"  # GPT-4o has vision capabilities
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # Vector Store
    PINECONE_INDEX: str = "taxgenie-knowledge"
    PINECONE_ENVIRONMENT: str = "us-east-1"
    USE_LOCAL_VECTORSTORE: bool = True  # Use Chroma for dev
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # App Settings
    DEBUG: bool = True
    MAX_PDF_SIZE_MB: int = 10
    CACHE_TTL_SECONDS: int = 3600
    
    class Config:
        env_file = ".env"


settings = Settings()