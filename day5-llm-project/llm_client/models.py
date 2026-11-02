from pydantic import BaseModel


class TokenUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage | None = None
    finish_reason: str | None = None
