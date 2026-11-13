"""Small in-memory stores for conversations and per-user memory."""

from collections import defaultdict

# Conversation history is isolated by (user_id, thread_id).
CONVERSATIONS: dict[tuple[str, str], list[dict]] = defaultdict(list)

# User memory is isolated by user_id, not by thread.
USER_MEMORY: dict[str, list[str]] = defaultdict(list)


def get_conversation(user_id: str, thread_id: str) -> list[dict]:
    return list(CONVERSATIONS[(user_id, thread_id)])


def save_conversation(
    user_id: str,
    thread_id: str,
    messages: list[dict],
) -> None:
    CONVERSATIONS[(user_id, thread_id)] = list(messages)


def get_user_memory(user_id: str) -> list[str]:
    return list(USER_MEMORY[user_id])


def remember_for_user(user_id: str, fact: str) -> None:
    if fact.strip():
        USER_MEMORY[user_id].append(fact.strip())
