"""Application configuration managed through Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate the .env file in the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Load and validate application settings."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required: application cannot start without a database connection.
    database_url: str

    # Optional settings with sensible defaults.
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "nomic-embed-text:latest"
    ollama_chat_model: str = "qwen3.5:2b"

    # Controls whether interactive API documentation is enabled.
    environment: Literal["development", "test", "production"] = "development"

    @property
    def docs_enabled(self) -> bool:
        """Enable interactive API documentation only in development."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()
