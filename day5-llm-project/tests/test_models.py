from llm_client.models import LLMResponse, TokenUsage


def test_llm_response_with_token_usage():
    response = LLMResponse(
        content="Hello Day 5",
        model="qwen3.5:2b",
        usage=TokenUsage(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        ),
        finish_reason="stop",
    )

    assert response.content == "Hello Day 5"
    assert response.model == "qwen3.5:2b"
    assert response.usage.total_tokens == 15


def test_llm_response_without_token_usage():
    response = LLMResponse(
        content="Hello",
        model="qwen3.5:2b",
    )

    assert response.usage is None
