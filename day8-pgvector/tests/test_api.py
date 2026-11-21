"""Tests for the FastAPI application."""

from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app, raise_server_exceptions=False)

# Temporary credentials used only by these tests.
EMPLOYEE_TEST_KEY = "employee-test-placeholder"
HR_TEST_KEY = "hr-test-placeholder"

EXPECTED_ANSWER = {
    "answer": "Annual leave depends on grade, contract type, and service.",
    "citations": [],
}


def configured_settings(employee_key=EMPLOYEE_TEST_KEY, hr_key=HR_TEST_KEY):
    """Return temporary API credentials for tests."""
    return SimpleNamespace(
        employee_api_key=employee_key,
        hr_api_key=hr_key,
    )


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


def test_ask_employee_success():
    with (
        patch("src.main.get_settings", return_value=configured_settings()),
        patch("src.main.ask", return_value=EXPECTED_ANSWER) as mock_ask,
    ):
        response = client.post(
            "/ask",
            headers={"X-API-Key": EMPLOYEE_TEST_KEY},
            json={
                "question": "What factors determine annual leave?",
                "limit": 5,
            },
        )

    assert response.status_code == 200
    assert response.json() == EXPECTED_ANSWER
    mock_ask.assert_called_once_with(
        question="What factors determine annual leave?",
        tenant_id="main",
        user_roles=["employee"],
        limit=5,
    )
    assert response.headers.get("X-Request-ID")


def test_ask_hr_success():
    with (
        patch("src.main.get_settings", return_value=configured_settings()),
        patch("src.main.ask", return_value=EXPECTED_ANSWER) as mock_ask,
    ):
        response = client.post(
            "/ask",
            headers={"X-API-Key": HR_TEST_KEY},
            json={"question": "What is the disciplinary procedure?"},
        )

    assert response.status_code == 200
    mock_ask.assert_called_once_with(
        question="What is the disciplinary procedure?",
        tenant_id="main",
        user_roles=["HR administrator"],
        limit=5,
    )


def test_ask_missing_api_key():
    with patch("src.main.get_settings", return_value=configured_settings()):
        response = client.post(
            "/ask",
            json={"question": "What is annual leave?"},
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "HTTP_ERROR"


def test_ask_invalid_api_key():
    with patch("src.main.get_settings", return_value=configured_settings()):
        response = client.post(
            "/ask",
            headers={"X-API-Key": "incorrect-test-key"},
            json={"question": "What is annual leave?"},
        )

    assert response.status_code == 401


def test_ask_missing_server_credentials():
    incomplete_settings = configured_settings(employee_key="", hr_key=HR_TEST_KEY)

    with patch("src.main.get_settings", return_value=incomplete_settings):
        response = client.post(
            "/ask",
            headers={"X-API-Key": EMPLOYEE_TEST_KEY},
            json={"question": "What is annual leave?"},
        )

    assert response.status_code == 503


def test_ask_identical_server_credentials():
    identical_settings = configured_settings(
        employee_key="same-test-key",
        hr_key="same-test-key",
    )

    with patch("src.main.get_settings", return_value=identical_settings):
        response = client.post(
            "/ask",
            headers={"X-API-Key": "same-test-key"},
            json={"question": "What is annual leave?"},
        )

    assert response.status_code == 503


def test_ask_rejects_caller_supplied_roles():
    with (
        patch("src.main.get_settings", return_value=configured_settings()),
        patch("src.main.ask") as mock_ask,
    ):
        response = client.post(
            "/ask",
            headers={"X-API-Key": EMPLOYEE_TEST_KEY},
            json={
                "question": "What is annual leave?",
                "user_roles": ["HR"],
            },
        )

    assert response.status_code == 422
    mock_ask.assert_not_called()


def test_ask_rejects_caller_supplied_tenant():
    with (
        patch("src.main.get_settings", return_value=configured_settings()),
        patch("src.main.ask") as mock_ask,
    ):
        response = client.post(
            "/ask",
            headers={"X-API-Key": EMPLOYEE_TEST_KEY},
            json={
                "question": "What is annual leave?",
                "tenant_id": "another_tenant",
            },
        )

    assert response.status_code == 422
    mock_ask.assert_not_called()


def test_ask_missing_question():
    with patch("src.main.get_settings", return_value=configured_settings()):
        response = client.post(
            "/ask",
            headers={"X-API-Key": EMPLOYEE_TEST_KEY},
            json={"limit": 5},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.headers.get("X-Request-ID")


def test_ask_empty_question():
    with (
        patch("src.main.get_settings", return_value=configured_settings()),
        patch(
            "src.main.ask",
            side_effect=ValueError("Question cannot be empty"),
        ),
    ):
        response = client.post(
            "/ask",
            headers={"X-API-Key": EMPLOYEE_TEST_KEY},
            json={"question": "   "},
        )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "HTTP_ERROR"
    assert response.headers.get("X-Request-ID")


def test_ask_unexpected_error():
    with (
        patch("src.main.get_settings", return_value=configured_settings()),
        patch(
            "src.main.ask",
            side_effect=RuntimeError("Internal database details"),
        ),
    ):
        response = client.post(
            "/ask",
            headers={"X-API-Key": EMPLOYEE_TEST_KEY},
            json={"question": "What is annual leave?"},
        )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "Internal database details" not in response.text
    assert response.headers.get("X-Request-ID")
