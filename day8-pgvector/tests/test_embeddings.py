"""Unit tests for embedding generation."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from src.embeddings import generate_embedding


def test_generate_embedding_returns_768_dimensions(monkeypatch):
    """Verify that the Ollama response is converted into a 768-value vector."""
    expected_embedding = [0.1] * 768

    mock_client = MagicMock()
    mock_client.embed.return_value = SimpleNamespace(embeddings=[expected_embedding])

    monkeypatch.setattr(
        "src.embeddings.ollama.Client",
        lambda **kwargs: mock_client,
    )

    monkeypatch.setattr(
        "src.embeddings.get_settings",
        lambda: SimpleNamespace(
            ollama_host="http://ollama.test",
            ollama_model="test-embedding-model",
        ),
    )

    embedding = generate_embedding("Annual leave policy")

    assert len(embedding) == 768
    assert all(isinstance(value, float) for value in embedding)

    mock_client.embed.assert_called_once_with(
        model="test-embedding-model",
        input="Annual leave policy",
    )


def test_generate_embedding_rejects_empty_text():
    """Verify that empty text is rejected without contacting Ollama."""
    with pytest.raises(ValueError, match="Text cannot be empty"):
        generate_embedding("   ")
