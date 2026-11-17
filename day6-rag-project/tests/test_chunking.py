import pytest

from src.chunking import (
    fixed_size_chunks,
    sentence_chunks,
    paragraph_chunks,
)


def test_fixed_size_chunks_returns_chunks():
    text = "A" * 150

    chunks = fixed_size_chunks(text, chunk_size=50, overlap=10)

    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)


def test_fixed_size_chunks_has_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunks = fixed_size_chunks(text, chunk_size=10, overlap=3)

    assert chunks[0][-3:] == chunks[1][:3]


def test_fixed_size_chunks_rejects_invalid_size():
    with pytest.raises(ValueError):
        fixed_size_chunks("Hello world", chunk_size=0)


def test_fixed_size_chunks_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        fixed_size_chunks("Hello world", chunk_size=10, overlap=10)


def test_sentence_chunks_preserves_complete_sentences():
    text = "Employees can apply for leave. Managers review the request."

    chunks = sentence_chunks(text, chunk_size=100)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_sentence_chunks_splits_when_size_is_exceeded():
    text = "Employees can apply for leave. Managers review the request."

    chunks = sentence_chunks(text, chunk_size=35)

    assert len(chunks) == 2


def test_sentence_chunks_keeps_long_sentence_intact():
    text = "Employees must submit their annual leave requests through the official HR portal."

    chunks = sentence_chunks(text, chunk_size=20)

    assert chunks == [text]


def test_paragraph_chunks_splits_paragraphs():
    text = (
        "Employees can apply for leave.\n\n"
        "Managers review the request.\n\n"
        "HR handles policy questions."
    )

    chunks = paragraph_chunks(text)

    assert len(chunks) == 3


def test_paragraph_chunks_handles_empty_text():
    assert paragraph_chunks("") == []


def test_paragraph_chunks_removes_extra_whitespace():
    text = "  First paragraph.  \n\n  Second paragraph.  "

    chunks = paragraph_chunks(text)

    assert chunks == [
        "First paragraph.",
        "Second paragraph.",
    ]
