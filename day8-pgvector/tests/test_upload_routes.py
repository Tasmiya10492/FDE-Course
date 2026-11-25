"""Integration tests for secure document uploads."""

import re
import stat
from uuid import uuid4

import src.main as main
from fastapi.testclient import TestClient
from src.database import get_connection
from src.main import app
from src.upload_routes import MAX_UPLOAD_BYTES, UPLOAD_DIR


def test_document_upload_authorization_and_file_validation(monkeypatch):
    """Verify upload authorization, validation and secure file storage."""

    # Keep this test independent of the normal request-rate threshold.
    monkeypatch.setattr(main, "RATE_LIMIT_MAX_REQUESTS", 1000)

    suffix = uuid4().hex
    credential = "FDE-Day17-Strong-Passphrase-2026!"

    accounts = {
        "employee": f"employee-upload-{suffix}@example.com",
        "line_manager": f"manager-upload-{suffix}@example.com",
        "hr_administrator": f"hr-upload-{suffix}@example.com",
    }

    clients = {role: TestClient(app) for role in accounts}
    anonymous_client = TestClient(app)
    uploaded_filenames = []

    try:
        # 1. Register three users.
        for role, email in accounts.items():
            response = clients[role].post(
                "/auth/register",
                json={"email": email, "password": credential},
            )
            assert response.status_code == 201, response.text

        # 2. Promote the manager and HR accounts.
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE users
                SET role = 'line_manager'
                WHERE email = %s
                """,
                (accounts["line_manager"],),
            )
            connection.execute(
                """
                UPDATE users
                SET role = 'hr_administrator'
                WHERE email = %s
                """,
                (accounts["hr_administrator"],),
            )

        # 3. Log in all three users.
        for role, client in clients.items():
            response = client.post(
                "/auth/login",
                json={"email": accounts[role], "password": credential},
            )
            assert response.status_code == 200, response.text
            assert response.json()["user"]["role"] == role

        # 4. Anonymous users cannot upload.
        response = anonymous_client.post(
            "/documents/upload",
            files={"file": ("anonymous.txt", b"test", "text/plain")},
        )
        assert response.status_code == 401

        # 5. Employees cannot upload.
        response = clients["employee"].post(
            "/documents/upload",
            files={"file": ("employee.txt", b"test", "text/plain")},
        )
        assert response.status_code == 403

        # 6. Line managers cannot upload.
        response = clients["line_manager"].post(
            "/documents/upload",
            files={"file": ("manager.txt", b"test", "text/plain")},
        )
        assert response.status_code == 403

        hr_client = clients["hr_administrator"]

        # 7. HR administrators can upload a valid text document.
        response = hr_client.post(
            "/documents/upload",
            files={
                "file": (
                    "../../employee-policy.txt",
                    b"Example HR policy document.",
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201, response.text

        uploaded = response.json()
        generated_name = uploaded["filename"]
        uploaded_filenames.append(generated_name)

        assert generated_name != "../../employee-policy.txt"
        assert re.fullmatch(r"[0-9a-f]{32}\.txt", generated_name)

        stored_file = UPLOAD_DIR / generated_name
        assert stored_file.is_file()
        assert stored_file.read_bytes() == b"Example HR policy document."
        assert uploaded["size_bytes"] == len(b"Example HR policy document.")

        # 8. Verify restricted directory and file permissions.
        assert stat.S_IMODE(UPLOAD_DIR.stat().st_mode) == 0o700
        assert stat.S_IMODE(stored_file.stat().st_mode) == 0o600

        # 9. Markdown files with an accepted MIME type are allowed.
        response = hr_client.post(
            "/documents/upload",
            files={
                "file": (
                    "policy.md",
                    b"# Example policy",
                    "text/markdown",
                )
            },
        )

        assert response.status_code == 201, response.text
        markdown_name = response.json()["filename"]
        uploaded_filenames.append(markdown_name)
        assert markdown_name.endswith(".md")

        # 10. Unsupported extensions are rejected.
        response = hr_client.post(
            "/documents/upload",
            files={"file": ("script.exe", b"not allowed", "text/plain")},
        )
        assert response.status_code == 415

        # 11. A mismatched content type is rejected.
        response = hr_client.post(
            "/documents/upload",
            files={"file": ("policy.txt", b"not a PDF", "application/pdf")},
        )
        assert response.status_code == 415

        # 12. Empty files are rejected.
        response = hr_client.post(
            "/documents/upload",
            files={"file": ("empty.txt", b"", "text/plain")},
        )
        assert response.status_code == 400

        # 13. Invalid UTF-8 content is rejected.
        response = hr_client.post(
            "/documents/upload",
            files={"file": ("invalid.txt", b"\xff\xfe", "text/plain")},
        )
        assert response.status_code == 400

        # 14. NUL bytes are rejected.
        response = hr_client.post(
            "/documents/upload",
            files={"file": ("binary.txt", b"hello\x00world", "text/plain")},
        )
        assert response.status_code == 400

        # 15. Files larger than 1 MiB are rejected.
        oversized_content = b"x" * (MAX_UPLOAD_BYTES + 1)

        response = hr_client.post(
            "/documents/upload",
            files={
                "file": (
                    "oversized.txt",
                    oversized_content,
                    "text/plain",
                )
            },
        )
        assert response.status_code == 413

    finally:
        # Remove only the files created by this test.
        for filename in uploaded_filenames:
            stored_file = UPLOAD_DIR / filename
            if stored_file.exists():
                stored_file.unlink()

        # Remove only the temporary test accounts and login attempts.
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM login_attempts WHERE email = ANY(%s)",
                (list(accounts.values()),),
            )
            connection.execute(
                "DELETE FROM users WHERE email = ANY(%s)",
                (list(accounts.values()),),
            )

        for client in clients.values():
            client.close()

        anonymous_client.close()
