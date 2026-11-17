import re


def fixed_size_chunks(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[str]:
    """Split text into fixed-size character chunks with overlap."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def sentence_chunks(
    text: str,
    chunk_size: int = 300,
) -> list[str]:
    """Group complete sentences without exceeding the target size,
    except when an individual sentence itself is longer.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if not sentence:
            continue

        if len(sentence) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            chunks.append(sentence)
            continue

        candidate = f"{current_chunk} {sentence}".strip()

        if len(candidate) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk = candidate

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def paragraph_chunks(text: str) -> list[str]:
    """Split text into chunks using blank lines as paragraph boundaries."""

    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]

    return paragraphs
