"""Shared pytest fixtures for isolated database tests."""

import pytest
from src.database import get_connection


@pytest.fixture
def retrieval_test_data(monkeypatch):
    """Provide deterministic embeddings and one isolated retrieval document."""
    embedding = [1.0] + [0.0] * 767
    source = "CI_RETRIEVAL_FIXTURE.txt"

    # Retrieval uses this predictable vector instead of contacting Ollama.
    monkeypatch.setattr(
        "src.retrieval.generate_embedding",
        lambda text: embedding,
    )

    # The cross-tenant sharing test imports this function directly.
    monkeypatch.setattr(
        "src.embeddings.generate_embedding",
        lambda text: embedding,
    )

    # Remove any stale copy of this fixture before inserting it.
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM document_chunks
            WHERE tenant_id = %s AND source = %s
            """,
            ("tenant_a", source),
        )

        connection.execute(
            """
            INSERT INTO document_chunks (
                tenant_id,
                content,
                embedding,
                allowed_roles,
                shared_with_tenants,
                source
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                "tenant_a",
                "Employees can apply for annual leave after completing the eligibility period.",
                embedding,
                ["HR", "Employee"],
                [],
                source,
            ),
        )

    yield

    # Remove only the fixture document, never the user's policy data.
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM document_chunks
            WHERE tenant_id = %s AND source = %s
            """,
            ("tenant_a", source),
        )
