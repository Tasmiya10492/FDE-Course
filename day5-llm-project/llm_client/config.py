from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="LLM_",
        extra="ignore",
    )

    provider: Literal["ollama", "openrouter", "groq"] = "ollama"
    base_url: str = "http://localhost:11434/v1"
    api_key: str = "ollama"
    model: str = "qwen3.5:2b"

    timeout: float = Field(default=60, gt=0)
    max_retries: int = Field(default=2, ge=0)
    fallback_models: str = ""

    @property
    def fallback_model_list(self) -> list[str]:
        return [
            name.strip() for name in self.fallback_models.split(",") if name.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
