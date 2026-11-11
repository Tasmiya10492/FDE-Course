"""Generate text embeddings using Ollama."""

import ollama

from src.config import get_settings


def generate_embedding(text: str) -> list[float]:
    """Generate a 768-dimensional embedding for the supplied text."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    settings = get_settings()
    model = settings.ollama_model
    host = settings.ollama_host

    client = ollama.Client(host=host)

    response = client.embed(
        model=model,
        input=text,
    )

    embedding = list(response.embeddings[0])

    if len(embedding) != 768:
        raise ValueError(f"Expected 768 dimensions, received {len(embedding)}")

    return embedding
