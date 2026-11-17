"""Read HR policy documents, create chunks, and store them in PostgreSQL."""

from collections.abc import Callable
from pathlib import Path

from src.database import get_connection
from src.embeddings import generate_embedding


def _split_long_paragraph(
    paragraph: str,
    max_chars: int,
) -> tuple[list[str], str]:
    """Split a long paragraph into completed chunks and a remaining chunk."""
    completed: list[str] = []
    current = ""

    for word in paragraph.split():
        parts = [word[index : index + max_chars] for index in range(0, len(word), max_chars)]

        for part in parts:
            if not current:
                current = part
            elif len(current) + 1 + len(part) <= max_chars:
                current += " " + part
            else:
                completed.append(current)
                current = part

    return completed, current


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    """Split text into paragraph-aware chunks."""
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero")

    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]

    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            completed, current_chunk = _split_long_paragraph(
                paragraph,
                max_chars,
            )
            chunks.extend(completed)
            continue

        candidate = f"{current_chunk}\n\n{paragraph}".strip()

        if current_chunk and len(candidate) > max_chars:
            chunks.append(current_chunk)
            current_chunk = paragraph
        else:
            current_chunk = candidate

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def paragraph_chunks(text: str) -> list[str]:
    """Split text into non-empty paragraphs, matching the Day 6 method."""
    return [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]


def _get_chunker(chunking_method: str) -> Callable[[str], list[str]]:
    """Select the requested chunking method."""
    if chunking_method == "limited":
        return chunk_text

    if chunking_method == "paragraph":
        return paragraph_chunks

    raise ValueError("chunking_method must be 'limited' or 'paragraph'")


def _validate_ingestion_metadata(
    tenant_id: str,
    allowed_roles: list[str],
    shared_tenants: list[str],
) -> None:
    """Validate tenant, role, and sharing metadata."""
    if not tenant_id.strip():
        raise ValueError("tenant_id cannot be empty")

    if not allowed_roles or any(not role.strip() for role in allowed_roles):
        raise ValueError("At least one valid allowed role is required")

    if any(not tenant.strip() for tenant in shared_tenants):
        raise ValueError("Shared tenant IDs cannot be empty")

    if tenant_id in shared_tenants:
        raise ValueError("A tenant cannot share a document with itself")


def _get_source_files(directory: Path) -> list[Path]:
    """Find the text documents to ingest."""
    if not directory.is_dir():
        raise ValueError(f"Directory does not exist: {directory}")

    files = sorted(directory.glob("*.txt"))

    if not files:
        raise ValueError(f"No text documents found in {directory}")

    return files


def _replace_source_chunks(
    tenant_id: str,
    source: str,
    chunks: list[str],
    allowed_roles: list[str],
    shared_tenants: list[str],
) -> int:
    """Replace one source's chunks in a single database transaction."""
    prepared_chunks = [(chunk, generate_embedding(chunk)) for chunk in chunks]

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM document_chunks
            WHERE tenant_id = %s AND source = %s
            """,
            (tenant_id, source),
        )

        for chunk, embedding in prepared_chunks:
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
                    tenant_id,
                    chunk,
                    embedding,
                    allowed_roles,
                    shared_tenants,
                    source,
                ),
            )

    return len(prepared_chunks)


def ingest_directory(
    directory: str | Path,
    tenant_id: str,
    allowed_roles: list[str],
    shared_with_tenants: list[str] | None = None,
    chunking_method: str = "limited",
) -> int:
    """Ingest text documents without creating duplicate chunks."""
    directory_path = Path(directory)
    shared_tenants = shared_with_tenants or []

    chunker = _get_chunker(chunking_method)

    _validate_ingestion_metadata(
        tenant_id,
        allowed_roles,
        shared_tenants,
    )

    files = _get_source_files(directory_path)
    inserted_count = 0

    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        chunks = chunker(text)

        inserted_count += _replace_source_chunks(
            tenant_id,
            file_path.name,
            chunks,
            allowed_roles,
            shared_tenants,
        )

    return inserted_count
