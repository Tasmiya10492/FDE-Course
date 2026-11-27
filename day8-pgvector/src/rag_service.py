"""Day 9 RAG service with citations, abstention and context budgeting."""

import ollama

from src.config import get_settings
from src.retrieval import search_similar

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
    relevant_chunks = [result for result in results if float(result["distance"]) <= MAX_DISTANCE]

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
    settings = get_settings()
    model = settings.ollama_chat_model
    host = settings.ollama_host

    client = ollama.Client(host=host)

    # Step 7: Generate an evidence-based answer.
    response = client.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an HR policy assistant. "
                    "Use only the supplied policy passages as evidence. "
                    "Answer the specific question directly and concisely. "
                    "Never invent numbers, dates, eligibility rules, exceptions, or entitlements. "
                    "When a question asks for a specific amount or figure that is not stated, "
                    "do not refuse the entire question if related policy information "
                    "is available. "
                    "Instead, explain the related information that the passages do establish, "
                    "and clearly state that the requested specific figure is not specified. "
                    "For annual leave entitlement questions, explain that entitlement is based "
                    "on employment terms and company policy, and may vary by employee grade, "
                    "contract type, and length of service, if those facts appear in the passages. "
                    "Do not assume that all full-time employees receive the same number of days. "
                    "Do not include unrelated leave types or policy topics. "
                    "Recommend contacting HR when the passages direct employees to do so. "
                    "If none of the supplied passages provides useful information, say: "
                    "'I don't know based on the available HR policy information.' "
                    "Never append the abstention message after providing a useful partial answer. "
                    "Do not cite passages that do not support the claim."
                ),
            },
            {
                "role": "user",
                "content": (f"Policy passages:\n{context}\n\nQuestion: {question}"),
            },
        ],
        think=False,
        options={
            "temperature": 0,
            "num_predict": 256,
            "num_ctx": 4096,
        },
    )

    answer = (response.message.content or "").strip()

    # Remove a redundant abstention sentence if useful information was provided.
    abstention_text = ABSTENTION_MESSAGE
    abstention_start = answer.casefold().find(abstention_text.casefold())

    if abstention_start >= 0:
        answer = (
            answer[:abstention_start] + answer[abstention_start + len(abstention_text) :]
        ).strip()

    # Step 8: Abstain if the model does not return an answer.
    if not answer:
        return {
            "answer": ABSTENTION_MESSAGE,
            "citations": [],
        }

    # Step 9: Abstain only when the entire answer is an abstention.
    if answer.casefold().strip() == ABSTENTION_MESSAGE.casefold():
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
