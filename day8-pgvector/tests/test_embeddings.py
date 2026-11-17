"""Tests for embedding generation."""

import pytest
from src.embeddings import generate_embedding


def test_generate_embedding_returns_768_dimensions() -> None:
    """Verify that Ollama generates a 768-dimensional vector."""
    embedding = generate_embedding("Annual leave policy")

    assert len(embedding) == 768
    assert all(isinstance(value, float) for value in embedding)


def test_generate_embedding_rejects_empty_text() -> None:
    """Verify that empty text is rejected."""
    with pytest.raises(ValueError, match="Text cannot be empty"):
        generate_embedding("   ")
