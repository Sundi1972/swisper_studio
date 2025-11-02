"""Application configuration using Pydantic Settings"""

from typing import Any
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project
    PROJECT_NAME: str = "SwisperStudio"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: PostgresDsn

    # ClickHouse (optional for MVP)
    CLICKHOUSE_URL: str = "http://localhost:8123"
    CLICKHOUSE_DB: str = "swisper_studio_analytics"
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""

    # Security
    SECRET_KEY: str
    API_KEY: str  # Simple API key for MVP (will enhance with user-specific keys later)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str] | str:
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic"""
        return str(self.DATABASE_URL).replace("+asyncpg", "")


# Global settings instance
settings = Settings()
