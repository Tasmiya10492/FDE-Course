"""Integration tests for Day 16 RBAC and record ownership."""

from uuid import uuid4

from fastapi.testclient import TestClient
from src.database import get_connection
from src.main import app


def test_role_endpoint_ownership_matrix():
    """Verify record permissions for employees, managers and HR admins."""

    suffix = uuid4().hex
    credential = "FDE-Day16-Strong-Passphrase-2026!"

    accounts = {
        "employee": f"employee-{suffix}@example.com",
        "line_manager": f"manager-{suffix}@example.com",
        "hr_administrator": f"hr-{suffix}@example.com",
    }

    clients = {role: TestClient(app) for role in accounts}

    try:
        # 1. Register three users. Registration assigns employee by default.
        for role, email in accounts.items():
            response = clients[role].post(
                "/auth/register",
                json={"email": email, "password": credential},
            )
            assert response.status_code == 201, response.text

        # 2. Promote the manager and HR accounts to their test roles.
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

        # 3. Log in all three users and establish their sessions.
        for role, client in clients.items():
            response = client.post(
                "/auth/login",
                json={"email": accounts[role], "password": credential},
            )
            assert response.status_code == 200, response.text
            assert response.json()["user"]["role"] == role

        # 4. Verify all three roles can create their own records.
        record_ids = {}

        for role, client in clients.items():
            response = client.post(
                "/records",
                json={
                    "title": f"{role} test record",
                    "content": f"Ownership test for {role}",
                },
            )
            assert response.status_code == 201, response.text

            record = response.json()
            record_ids[role] = record["id"]

            # The server must assign ownership to the logged-in user.
            assert record["owner_id"]

        employee_record = record_ids["employee"]
        manager_record = record_ids["line_manager"]

        # 5. Employees can list only their own records.
        response = clients["employee"].get("/records")
        assert response.status_code == 200
        assert {r["id"] for r in response.json()} == {employee_record}

        # 6. Line managers can list only their own records.
        response = clients["line_manager"].get("/records")
        assert response.status_code == 200
        assert {r["id"] for r in response.json()} == {manager_record}

        # 7. HR administrators can list records belonging to all users.
        response = clients["hr_administrator"].get("/records")
        assert response.status_code == 200
        hr_record_ids = {r["id"] for r in response.json()}
        assert set(record_ids.values()).issubset(hr_record_ids)

        # 8. Every role can read its own record.
        for role, client in clients.items():
            response = client.get(f"/records/{record_ids[role]}")
            assert response.status_code == 200, response.text

        # 9. Employee cannot read the manager's record.
        response = clients["employee"].get(f"/records/{manager_record}")
        assert response.status_code == 404

        # 10. Manager cannot read the employee's record.
        response = clients["line_manager"].get(f"/records/{employee_record}")
        assert response.status_code == 404

        # 11. HR administrator can read another user's record.
        response = clients["hr_administrator"].get(f"/records/{employee_record}")
        assert response.status_code == 200

        # 12. Verify both denied attempts were recorded in the audit log.
        with get_connection() as connection:
            denied_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM audit_events
                WHERE event_type = 'record_access_denied'
                  AND target_id = ANY(%s)
                """,
                ([employee_record, manager_record],),
            ).fetchone()[0]

        assert denied_count >= 2

        # 13. Unauthenticated users cannot list or create records.
        anonymous_client = TestClient(app)
        assert anonymous_client.get("/records").status_code == 401
        assert (
            anonymous_client.post(
                "/records",
                json={"title": "Unauthenticated record", "content": ""},
            ).status_code
            == 401
        )

    finally:
        # 14. Remove only the temporary test accounts and their login attempts.
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
