class LLMError(Exception):
    """Base exception for LLM client errors."""


class LLMAPIError(LLMError):
    """Raised when an LLM API returns an unsuccessful response."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class LLMConnectionError(LLMError):
    """Raised when the LLM API cannot be reached."""
