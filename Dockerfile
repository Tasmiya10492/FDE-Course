# syntax=docker/dockerfile:1

# ------------------------------------------------------------
# Stage 1: Install production dependencies
# ------------------------------------------------------------
FROM python:3.14.10-slim@sha256:f57c4c23b985d95deea5bc5249e2f9c8a512b4cc9d5d3fd31900cbd2f5f0a604 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.8@sha256:5cc1805e2426484abca4ad46ea783bab281fdb225fd82d8ce6d66a81254bac85 /uv /bin/uv

WORKDIR /build

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy workspace dependency metadata first for better build caching.
COPY pyproject.toml uv.lock ./
COPY day8-pgvector/pyproject.toml ./day8-pgvector/pyproject.toml

# Install only the HR application's production dependencies.
RUN uv sync --project day8-pgvector --locked --no-dev --no-install-project

# ------------------------------------------------------------
# Stage 2: Minimal runtime
# ------------------------------------------------------------
FROM python:3.14.10-slim@sha256:f57c4c23b985d95deea5bc5249e2f9c8a512b4cc9d5d3fd31900cbd2f5f0a604 AS runtime

# Apply available Debian security and package updates.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Create a fixed non-root application identity.
RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin appuser

WORKDIR /app

# Copy the virtual environment from the builder.
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy only the files needed at runtime.
COPY --chown=appuser:appuser day8-pgvector/src ./src
COPY --chown=appuser:appuser day8-pgvector/templates ./templates
COPY --chown=appuser:appuser day8-pgvector/static ./static
COPY --chown=appuser:appuser day8-pgvector/data ./data

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

USER appuser

EXPOSE 8000

# Readiness includes a database connectivity check.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=8)"

# Exec-form command allows Uvicorn to receive SIGTERM directly.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
