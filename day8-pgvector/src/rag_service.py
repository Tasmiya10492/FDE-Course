"""Day 9 RAG service with citations, abstention and context budgeting."""

import os

import ollama
from dotenv import load_dotenv

from src.retrieval import search_similar

load_dotenv()

MAX_DISTANCE = 0.40
DEFAULT_CONTEXT_TOKENS = 2000

ABSTENTION_MESSAGE = "I don't know based on the available HR policy information."


def _estimate_tokens(text: str) -> int:
    """Estimate token count using approximately four characters per token."""
    return (len(text) + 3) // 4


def _select_chunks_within_budget(
    chunks: list[dict],
    max_context_tokens: int = DEFAULT_CONTEXT_TOKENS,
) -> list[dict]:
    """Select the highest-ranked chunks that fit within the context budget."""

    if max_context_tokens < 1:
        raise ValueError("Context token budget must be positive")

    selected = []
    used_tokens = 0

    for chunk in chunks:
        chunk_text = f"[Source: {chunk['source']}, Chunk ID: {chunk['id']}]\n{chunk['content']}"

        chunk_tokens = _estimate_tokens(chunk_text)

        if used_tokens + chunk_tokens <= max_context_tokens:
            selected.append(chunk)
            used_tokens += chunk_tokens

    return selected


def ask(
    question: str,
    tenant_id: str,
    user_roles: list[str],
    limit: int = 5,
    max_context_tokens: int = DEFAULT_CONTEXT_TOKENS,
) -> dict:
    """Retrieve policy evidence and generate an answer with citations."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    # Step 1: Retrieve chunks while enforcing tenant and role permissions.
    results = search_similar(
        question=question,
        tenant_id=tenant_id,
        user_roles=user_roles,
        limit=limit,
    )

    # Step 2: Remove chunks whose similarity distance is too high.
    relevant_chunks = [result for result in results if result["distance"] <= MAX_DISTANCE]

    # Step 3: Keep only chunks that fit within the context budget.
    relevant_chunks = _select_chunks_within_budget(
        relevant_chunks,
        max_context_tokens=max_context_tokens,
    )

    # Step 4: Abstain when no usable evidence remains.
    if not relevant_chunks:
        return {
            "answer": ABSTENTION_MESSAGE,
            "citations": [],
        }

    # Step 5: Assemble context with source and chunk identifiers.
    context = "\n\n".join(
        f"[Source: {chunk['source']}, Chunk ID: {chunk['id']}]\n{chunk['content']}"
        for chunk in relevant_chunks
    )

    # Step 6: Configure the local Ollama model.
    model = os.getenv("OLLAMA_CHAT_MODEL", "qwen3.5:2b")
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    client = ollama.Client(host=host)

    # Step 7: Generate an evidence-based answer.
    response = client.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an HR policy assistant. "
                    "Answer only using the supplied policy passages. "
                    "Do not invent policies, dates or eligibility rules. "
                    "If the passages do not answer the question, "
                    "say that you don't know. "
                    "Cite supporting sources using their filename and chunk ID."
                ),
            },
            {
                "role": "user",
                "content": (f"Policy passages:\n{context}\n\nQuestion: {question}"),
            },
        ],
        options={"temperature": 0},
    )

    answer = (response.message.content or "").strip()

    # Step 8: Abstain if the model does not return an answer.
    if not answer:
        return {
            "answer": ABSTENTION_MESSAGE,
            "citations": [],
        }

    # Step 9: Abstain if the model explicitly says it does not know.
    normalized_answer = answer.casefold()

    if "i don't know" in normalized_answer or "i do not know" in normalized_answer:
        return {
            "answer": ABSTENTION_MESSAGE,
            "citations": [],
        }

    # Step 10: Return the answer and the exact passages supplied as evidence.
    citations = [
        {
            "chunk_id": chunk["id"],
            "source": chunk["source"],
            "passage": chunk["content"],
        }
        for chunk in relevant_chunks
    ]

    return {
        "answer": answer,
        "citations": citations,
    }
