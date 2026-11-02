import httpx

from llm_client.client import LLMClient
from llm_client.config import Settings


def create_settings(**overrides):
    values = {
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "qwen3.5:2b",
        "timeout": 60,
        "max_retries": 0,
        "fallback_models": "",
    }
    values.update(overrides)
    return Settings(**values)


def successful_response(model="qwen3.5:2b"):
    return httpx.Response(
        200,
        json={
            "model": model,
            "choices": [
                {
                    "message": {"content": "Hello Day 5"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        },
        request=httpx.Request("POST", "http://localhost/v1/chat/completions"),
    )


def test_successful_llm_request(monkeypatch):
    def fake_post(*args, **kwargs):
        return successful_response()

    monkeypatch.setattr("llm_client.client.httpx.post", fake_post)

    client = LLMClient(create_settings())

    result = client.chat([{"role": "user", "content": "Say hello"}])

    assert result.content == "Hello Day 5"
    assert result.model == "qwen3.5:2b"
    assert result.usage.total_tokens == 15


def test_llm_retries_temporary_error(monkeypatch):
    responses = [
        httpx.Response(
            503,
            request=httpx.Request("POST", "http://localhost/v1/chat/completions"),
        ),
        successful_response(),
    ]

    calls = []

    def fake_post(*args, **kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr("llm_client.client.httpx.post", fake_post)
    monkeypatch.setattr("llm_client.client.time.sleep", lambda seconds: None)

    client = LLMClient(create_settings(max_retries=1))

    result = client.chat([{"role": "user", "content": "Say hello"}])

    assert result.content == "Hello Day 5"
    assert len(calls) == 2


def test_llm_uses_fallback_model(monkeypatch):
    requested_models = []

    def fake_post(*args, **kwargs):
        requested_models.append(kwargs["json"]["model"])

        if kwargs["json"]["model"] == "qwen3.5:2b":
            return httpx.Response(
                503,
                request=httpx.Request("POST", "http://localhost/v1/chat/completions"),
            )

        return successful_response("fallback-model")

    monkeypatch.setattr("llm_client.client.httpx.post", fake_post)

    settings = create_settings(fallback_models="fallback-model")

    client = LLMClient(settings)

    result = client.chat([{"role": "user", "content": "Say hello"}])

    assert requested_models == ["qwen3.5:2b", "fallback-model"]
    assert result.model == "fallback-model"
