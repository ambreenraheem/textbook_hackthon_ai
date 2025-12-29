"""
Application configuration module.

Loads and validates environment variables using Pydantic settings.
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated on startup to ensure required values are present.
    """

    # OpenAI Configuration
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    # Qdrant Configuration
    qdrant_url: str = Field(..., alias="QDRANT_URL")
    qdrant_api_key: str = Field(..., alias="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(default="textbook_chunks", alias="QDRANT_COLLECTION_NAME")

    # Neon Postgres Configuration
    database_url: str = Field(..., alias="DATABASE_URL")

    # Application Settings
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    # Backend Server Configuration
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")

    # RAG Configuration
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1536, alias="EMBEDDING_DIMENSIONS")
    llm_model: str = Field(default="gpt-4-turbo-preview", alias="LLM_MODEL")
    max_tokens: int = Field(default=2000, alias="MAX_TOKENS")
    temperature: float = Field(default=0.7, alias="TEMPERATURE")

    # Retrieval Configuration
    retrieval_top_k: int = Field(default=20, alias="RETRIEVAL_TOP_K")
    rerank_top_n: int = Field(default=5, alias="RERANK_TOP_N")
    min_similarity_score: float = Field(default=0.6, alias="MIN_SIMILARITY_SCORE")

    # Chunking Configuration
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return ["http://localhost:3000"]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    class Config:
        case_sensitive = False
        extra = 'ignore'  # Ignore extra fields in .env


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.

    Returns:
        Settings: Application configuration settings
    """
    return settings
