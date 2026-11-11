"""Tests for application configuration."""

import pytest
from pydantic import ValidationError
from src.config import Settings


def test_database_url_is_required(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError, match="database_url"):
        Settings(_env_file=None)


def test_default_settings(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5433/testdb",
    )

    settings = Settings(_env_file=None)

    assert settings.ollama_host == "http://localhost:11434"
    assert settings.ollama_model == "nomic-embed-text:latest"
    assert settings.ollama_chat_model == "qwen3.5:2b"
    assert settings.environment == "development"
    assert settings.docs_enabled is True


def test_production_disables_api_docs(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5433/testdb",
    )
    monkeypatch.setenv("ENVIRONMENT", "production")

    settings = Settings(_env_file=None)

    assert settings.docs_enabled is False


def test_custom_ollama_settings(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5433/testdb",
    )
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    monkeypatch.setenv("OLLAMA_CHAT_MODEL", "custom-model")
    monkeypatch.setenv("ENVIRONMENT", "test")

    settings = Settings(_env_file=None)

    assert settings.ollama_host == "http://127.0.0.1:11434"
    assert settings.ollama_chat_model == "custom-model"
    assert settings.environment == "test"
    assert settings.docs_enabled is False
