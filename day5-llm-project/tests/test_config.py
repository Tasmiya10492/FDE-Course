from llm_client.config import get_settings


def test_load_settings():
    settings = get_settings()

    assert settings.provider == "ollama"
    assert settings.base_url == "http://localhost:11434/v1"
    assert settings.api_key == "ollama"
    assert settings.model == "qwen3.5:2b"
    assert settings.timeout == 180
    assert settings.max_retries == 2
    assert settings.fallback_model_list == []


def test_environment_variable_override(monkeypatch):
    get_settings.cache_clear()

    monkeypatch.setenv("LLM_MODEL", "test-model-from-env")

    settings = get_settings()

    assert settings.model == "test-model-from-env"

    get_settings.cache_clear()
