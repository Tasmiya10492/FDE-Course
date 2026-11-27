"""Tests for application CORS middleware."""

from fastapi.testclient import TestClient
from src.config import get_settings
from src.main import app
from starlette.middleware.cors import CORSMiddleware


def test_cors_middleware_is_registered_with_restricted_settings():
    cors = next(
        middleware for middleware in app.user_middleware if middleware.cls is CORSMiddleware
    )

    assert cors.kwargs["allow_origins"] == get_settings().cors_origins
    assert cors.kwargs["allow_credentials"] is False
    assert cors.kwargs["allow_methods"] == ["GET", "POST", "OPTIONS"]
    assert cors.kwargs["allow_headers"] == ["Content-Type", "X-API-Key"]


def test_cors_preflight_rejects_untrusted_origin():
    client = TestClient(app)

    response = client.options(
        "/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
