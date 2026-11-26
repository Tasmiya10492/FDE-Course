"""FastAPI endpoints for the LangGraph agent service."""

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent_graph import build_graph, resume, start
from llm import ChatModel, OpenAICompatibleChat

app = FastAPI(title="LangGraph agent service")

_graph = None
_active_threads: set[str] = set()


class ChatRequest(BaseModel):
    """A new user question."""

    question: str = Field(min_length=1, max_length=2000)


class ApprovalRequest(BaseModel):
    """A human decision for a pending tool action."""

    thread_id: str = Field(min_length=1)
    approved: bool


def get_model() -> ChatModel:
    """Create the real model client from the environment."""
    return OpenAICompatibleChat()


def get_graph():
    """Build the graph once and reuse it."""
    global _graph

    if _graph is None:
        _graph = build_graph(get_model())

    return _graph


@app.get("/health")
def health():
    """Report whether the agent API process is running."""
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    """Start a new conversation with the agent."""
    thread_id = str(uuid4())
    _active_threads.add(thread_id)

    try:
        result = start(
            get_graph(),
            question=request.question,
            thread_id=thread_id,
        )
    except Exception:
        _active_threads.discard(thread_id)
        raise

    return {
        "thread_id": thread_id,
        **result,
    }


@app.post("/approve")
def approve(request: ApprovalRequest):
    """Resume a conversation after a human approval decision."""
    if request.thread_id not in _active_threads:
        raise HTTPException(
            status_code=404,
            detail="Unknown or inactive conversation thread.",
        )

    result = resume(
        get_graph(),
        thread_id=request.thread_id,
        approved=request.approved,
    )

    return {
        "thread_id": request.thread_id,
        **result,
    }
