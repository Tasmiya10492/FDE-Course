"""Tests for application rate limiting."""

import pytest
import src.main as main
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def clear_rate_limit_buckets():
    """Keep rate-limit state isolated between tests."""
    main._rate_limit_buckets.clear()
    yield
    main._rate_limit_buckets.clear()


def test_rate_limit_allows_requests_until_limit(monkeypatch):
    """Requests are allowed until the configured limit is reached."""
    monkeypatch.setattr(main, "RATE_LIMIT_MAX_REQUESTS", 2)

    assert main.get_rate_limit_retry_after("198.51.100.10") is None
    assert main.get_rate_limit_retry_after("198.51.100.10") is None

    retry_after = main.get_rate_limit_retry_after("198.51.100.10")

    assert isinstance(retry_after, int)
    assert retry_after >= 1


def test_rate_limit_resets_after_window(monkeypatch):
    """A new time window allows requests again."""
    monkeypatch.setattr(main, "RATE_LIMIT_MAX_REQUESTS", 1)
    monkeypatch.setattr(main, "RATE_LIMIT_WINDOW_SECONDS", 60)

    times = iter([100.0, 101.0, 160.0])
    monkeypatch.setattr(main, "monotonic", lambda: next(times))

    assert main.get_rate_limit_retry_after("198.51.100.20") is None

    retry_after = main.get_rate_limit_retry_after("198.51.100.20")
    assert retry_after == 59

    assert main.get_rate_limit_retry_after("198.51.100.20") is None


def test_rate_limit_middleware_returns_429_and_retry_after(monkeypatch):
    """The middleware blocks excess requests and preserves response headers."""
    monkeypatch.setattr(main, "RATE_LIMIT_MAX_REQUESTS", 1)

    client = TestClient(main.app)

    # Health checks must not consume the client's request allowance.
    client.get("/health")

    first_response = client.get("/ui")
    assert first_response.status_code != 429

    second_response = client.get("/ui")

    assert second_response.status_code == 429
    assert second_response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert int(second_response.headers["Retry-After"]) >= 1
    assert "X-Request-ID" in second_response.headers
    assert "Content-Security-Policy" in second_response.headers
