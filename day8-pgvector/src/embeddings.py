"""Generate text embeddings using Ollama."""

import os

import ollama
from dotenv import load_dotenv

load_dotenv()


def generate_embedding(text: str) -> list[float]:
    """Generate a 768-dimensional embedding for the supplied text."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    model = os.getenv("OLLAMA_MODEL", "nomic-embed-text:latest")
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    client = ollama.Client(host=host)

    response = client.embed(
        model=model,
        input=text,
    )

    embedding = list(response.embeddings[0])

    if len(embedding) != 768:
        raise ValueError(f"Expected 768 dimensions, received {len(embedding)}")

    return embedding
