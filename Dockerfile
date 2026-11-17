# syntax=docker/dockerfile:1
#
# Dockerfile: the recipe that turns this repository into a container image.
# Read it from top to bottom. Each block has a comment that says what it does and why.
#
# BEFORE FIRST USE replace the <PLACEHOLDERS>. How to find each value is written in
# starter_kit/PLACEHOLDERS.md. Short form: open the image's official page, use the current
# stable release, copy its tag and digest, paste them here.
#

# ---------------------------------------------------------------- stage 1: build
# A "multi-stage" build keeps build tools out of the final image (CTR-01).
FROM python:3.14.10-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f AS builder

# Copy the uv program from its official image instead of installing it with pip.
COPY --from=ghcr.io/astral-sh/uv:0.13.8@sha256:5cc1805e2426484abca4ad46ea783bab281fdb225fd82d8ce6d66a81254bac85 /uv /bin/uv

WORKDIR /build
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy only the dependency files first. Docker caches this step, so a code change does not
# re-install every package. uv.lock must exist: run `uv lock` once and commit it (README, Quick start).
COPY pyproject.toml uv.lock ./
COPY day8-pgvector/pyproject.toml ./day8-pgvector/pyproject.toml

# Install dependencies without installing workspace projects.
RUN uv sync --locked --no-dev --no-install-workspace

# ---------------------------------------------------------------- stage 2: run
FROM python:3.14.10-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f AS runtime

# Run as a normal user with a fixed ID, never as root (CTR-02).
RUN useradd --create-home --uid 1000 --shell /bin/sh appuser

WORKDIR /app

# Bring the installed libraries from stage 1.
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy the application code and give it to the normal user.
COPY --chown=appuser:appuser app/ ./app/

USER appuser
EXPOSE 8000

# The container reports its own health. Slim images have no curl, so we use a tiny Python call.
# It asks /health/ready, which also checks dependencies (CTR-06).
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request, sys; r = urllib.request.urlopen('http://localhost:8000/health/ready', timeout=8); sys.exit(0 if r.status == 200 else 1)"

# `exec` makes uvicorn the main process, so it receives the stop signal (SIGTERM) and can
# finish current requests before exiting (CTR-07, ARC-08).
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=\"${FORWARDED_ALLOW_IPS:-127.0.0.1}\" --no-access-log"]
