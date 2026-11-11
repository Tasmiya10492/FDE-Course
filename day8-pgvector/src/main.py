"""FastAPI application for the HR policy RAG assistant."""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.config import get_settings
from src.database import check_connection
from src.rag_service import ask

request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default="startup",
)


class RequestIdFilter(logging.Filter):
    """Attach the current request ID to every log record."""

    def filter(self, record):
        record.request_id = request_id_context.get()
        return True


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "startup"),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
handler.addFilter(RequestIdFilter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    force=True,
)

logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="HR Policy RAG API",
    description="Ask questions about HR policies with permission-filtered citations.",
    version="1.0.0",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Assign a request ID and log each API request."""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    token = request_id_context.set(request_id)

    try:
        logger.info(
            "Request started: %s %s",
            request.method,
            request.url.path,
        )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed with status %s",
            response.status_code,
        )
        return response

    except Exception:
        logger.exception("Request failed")
        response = JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred.",
                }
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response

    finally:
        request_id_context.reset(token)


class AskRequest(BaseModel):
    """Request body for the ask endpoint."""

    question: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    user_roles: list[str] = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class AskResponse(BaseModel):
    """Response returned by the ask endpoint."""

    answer: str
    citations: list[dict]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Return a consistent error response for invalid requests."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid or missing fields.",
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Return a consistent error response for HTTP errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Hide internal exception details from API clients."""
    logger.error(
        "Unhandled application error",
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
    )


@app.get("/health")
def health():
    """Check whether the application and database are available."""
    try:
        check_connection()
        return {"status": "healthy", "database": "connected"}
    except Exception:
        logger.exception("Health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable",
        ) from None


@app.post("/ask", response_model=AskResponse)
def ask_policy_question(request: AskRequest):
    """Answer an HR policy question using the existing RAG service."""
    try:
        result = ask(
            question=request.question,
            tenant_id=request.tenant_id,
            user_roles=request.user_roles,
            limit=request.limit,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
