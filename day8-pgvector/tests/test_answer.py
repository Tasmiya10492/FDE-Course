"""Integration tests for RAG answer generation."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from src.answer import answer_question


def test_answer_question_returns_an_answer(retrieval_test_data, monkeypatch) -> None:
    """Verify that the RAG system generates an answer from policy documents."""
    mock_client = Mock()
    mock_client.chat.return_value = SimpleNamespace(
        message=SimpleNamespace(
            content="Employees can apply for annual leave after completing the eligibility period."
        )
    )

    monkeypatch.setattr(
        "src.answer.ollama.Client",
        lambda host: mock_client,
    )

    answer = answer_question(
        question="What are the annual leave eligibility requirements?",
        tenant_id="tenant_a",
        user_roles=["HR", "Employee"],
    )

    assert isinstance(answer, str)
    assert answer.strip()
    mock_client.chat.assert_called_once()


def test_answer_question_denies_unshared_tenant(retrieval_test_data) -> None:
    """Verify that an unauthorized tenant does not receive policy information."""
    answer = answer_question(
        question="What are the annual leave eligibility requirements?",
        tenant_id="tenant_b",
        user_roles=["HR", "Employee"],
    )

    assert answer == ("I could not find relevant information in the policies you can access.")


def test_answer_question_rejects_empty_question() -> None:
    """Verify that an empty question is rejected."""
    with pytest.raises(ValueError, match="Question"):
        answer_question(
            question=" ",
            tenant_id="tenant_a",
            user_roles=["HR", "Employee"],
        )
