"""Integration tests for PostgreSQL vector retrieval."""

import pytest
from src.retrieval import search_similar


def test_retrieval_returns_relevant_chunks() -> None:
    """Verify that a valid tenant can retrieve policy chunks."""
    results = search_similar(
        question="What are the annual leave eligibility requirements?",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
    )

    assert results
    assert all("content" in result for result in results)
    assert all("source" in result for result in results)
    assert all("distance" in result for result in results)


def test_retrieval_respects_result_limit() -> None:
    """Verify that retrieval respects the requested result limit."""
    results = search_similar(
        question="What are the annual leave eligibility requirements?",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
        limit=2,
    )

    assert len(results) <= 2


def test_other_tenant_cannot_access_unshared_documents() -> None:
    """Verify that an unrelated tenant cannot retrieve tenant_a documents."""
    results = search_similar(
        question="What are the annual leave eligibility requirements?",
        tenant_id="tenant_b",
        user_roles=["HR", "Employee"],
    )

    assert results == []


def test_missing_required_role_denies_access() -> None:
    """Verify that a user missing a required role gets no results."""
    results = search_similar(
        question="What are the annual leave eligibility requirements?",
        tenant_id="tenant_a",
        user_roles=["HR"],
    )

    assert results == []


@pytest.mark.parametrize("limit", [0, 21])
def test_retrieval_rejects_invalid_limit(limit: int) -> None:
    """Verify that invalid retrieval limits are rejected."""
    with pytest.raises(ValueError, match="limit"):
        search_similar(
            question="Annual leave",
            tenant_id="tenant_a",
            user_roles=["HR", "Employee"],
            limit=limit,
        )


def test_retrieval_rejects_empty_question() -> None:
    """Verify that an empty question is rejected."""
    with pytest.raises(ValueError, match="Question"):
        search_similar(
            question=" ",
            tenant_id="tenant_a",
            user_roles=["HR", "Employee"],
        )


def test_cross_tenant_sharing_requires_explicit_permission() -> None:
    """Allow explicitly shared documents but enforce their required roles."""
    from src.database import get_connection
    from src.embeddings import generate_embedding

    content = (
        "SHARING TEST: Employees can request a special remote work allowance "
        "after receiving HR approval."
    )
    source = "SHARING_TEST_ONLY.txt"
    embedding = generate_embedding(content)

    try:
        # Create a document owned by tenant_a and explicitly shared with tenant_b.
        with get_connection() as connection:
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
                    content,
                    embedding,
                    ["HR"],
                    ["tenant_b"],
                    source,
                ),
            )

        # tenant_b should retrieve the document because sharing is explicit.
        shared_results = search_similar(
            question="What special remote work allowance can employees request?",
            tenant_id="tenant_b",
            user_roles=["HR"],
            limit=20,
        )

        assert any(result["source"] == source for result in shared_results)

        # Sharing does not override the document's role restriction.
        restricted_results = search_similar(
            question="What special remote work allowance can employees request?",
            tenant_id="tenant_b",
            user_roles=["Employee"],
            limit=20,
        )

        assert all(result["source"] != source for result in restricted_results)

    finally:
        # Remove only our temporary test document.
        with get_connection() as connection:
            connection.execute(
                """
                DELETE FROM document_chunks
                WHERE tenant_id = %s AND source = %s
                """,
                ("tenant_a", source),
            )
