"""Generate answers using retrieved HR policy documents."""

import os

import ollama
from dotenv import load_dotenv

from src.retrieval import search_similar

load_dotenv()


def answer_question(
    question: str,
    tenant_id: str,
    user_roles: list[str],
    limit: int = 5,
) -> str:
    """Answer a question using only the documents the user can access."""
    results = search_similar(
        question=question,
        tenant_id=tenant_id,
        user_roles=user_roles,
        limit=limit,
    )

    if not results:
        return "I could not find relevant information in the policies you can access."

    context = "\n\n".join(f"Source: {result['source']}\n{result['content']}" for result in results)

    model = os.getenv("OLLAMA_CHAT_MODEL", "qwen3.5:2b")
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    client = ollama.Client(host=host)

    response = client.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an HR policy assistant. "
                    "Answer the user's question using only the supplied policy context. "
                    "Do not invent rules, dates, eligibility criteria, or benefits. "
                    "If the context does not contain the answer, clearly say so. "
                    "Mention the source filename when useful."
                ),
            },
            {
                "role": "user",
                "content": (f"Policy context:\n{context}\n\nQuestion: {question}"),
            },
        ],
        options={"temperature": 0},
    )

    answer = (response.message.content or "").strip()

    if not answer:
        return "I could not generate an answer from the available policy information."

    return answer
