"""Read HR policy documents, create chunks, and store them in PostgreSQL."""

from collections.abc import Callable
from datetime import date
from pathlib import Path

import yaml

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
            WHERE tenant_id = %s
            AND source = %s
            AND allowed_roles = %s
            AND shared_with_tenants = %s
            """,
            (tenant_id, source, allowed_roles, shared_tenants),
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

    # Normalize permission metadata so equivalent role sets match consistently.
    allowed_roles = sorted(set(allowed_roles))
    shared_tenants = sorted(set(shared_tenants))

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


def _read_markdown_frontmatter(
    file_path: Path,
) -> tuple[dict, list[str], int]:
    """Read and validate the YAML frontmatter structure."""
    lines = file_path.read_text(encoding="utf-8").splitlines()

    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Missing YAML frontmatter in {file_path.name}")

    try:
        closing_index = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(
            f"Closing YAML frontmatter delimiter missing in {file_path.name}"
        ) from error

    try:
        metadata = yaml.safe_load("\n".join(lines[1:closing_index]))
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML frontmatter in {file_path.name}") from error

    if not isinstance(metadata, dict):
        raise ValueError(f"Frontmatter must be a YAML mapping in {file_path.name}")

    return metadata, lines, closing_index


def _validate_markdown_required_fields(
    metadata: dict,
    file_path: Path,
) -> None:
    """Ensure all required document metadata fields are present."""
    required_fields = (
        "id",
        "title",
        "tenant",
        "type",
        "allowed_roles",
        "updated",
    )
    missing_fields = [field for field in required_fields if field not in metadata]

    if missing_fields:
        raise ValueError(
            f"Missing frontmatter fields in {file_path.name}: {', '.join(missing_fields)}"
        )


def _require_markdown_string(
    value: object,
    field_name: str,
    file_path: Path,
) -> str:
    """Validate a required non-empty string metadata field."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Frontmatter field '{field_name}' must be a non-empty string in {file_path.name}"
        )
    return value.strip()


def _parse_markdown_roles(value: object, file_path: Path) -> list[str]:
    """Validate the document's allowed roles."""
    if not isinstance(value, list) or not all(isinstance(role, str) for role in value):
        raise ValueError(f"allowed_roles must be a list of strings in {file_path.name}")
    return value


def _parse_markdown_date(value: object, file_path: Path) -> date:
    """Convert the document's updated metadata to a date."""
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"Invalid updated date in {file_path.name}") from error

    if not isinstance(value, date):
        raise ValueError(f"Frontmatter field 'updated' must be a date in {file_path.name}")
    return value


def _parse_markdown_document(
    file_path: Path,
) -> tuple[str, str, str, list[str], date, str, str]:
    """Read YAML frontmatter and return document metadata and body text."""
    metadata, lines, closing_index = _read_markdown_frontmatter(file_path)
    _validate_markdown_required_fields(metadata, file_path)

    document_id = str(metadata["id"]).strip()
    if not document_id:
        raise ValueError(f"Document ID cannot be empty in {file_path.name}")

    title = _require_markdown_string(metadata["title"], "title", file_path)
    tenant_id = _require_markdown_string(metadata["tenant"], "tenant", file_path)
    document_type = _require_markdown_string(metadata["type"], "type", file_path)
    allowed_roles = _parse_markdown_roles(metadata["allowed_roles"], file_path)
    updated = _parse_markdown_date(metadata["updated"], file_path)

    body = "\\n".join(lines[closing_index + 1 :]).strip()
    if not body:
        raise ValueError(f"Document body is empty in {file_path.name}")

    return (
        document_id,
        title,
        tenant_id,
        allowed_roles,
        updated,
        document_type,
        body,
    )


def _get_markdown_files(directory: Path) -> list[Path]:
    """Find Markdown documents to ingest."""
    if not directory.is_dir():
        raise ValueError(f"Directory does not exist: {directory}")

    files = sorted(directory.glob("*.md"))

    if not files:
        raise ValueError(f"No Markdown documents found in {directory}")

    return files


def _replace_markdown_document_chunks(
    tenant_id: str,
    document_id: str,
    title: str,
    document_type: str,
    document_updated_at: date,
    source: str,
    chunks: list[str],
    allowed_roles: list[str],
) -> int:
    """Replace all chunks for one Markdown document transactionally."""
    prepared_chunks = [(chunk, generate_embedding(chunk)) for chunk in chunks]

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM document_chunks
            WHERE tenant_id = %s
              AND document_id = %s
            """,
            (tenant_id, document_id),
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
                    source,
                    document_id,
                    title,
                    document_type,
                    document_updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    tenant_id,
                    chunk,
                    embedding,
                    allowed_roles,
                    [],
                    source,
                    document_id,
                    title,
                    document_type,
                    document_updated_at,
                ),
            )

    return len(prepared_chunks)


def ingest_markdown_directory(
    directory: str | Path,
    chunking_method: str = "limited",
) -> int:
    """Ingest Markdown documents using each document's YAML permissions."""
    directory_path = Path(directory)
    chunker = _get_chunker(chunking_method)
    files = _get_markdown_files(directory_path)

    inserted_count = 0

    for file_path in files:
        (
            document_id,
            title,
            tenant_id,
            allowed_roles,
            document_updated_at,
            document_type,
            body,
        ) = _parse_markdown_document(file_path)

        _validate_ingestion_metadata(
            tenant_id,
            allowed_roles,
            [],
        )

        allowed_roles = sorted({role.strip() for role in allowed_roles})

        if not allowed_roles:
            raise ValueError(f"At least one valid allowed role is required in {file_path.name}")

        if any(not role for role in allowed_roles):
            raise ValueError(f"Empty allowed role found in {file_path.name}")

        chunks = chunker(body)

        if not chunks:
            raise ValueError(f"No searchable text found in {file_path.name}")

        inserted_count += _replace_markdown_document_chunks(
            tenant_id=tenant_id,
            document_id=document_id,
            title=title,
            document_type=document_type,
            document_updated_at=document_updated_at,
            source=file_path.name,
            chunks=chunks,
            allowed_roles=allowed_roles,
        )

    return inserted_count
