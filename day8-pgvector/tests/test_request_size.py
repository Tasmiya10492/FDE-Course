"""Tests for HTTP request body size protection."""

import src.main as main
from fastapi.testclient import TestClient

client = TestClient(main.app, raise_server_exceptions=False)


def test_oversized_request_is_rejected():
    """Requests larger than 2 MiB receive HTTP 413."""
    body = b"x" * (main.MAX_REQUEST_BODY_BYTES + 1)

    response = client.post(
        "/ask",
        content=body,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "REQUEST_TOO_LARGE"
    assert response.headers.get("X-Request-ID")
    assert response.headers.get("Content-Security-Policy")


def test_normal_request_reaches_endpoint():
    """A small request passes the size check."""
    response = client.post(
        "/ask",
        json={},
    )

    # The request is small, so it reaches the API's authentication check.
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "HTTP_ERROR"
