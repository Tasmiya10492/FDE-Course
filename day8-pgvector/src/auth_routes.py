"""Registration, login, logout and server-side session authentication."""

import re
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from psycopg.errors import UniqueViolation
from psycopg.types.json import Jsonb
from pydantic import BaseModel, ConfigDict, Field

from src.database import get_connection
from src.password_security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

SESSION_DURATION = timedelta(hours=1)
MAX_LOGIN_ATTEMPTS = 5


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=1024)


def normalize_email(email: str) -> str:
    """Normalize and validate an email address."""
    normalized = email.strip().casefold()

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
        raise HTTPException(status_code=422, detail="Invalid email address")

    return normalized


def client_ip(request: Request) -> str:
    """Return the direct client address."""
    return request.client.host if request.client else "unknown"


def write_audit_event(
    event_type: str,
    request: Request,
    actor_user_id: UUID | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    details: dict | None = None,
) -> None:
    """Write an audit event without recording credentials."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO audit_events (
                actor_user_id, event_type, target_type,
                target_id, ip_address, details
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                actor_user_id,
                event_type,
                target_type,
                target_id,
                client_ip(request),
                Jsonb(details or {}),
            ),
        )


def get_current_user(request: Request) -> dict:
    """Validate the signed cookie against the server-side session table."""
    session_id = request.session.get("session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        parsed_session_id = UUID(session_id)
    except ValueError, TypeError:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Invalid session") from None

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT u.id, u.email, u.role
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.session_id = %s
              AND s.expires_at > NOW()
            """,
            (parsed_session_id,),
        ).fetchone()

        if user is None:
            request.session.clear()
            raise HTTPException(status_code=401, detail="Session expired or invalid")

        connection.execute(
            """
            UPDATE user_sessions
            SET last_seen_at = NOW()
            WHERE session_id = %s
            """,
            (parsed_session_id,),
        )

    return {"id": user[0], "email": user[1], "role": user[2]}


@router.post("/register", status_code=201)
def register(payload: Credentials, request: Request):
    """Register a new employee account."""
    email = normalize_email(payload.email)

    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

    try:
        with get_connection() as connection:
            user = connection.execute(
                """
                INSERT INTO users (email, password_hash, role)
                VALUES (%s, %s, 'employee')
                RETURNING id, email, role
                """,
                (email, password_hash),
            ).fetchone()
    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists",
        ) from None

    write_audit_event(
        "registration_success",
        request,
        actor_user_id=user[0],
        target_type="user",
        target_id=str(user[0]),
    )

    return {"id": str(user[0]), "email": user[1], "role": user[2]}


@router.post("/login")
def login(payload: Credentials, request: Request):
    """Authenticate credentials and create a server-side session."""
    email = normalize_email(payload.email)
    ip = client_ip(request)

    with get_connection() as connection:
        attempt = connection.execute(
            """
            SELECT locked_until
            FROM login_attempts
            WHERE email = %s AND ip_address = %s
            """,
            (email, ip),
        ).fetchone()

        if attempt and attempt[0] and attempt[0] > datetime.now(UTC):
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Try again later.",
            )

        user = connection.execute(
            """
            SELECT id, email, password_hash, role
            FROM users
            WHERE email = %s
            """,
            (email,),
        ).fetchone()

        valid = user is not None and verify_password(payload.password, user[2])

        if not valid:
            connection.execute(
                """
                INSERT INTO login_attempts (
                    email, ip_address, failed_attempts
                )
                VALUES (%s, %s, 1)
                ON CONFLICT (email, ip_address)
                DO UPDATE SET
                    failed_attempts = CASE
                        WHEN login_attempts.window_started_at
                             < NOW() - INTERVAL '15 minutes'
                        THEN 1
                        ELSE login_attempts.failed_attempts + 1
                    END,
                    window_started_at = CASE
                        WHEN login_attempts.window_started_at
                             < NOW() - INTERVAL '15 minutes'
                        THEN NOW()
                        ELSE login_attempts.window_started_at
                    END
                """,
                (email, ip),
            )

            connection.execute(
                """
                UPDATE login_attempts
                SET locked_until = NOW() + INTERVAL '15 minutes'
                WHERE email = %s
                  AND ip_address = %s
                  AND failed_attempts >= %s
                """,
                (email, ip, MAX_LOGIN_ATTEMPTS),
            )

            failed_user_id = None
        else:
            connection.execute(
                """
                DELETE FROM login_attempts
                WHERE email = %s AND ip_address = %s
                """,
                (email, ip),
            )
            failed_user_id = user[0]

    if failed_user_id is None:
        write_audit_event(
            "login_failure",
            request,
            details={"email": email},
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")

    session_id = uuid4()
    expires_at = datetime.now(UTC) + SESSION_DURATION

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO user_sessions (session_id, user_id, expires_at)
            VALUES (%s, %s, %s)
            """,
            (session_id, user[0], expires_at),
        )

    request.session.clear()
    request.session["session_id"] = str(session_id)

    write_audit_event(
        "login_success",
        request,
        actor_user_id=user[0],
        target_type="user",
        target_id=str(user[0]),
    )

    return {
        "message": "Login successful",
        "user": {"id": str(user[0]), "email": user[1], "role": user[3]},
    }


@router.get("/me")
def current_user(user: dict = Depends(get_current_user)):  # noqa: B008
    """Return the authenticated user's identity."""
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
    }


@router.post("/logout")
def logout(request: Request, user: dict = Depends(get_current_user)):  # noqa: B008
    """Invalidate the server-side session and clear the cookie."""
    session_id = UUID(request.session["session_id"])

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM user_sessions WHERE session_id = %s",
            (session_id,),
        )

    write_audit_event(
        "logout",
        request,
        actor_user_id=user["id"],
        target_type="user",
        target_id=str(user["id"]),
    )

    request.session.clear()
    return {"message": "Logout successful"}
