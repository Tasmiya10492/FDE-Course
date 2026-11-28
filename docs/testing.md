# Testing Guide

Run these commands from `day8-pgvector/`.

## Formatting and lint
- `uv run ruff format --check src tests`
- `uv run ruff check src tests`

## Type checking
- `uv run pyright src tests`

## Automated tests
- `uv run pytest -q tests`

## Security checks
- `uv run bandit -r src`
- `uv run pip-audit`

Use an isolated test database for automated tests, not production data.
