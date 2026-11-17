"""Tests for the Day 9 RAG service."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from src.rag_service import _select_chunks_within_budget, ask


@pytest.fixture
def relevant_chunks():
    """Provide two relevant HR policy chunks."""
    return [
        {
            "id": 43,
            "content": "Employees who complete the eligibility period can apply for annual leave.",
            "source": "HR001.txt",
            "distance": 0.1843,
        },
        {
            "id": 44,
            "content": "Employees receive annual leave entitlement according to policy.",
            "source": "HR002.txt",
            "distance": 0.2421,
        },
    ]


def mock_ollama(monkeypatch, answer):
    """Replace the Ollama client with a predictable mock."""
    mock_client = MagicMock()
    mock_client.chat.return_value = SimpleNamespace(message=SimpleNamespace(content=answer))

    monkeypatch.setattr(
        "src.rag_service.ollama.Client",
        lambda **kwargs: mock_client,
    )

    return mock_client


def test_ask_returns_answer_and_citations(monkeypatch, relevant_chunks):
    """A supported question returns its answer and exact source passages."""
    monkeypatch.setattr(
        "src.rag_service.search_similar",
        lambda **kwargs: relevant_chunks[:1],
    )
    mock_client = mock_ollama(
        monkeypatch,
        "Eligible employees can apply for annual leave [HR001.txt, chunk 43].",
    )

    result = ask(
        question="What are the annual leave eligibility requirements?",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
    )

    assert result["answer"]
    assert len(result["citations"]) == 1
    assert result["citations"][0] == {
        "chunk_id": 43,
        "source": "HR001.txt",
        "passage": relevant_chunks[0]["content"],
    }
    mock_client.chat.assert_called_once()


def test_ask_returns_multiple_citations(monkeypatch, relevant_chunks):
    """Multiple relevant chunks should be available as citations."""
    monkeypatch.setattr(
        "src.rag_service.search_similar",
        lambda **kwargs: relevant_chunks,
    )
    mock_ollama(monkeypatch, "Employees can apply according to the policy.")

    result = ask(
        question="Explain annual leave.",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
    )

    assert len(result["citations"]) == 2
    assert [item["chunk_id"] for item in result["citations"]] == [43, 44]


def test_ask_abstains_when_chunks_are_irrelevant(monkeypatch):
    """Weak similarity matches should not be sent to the LLM."""
    monkeypatch.setattr(
        "src.rag_service.search_similar",
        lambda **kwargs: [
            {
                "id": 45,
                "content": "Employees must submit leave requests through the HR portal.",
                "source": "HR003.txt",
                "distance": 0.4994,
            }
        ],
    )
    mock_client = MagicMock()

    monkeypatch.setattr(
        "src.rag_service.ollama.Client",
        lambda **kwargs: mock_client,
    )

    result = ask(
        question="What is the Wi-Fi password?",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
    )

    assert "I don't know" in result["answer"]
    assert result["citations"] == []
    mock_client.chat.assert_not_called()


def test_ask_abstains_when_retrieval_returns_nothing(monkeypatch):
    """No retrieved chunks should produce an abstention."""
    monkeypatch.setattr(
        "src.rag_service.search_similar",
        lambda **kwargs: [],
    )
    mock_client = MagicMock()

    monkeypatch.setattr(
        "src.rag_service.ollama.Client",
        lambda **kwargs: mock_client,
    )

    result = ask(
        question="What is the leave policy?",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
    )

    assert "I don't know" in result["answer"]
    assert result["citations"] == []
    mock_client.chat.assert_not_called()


def test_ask_rejects_empty_question():
    """An empty question should be rejected."""
    with pytest.raises(ValueError, match="Question"):
        ask(
            question=" ",
            tenant_id="tenant_a",
            user_roles=["HR", "Employee"],
        )


def test_context_budget_limits_selected_chunks():
    """Only chunks that fit within the budget should be selected."""
    chunks = [
        {
            "id": 43,
            "content": "A" * 100,
            "source": "HR001.txt",
            "distance": 0.18,
        },
        {
            "id": 44,
            "content": "B" * 100,
            "source": "HR002.txt",
            "distance": 0.20,
        },
    ]

    selected = _select_chunks_within_budget(
        chunks,
        max_context_tokens=35,
    )

    assert len(selected) == 1
    assert selected[0]["id"] == 43


def test_context_budget_skips_oversized_chunk():
    """A chunk that cannot fit should not prevent a later chunk from fitting."""
    chunks = [
        {
            "id": 43,
            "content": "A" * 500,
            "source": "HR001.txt",
            "distance": 0.18,
        },
        {
            "id": 44,
            "content": "Short passage.",
            "source": "HR002.txt",
            "distance": 0.20,
        },
    ]

    selected = _select_chunks_within_budget(
        chunks,
        max_context_tokens=20,
    )

    assert len(selected) == 1
    assert selected[0]["id"] == 44


def test_context_budget_rejects_zero():
    """A zero context budget is invalid."""
    with pytest.raises(ValueError, match="budget"):
        _select_chunks_within_budget([], max_context_tokens=0)


def test_context_budget_rejects_negative_value():
    """A negative context budget is invalid."""
    with pytest.raises(ValueError, match="budget"):
        _select_chunks_within_budget([], max_context_tokens=-10)


def test_ask_uses_configured_context_budget(monkeypatch, relevant_chunks):
    """The caller can configure the maximum context size."""
    monkeypatch.setattr(
        "src.rag_service.search_similar",
        lambda **kwargs: relevant_chunks,
    )
    mock_client = mock_ollama(monkeypatch, "Annual leave is available.")

    ask(
        question="Explain annual leave.",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
        max_context_tokens=2000,
    )

    sent_context = mock_client.chat.call_args.kwargs["messages"][1]["content"]

    assert "HR001.txt" in sent_context
    assert "HR002.txt" in sent_context


def test_ask_abstains_when_model_returns_empty_answer(
    monkeypatch,
    relevant_chunks,
):
    """An empty model response should produce an abstention without citations."""
    monkeypatch.setattr(
        "src.rag_service.search_similar",
        lambda **kwargs: relevant_chunks[:1],
    )
    mock_ollama(monkeypatch, "   ")

    result = ask(
        question="Explain annual leave.",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
    )

    assert "I don't know" in result["answer"]
    assert result["citations"] == []


def test_ask_abstains_when_model_says_i_dont_know(
    monkeypatch,
    relevant_chunks,
):
    """An explicit model abstention must not return misleading citations."""
    monkeypatch.setattr(
        "src.rag_service.search_similar",
        lambda **kwargs: relevant_chunks,
    )
    mock_ollama(
        monkeypatch,
        "I don't know based on the available HR policy information.",
    )

    result = ask(
        question="What is the annual leave policy?",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
    )

    assert result["answer"] == ("I don't know based on the available HR policy information.")
    assert result["citations"] == []


def test_ask_only_cites_chunks_included_in_context_budget(
    monkeypatch,
    relevant_chunks,
):
    """Chunks excluded by the context budget must not appear as citations."""
    monkeypatch.setattr(
        "src.rag_service.search_similar",
        lambda **kwargs: [
            {
                **relevant_chunks[0],
                "content": "A" * 100,
            },
            {
                **relevant_chunks[1],
                "content": "B" * 100,
            },
        ],
    )
    mock_ollama(monkeypatch, "Annual leave is governed by HR policy.")

    result = ask(
        question="Explain annual leave.",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
        max_context_tokens=35,
    )

    assert [item["chunk_id"] for item in result["citations"]] == [43]
