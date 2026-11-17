"""Retrieve relevant document chunks using PostgreSQL pgvector."""

from src.access_control import validate_access_context
from src.database import get_connection
from src.embeddings import generate_embedding


def search_similar(
    question: str,
    tenant_id: str,
    user_roles: list[str],
    limit: int = 5,
) -> list[dict[str, str | int | float]]:
    """Search for relevant chunks while enforcing access permissions."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    validate_access_context(tenant_id, user_roles)

    if limit < 1 or limit > 20:
        raise ValueError("limit must be between 1 and 20")

    query_embedding = generate_embedding(question)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                content,
                source,
                embedding <=> %s::vector AS distance
            FROM document_chunks
            WHERE
                (
                    tenant_id = %s
                    OR %s = ANY(shared_with_tenants)
                )
                AND allowed_roles <@ %s::text[]
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (
                query_embedding,
                tenant_id,
                tenant_id,
                user_roles,
                query_embedding,
                limit,
            ),
        ).fetchall()

    return [
        {
            "id": row[0],
            "content": row[1],
            "source": row[2],
            "distance": float(row[3]),
        }
        for row in rows
    ]
