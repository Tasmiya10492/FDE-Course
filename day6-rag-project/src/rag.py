import ollama

from src.embeddings import generate_embedding
from src.vector_store import search_chunks


LLM_MODEL = "qwen3.5:2b"


def retrieve_context(
    question: str,
    method: str = "fixed",
    top_k: int = 3,
) -> list[dict]:
    """
    Retrieve the most relevant policy chunks for a question.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    collection_name = f"hr_{method}_chunks"

    question_embedding = generate_embedding(question)

    matches = search_chunks(
        collection_name=collection_name,
        query_embedding=question_embedding,
        top_k=top_k,
    )

    return matches


def format_context(matches: list[dict]) -> str:
    """
    Format retrieved chunks for the LLM.
    """

    if not matches:
        return "No relevant policy content was retrieved."

    context_parts = []

    for match in matches:
        policy_id = match["metadata"]["policy_id"]

        context_parts.append(f"Policy ID: {policy_id}\nContent: {match['document']}")

    return "\n\n".join(context_parts)


def answer_question(
    question: str,
    method: str = "fixed",
    top_k: int = 3,
) -> dict:
    """
    Retrieve policy information and generate an answer.
    """

    matches = retrieve_context(
        question=question,
        method=method,
        top_k=top_k,
    )

    context = format_context(matches)

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an HR policy assistant. "
                    "Answer using only the supplied policy context. "
                    "Do not invent policy rules, dates or entitlements. "
                    "If the answer is not available in the context, "
                    "clearly say that the information is not available "
                    "and advise the employee to contact HR."
                ),
            },
            {
                "role": "user",
                "content": (f"Policy context:\n{context}\n\nQuestion: {question}"),
            },
        ],
    )

    return {
        "question": question,
        "answer": response.message.content,
        "retrieved_chunks": matches,
    }
