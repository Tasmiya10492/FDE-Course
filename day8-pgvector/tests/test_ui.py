import re

from fastapi.testclient import TestClient

from src import main


def get_csrf_token(client: TestClient) -> str:
    """Load the UI page and extract its CSRF token."""

    response = client.get("/ui")
    assert response.status_code == 200

    input_match = re.search(
        r'<input[^>]*name="csrf_token"[^>]*>',
        response.text,
    )

    assert input_match is not None

    token_match = re.search(
        r'value="([^"]+)"',
        input_match.group(0),
    )

    assert token_match is not None

    return token_match.group(1)


def test_ui_page_loads():
    client = TestClient(main.app)

    response = client.get("/ui")

    assert response.status_code == 200
    assert "Knowledge Assistant" in response.text
    assert 'name="csrf_token"' in response.text
    assert 'name="question"' in response.text
    assert "Content-Security-Policy" in response.headers


def test_ui_rejects_invalid_csrf_token():
    client = TestClient(main.app)

    get_csrf_token(client)

    response = client.post(
        "/ui/ask",
        data={
            "csrf_token": "invalid-token",
            "question": "How many annual leave days are available?",
        },
    )

    assert response.status_code == 403
    assert "session could not be verified" in response.text


def test_ui_rejects_blank_question():
    client = TestClient(main.app)
    csrf_token = get_csrf_token(client)

    response = client.post(
        "/ui/ask",
        data={
            "csrf_token": csrf_token,
            "question": "   ",
        },
    )

    assert response.status_code == 200
    assert "Please enter a question" in response.text


def test_ui_rejects_question_over_2000_characters():
    client = TestClient(main.app)
    csrf_token = get_csrf_token(client)

    response = client.post(
        "/ui/ask",
        data={
            "csrf_token": csrf_token,
            "question": "A" * 2001,
        },
    )

    assert response.status_code == 200
    assert "2,000 characters" in response.text


def test_ui_returns_answer_and_citations(monkeypatch):
    client = TestClient(main.app)
    csrf_token = get_csrf_token(client)

    def fake_ask(**kwargs):
        assert kwargs["tenant_id"] == "tenant_a"
        assert kwargs["user_roles"] == ["Employee"]

        return {
            "answer": "A full-time employee receives 25 days of paid annual leave.",
            "citations": [
                {
                    "source": "HR Leave Policy",
                    "chunk_id": "8013",
                    "passage": "Full-time employees receive 25 days of annual leave.",
                }
            ],
        }

    monkeypatch.setattr(main, "ask", fake_ask)

    response = client.post(
        "/ui/ask",
        data={
            "csrf_token": csrf_token,
            "question": "How many annual leave days are available?",
        },
    )

    assert response.status_code == 200
    assert "25 days" in response.text
    assert "HR Leave Policy" in response.text
    assert "8013" in response.text


def test_ui_escapes_untrusted_html(monkeypatch):
    client = TestClient(main.app)
    csrf_token = get_csrf_token(client)

    def fake_ask(**kwargs):
        return {
            "answer": "<script>alert('answer')</script>",
            "citations": [
                {
                    "source": "<img src=x onerror=alert(1)>",
                    "chunk_id": "xss-test",
                    "passage": "<script>alert('citation')</script>",
                }
            ],
        }

    monkeypatch.setattr(main, "ask", fake_ask)

    response = client.post(
        "/ui/ask",
        data={
            "csrf_token": csrf_token,
            "question": "Test HTML escaping",
        },
    )

    assert response.status_code == 200
    assert "&lt;script&gt;" in response.text
    assert "&lt;img" in response.text
    assert "<script>alert('answer')</script>" not in response.text
    assert "&lt;img src=x onerror=alert(1)&gt;" in response.text
    assert "<img src=x onerror=alert(1)>" not in response.text


def test_ui_security_headers():
    client = TestClient(main.app)

    response = client.get("/ui")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Permissions-Policy" in response.headers


def test_ui_static_css_is_available():
    client = TestClient(main.app)

    response = client.get("/static/styles.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_ui_htmx_configuration_is_available():
    client = TestClient(main.app)

    response = client.get("/static/ui.js")

    assert response.status_code == 200
    assert 'code: "403"' in response.text
    assert "swap: true" in response.text
