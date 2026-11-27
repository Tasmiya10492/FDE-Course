"""Application configuration managed through Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

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
    # Secret used to sign browser session cookies.
    session_secret: str = ""

    # API keys for trusted machine-to-machine callers.
    employee_api_key: str = ""
    hr_api_key: str = ""

    # Explicit comma-separated origins allowed to call the API.
    # Empty means no cross-origin browser access is allowed.
    cors_allowed_origins: str = ""

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

    @property
    def cors_origins(self) -> list[str]:
        """Return validated, non-empty HTTP or HTTPS origins."""
        origins = []

        for value in self.cors_allowed_origins.split(","):
            origin = value.strip().rstrip("/")

            if not origin:
                continue

            parsed = urlsplit(origin)

            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path
                or parsed.query
                or parsed.fragment
                or "*" in origin
            ):
                raise ValueError(f"Invalid CORS origin: {origin}")

            try:
                _ = parsed.port
            except ValueError:
                raise ValueError(f"Invalid CORS origin: {origin}") from None

            origins.append(origin)

        return origins


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()  # pyright: ignore[reportCallIssue]
