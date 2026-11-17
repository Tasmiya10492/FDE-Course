import ollama


# Local Ollama embedding model
EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(text: str) -> list[float]:
    """
    Convert text into a numerical embedding vector
    using the local Ollama embedding model.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    embedding = response.embeddings[0]

    return embedding
