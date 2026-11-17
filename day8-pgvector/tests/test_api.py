"""Tests for the FastAPI application."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_success():
    with patch("src.main.check_connection"):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
    }
    assert response.headers.get("X-Request-ID")


def test_health_database_failure():
    with patch(
        "src.main.check_connection",
        side_effect=Exception("Database unavailable"),
    ):
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "HTTP_ERROR"
    assert response.json()["error"]["message"] == "Database is unavailable"
    assert "Database unavailable" not in response.text
    assert response.headers.get("X-Request-ID")


def test_ask_success():
    expected = {
        "answer": "Annual leave depends on grade, contract type, and service.",
        "citations": [],
    }

    with patch("src.main.ask", return_value=expected):
        response = client.post(
            "/ask",
            json={
                "question": "What factors determine annual leave?",
                "tenant_id": "tenant_a",
                "user_roles": ["HR", "Employee"],
                "limit": 5,
            },
        )

    assert response.status_code == 200
    assert response.json() == expected
    assert response.headers.get("X-Request-ID")


def test_ask_missing_question():
    response = client.post(
        "/ask",
        json={
            "tenant_id": "tenant_a",
            "user_roles": ["HR", "Employee"],
            "limit": 5,
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.headers.get("X-Request-ID")


def test_ask_empty_question():
    with patch(
        "src.main.ask",
        side_effect=ValueError("Question cannot be empty"),
    ):
        response = client.post(
            "/ask",
            json={
                "question": "   ",
                "tenant_id": "tenant_a",
                "user_roles": ["HR", "Employee"],
                "limit": 5,
            },
        )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "HTTP_ERROR"
    assert response.headers.get("X-Request-ID")


def test_ask_unexpected_error():
    with patch(
        "src.main.ask",
        side_effect=RuntimeError("Internal database details"),
    ):
        response = client.post(
            "/ask",
            json={
                "question": "What is annual leave?",
                "tenant_id": "tenant_a",
                "user_roles": ["HR", "Employee"],
                "limit": 5,
            },
        )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "Internal database details" not in response.text
    assert response.headers.get("X-Request-ID")
