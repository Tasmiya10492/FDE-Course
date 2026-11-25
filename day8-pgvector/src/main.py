"""FastAPI application for the HR policy RAG assistant."""

import json
import logging
import secrets
from contextvars import ContextVar
from datetime import UTC, datetime
from math import ceil
from threading import Lock
from time import monotonic
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import select_autoescape
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from starlette.middleware.sessions import SessionMiddleware

from src.auth_routes import router as auth_router
from src.config import PROJECT_ROOT, get_settings
from src.database import check_connection
from src.rag_service import ask
from src.record_routes import router as record_router
from src.upload_routes import router as upload_router

MAX_REQUEST_BODY_BYTES = 2 * 1024 * 1024


class RequestSizeLimitMiddleware:
    """Reject HTTP requests whose body exceeds the configured size."""

    def __init__(self, app, max_body_size: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_body_size = max_body_size

    def _declared_body_is_too_large(self, scope) -> bool:
        """Check whether Content-Length declares an oversized request."""
        content_length = next(
            (
                value
                for name, value in scope.get("headers", [])
                if name.lower() == b"content-length"
            ),
            None,
        )

        if content_length is None:
            return False

        try:
            declared_size = int(content_length)
        except ValueError:
            return False

        return declared_size > self.max_body_size

    async def _read_request_body(self, receive) -> tuple[bytes, bool, bool]:
        """Read and buffer the body, enforcing the maximum size."""
        body = bytearray()

        while True:
            message = await receive()

            if message["type"] == "http.disconnect":
                return b"", False, True

            if message["type"] != "http.request":
                continue

            chunk = message.get("body", b"")

            if len(body) + len(chunk) > self.max_body_size:
                return b"", True, False

            body.extend(chunk)

            if not message.get("more_body", False):
                return bytes(body), False, False

    async def _send_too_large(self, scope, receive, send):
        """Return a consistent HTTP 413 response."""
        response = JSONResponse(
            status_code=413,
            content={
                "error": {
                    "code": "REQUEST_TOO_LARGE",
                    "message": "Request body exceeds the 2 MiB size limit.",
                }
            },
        )
        await response(scope, receive, send)

    async def __call__(self, scope, receive, send):
        """Apply the body-size check to HTTP requests."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if scope["method"] in {"GET", "HEAD", "OPTIONS"}:
            await self.app(scope, receive, send)
            return

        if self._declared_body_is_too_large(scope):
            await self._send_too_large(scope, receive, send)
            return

        body, too_large, disconnected = await self._read_request_body(receive)

        if disconnected:
            return

        if too_large:
            await self._send_too_large(scope, receive, send)
            return

        body_sent = False

        async def replay_body():
            nonlocal body_sent

            if not body_sent:
                body_sent = True
                return {
                    "type": "http.request",
                    "body": body,
                    "more_body": False,
                }

            return {"type": "http.disconnect"}

        await self.app(scope, replay_body, send)


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

# In-memory rate limiting: suitable for a single application process.
RATE_LIMIT_MAX_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60

_rate_limit_buckets: dict[str, tuple[float, int]] = {}
_rate_limit_lock = Lock()


def get_rate_limit_retry_after(client_ip: str) -> int | None:
    """Return retry delay when the client has exceeded its request limit."""
    now = monotonic()

    with _rate_limit_lock:
        window_start, request_count = _rate_limit_buckets.get(
            client_ip,
            (now, 0),
        )

        if now - window_start >= RATE_LIMIT_WINDOW_SECONDS:
            window_start = now
            request_count = 0

        if request_count >= RATE_LIMIT_MAX_REQUESTS:
            remaining = window_start + RATE_LIMIT_WINDOW_SECONDS - now
            return max(1, ceil(remaining))

        _rate_limit_buckets[client_ip] = (
            window_start,
            request_count + 1,
        )

        # Periodically remove expired client entries to limit memory growth.
        if len(_rate_limit_buckets) > 10_000:
            expired_clients = [
                ip
                for ip, (start, _) in _rate_limit_buckets.items()
                if now - start >= RATE_LIMIT_WINDOW_SECONDS
            ]

            for ip in expired_clients:
                _rate_limit_buckets.pop(ip, None)

    return None


settings = get_settings()
if not settings.session_secret:
    if settings.environment == "production":
        raise RuntimeError("A secure SESSION_SECRET must be configured in production.")

    settings.session_secret = secrets.token_urlsafe(48)

app = FastAPI(
    title="HR Policy RAG API",
    description="Ask questions about HR policies with permission-filtered citations.",
    version="1.0.0",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
)

app.add_middleware(
    RequestSizeLimitMiddleware,
    max_body_size=MAX_REQUEST_BODY_BYTES,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie="hr_policy_session",
    max_age=3600,
    same_site="lax",
    https_only=settings.environment == "production",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
    max_age=600,
)

app.include_router(auth_router)
app.include_router(record_router)
app.include_router(upload_router)


def add_security_headers(response):
    """Add browser security headers to every response."""

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://unpkg.com; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"

    return response


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

        retry_after = None

        if request.url.path != "/health" and request.method != "OPTIONS":
            client_ip = request.client.host if request.client else "unknown"
            retry_after = get_rate_limit_retry_after(client_ip)

        if retry_after is not None:
            response = JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Try again later.",
                    }
                },
                headers={"Retry-After": str(retry_after)},
            )
        else:
            response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        add_security_headers(response)

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
        add_security_headers(response)
        return response

    finally:
        request_id_context.reset(token)


templates = Jinja2Templates(
    directory=str(PROJECT_ROOT / "templates"),
)

templates.env.autoescape = select_autoescape(
    enabled_extensions=("html", "htm", "xml"),
    default_for_string=True,
)

app.mount(
    "/static",
    StaticFiles(directory=str(PROJECT_ROOT / "static")),
    name="static",
)


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class AskResponse(BaseModel):
    """Response returned by the ask endpoint."""

    answer: str
    citations: list[dict]


def get_api_identity(
    api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> tuple[str, list[str]]:
    settings = get_settings()

    employee_key = settings.employee_api_key
    hr_key = settings.hr_api_key

    # Fail closed if the API credentials are missing or identical.
    if not employee_key or not hr_key or secrets.compare_digest(employee_key, hr_key):
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured",
        )

    provided_key = api_key or ""

    if secrets.compare_digest(provided_key, employee_key):
        return "main", ["employee"]

    if secrets.compare_digest(provided_key, hr_key):
        return "main", ["HR administrator"]

    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API key",
    )


@app.get("/ui", response_class=HTMLResponse)
async def knowledge_assistant(request: Request):
    """Render the Knowledge Assistant browser page."""

    csrf_token = request.session.get("csrf_token")

    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = csrf_token

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"csrf_token": csrf_token},
    )


@app.post("/ui/ask", response_class=HTMLResponse)
async def ask_from_ui(request: Request):
    """Process an HTMX question and return an HTML answer fragment."""

    form = await request.form()

    submitted_token = str(form.get("csrf_token", ""))
    expected_token = request.session.get("csrf_token", "")

    if (
        not expected_token
        or not submitted_token
        or not secrets.compare_digest(submitted_token, expected_token)
    ):
        return templates.TemplateResponse(
            request=request,
            name="partials/error.html",
            context={
                "message": "Your session could not be verified. Refresh the page and try again."
            },
            status_code=403,
        )

    question = str(form.get("question", "")).strip()

    if not question:
        return templates.TemplateResponse(
            request=request,
            name="partials/error.html",
            context={"message": "Please enter a question before submitting."},
        )

    if len(question) > 2000:
        return templates.TemplateResponse(
            request=request,
            name="partials/error.html",
            context={
                "message": "Your question is too long. Please keep it within 2,000 characters."
            },
        )

    try:
        result = await run_in_threadpool(
            ask,
            question=question,
            tenant_id="tenant_a",
            user_roles=["Employee"],
            limit=5,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="partials/error.html",
            context={"message": str(exc)},
        )

    except Exception:
        logger.exception("Knowledge Assistant UI request failed")

        return templates.TemplateResponse(
            request=request,
            name="partials/error.html",
            context={
                "message": "The assistant could not complete your request. Please try again."
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="partials/answer.html",
        context={
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
        },
    )


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
        headers=exc.headers,
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
def ask_policy_question(
    request: AskRequest,
    identity: tuple[str, list[str]] = Depends(get_api_identity),
):
    tenant_id, user_roles = identity

    try:
        result = ask(
            question=request.question,
            tenant_id=tenant_id,
            user_roles=user_roles,
            limit=request.limit,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
