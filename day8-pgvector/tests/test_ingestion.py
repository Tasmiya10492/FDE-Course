"""Tests for document chunking and ingestion validation."""

import pytest
from src.ingestion import chunk_text, ingest_directory


def test_chunk_text_splits_long_text() -> None:
    """Verify that long text is divided into smaller chunks."""
    text = "A" * 600

    chunks = chunk_text(text, max_chars=500)

    assert len(chunks) == 2
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_chunk_text_preserves_all_content() -> None:
    """Verify that chunking does not lose words."""
    text = "Annual leave policy.\n\nEmployees can apply for leave."

    chunks = chunk_text(text)

    assert len(chunks) == 1
    assert "Annual leave policy." in chunks[0]
    assert "Employees can apply for leave." in chunks[0]


def test_chunk_text_rejects_invalid_size() -> None:
    """Verify that invalid chunk sizes are rejected."""
    with pytest.raises(ValueError, match="max_chars"):
        chunk_text("Some policy text", max_chars=0)


def test_ingestion_rejects_empty_roles(tmp_path) -> None:
    """Verify that ingestion requires access roles."""
    with pytest.raises(ValueError, match="allowed role"):
        ingest_directory(
            tmp_path,
            tenant_id="tenant_a",
            allowed_roles=[],
        )


def test_ingestion_rejects_empty_tenant(tmp_path) -> None:
    """Verify that ingestion requires a tenant ID."""
    with pytest.raises(ValueError, match="tenant_id"):
        ingest_directory(
            tmp_path,
            tenant_id=" ",
            allowed_roles=["HR"],
        )


def test_ingestion_rejects_self_sharing(tmp_path) -> None:
    """Verify that a tenant cannot share with itself."""
    with pytest.raises(ValueError, match=r"share.*itself"):
        ingest_directory(
            tmp_path,
            tenant_id="tenant_a",
            allowed_roles=["HR"],
            shared_with_tenants=["tenant_a"],
        )


def test_ingestion_is_idempotent(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that ingesting the same document twice creates no duplicates."""
    from src.database import get_connection
    from src.ingestion import ingest_directory

    tenant_id = "tenant_ingestion_test"
    source = "idempotency_test_policy.txt"

    # Create a small temporary policy document.
    policy_file = tmp_path / source
    policy_file.write_text(
        "Employees can apply for annual leave through the HR portal.",
        encoding="utf-8",
    )

    # Use a test embedding so this test does not need to call Ollama.
    monkeypatch.setattr(
        "src.ingestion.generate_embedding",
        lambda text: [0.0] * 768,
    )

    try:
        with get_connection() as connection:
            connection.execute(
                """
                DELETE FROM document_chunks
                WHERE tenant_id = %s AND source = %s
                """,
                (tenant_id, source),
            )

        first_count = ingest_directory(
            tmp_path,
            tenant_id=tenant_id,
            allowed_roles=["HR"],
        )

        second_count = ingest_directory(
            tmp_path,
            tenant_id=tenant_id,
            allowed_roles=["HR"],
        )

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM document_chunks
                WHERE tenant_id = %s AND source = %s
                """,
                (tenant_id, source),
            ).fetchone()

        assert first_count == 1
        assert second_count == 1
        assert row is not None
        assert row[0] == 1

    finally:
        with get_connection() as connection:
            connection.execute(
                """
                DELETE FROM document_chunks
                WHERE tenant_id = %s AND source = %s
                """,
                (tenant_id, source),
            )


def test_paragraph_chunks_matches_day6_method():
    from src.ingestion import paragraph_chunks

    text = "First paragraph.\n\nSecond paragraph.\n\n\nThird paragraph."

    assert paragraph_chunks(text) == [
        "First paragraph.",
        "Second paragraph.",
        "Third paragraph.",
    ]
