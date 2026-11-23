"""Record endpoints with RBAC and object-level ownership checks."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from src.access_control import has_permission, require_permission
from src.database import get_connection

router = APIRouter(prefix="/records", tags=["Records"])

CreateUser = Annotated[
    dict,
    Depends(require_permission("records:create")),
]

ReadUser = Annotated[
    dict,
    Depends(require_permission("records:read_own")),
]


class RecordCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="", max_length=10000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty.")
        return value


@router.post("", status_code=201)
def create_record(
    payload: RecordCreate,
    request: Request,
    user: CreateUser,
):
    """Create a record owned by the authenticated user."""

    with get_connection() as connection:
        record = connection.execute(
            """
            INSERT INTO user_records (owner_id, title, content)
            VALUES (%s, %s, %s)
            RETURNING id, owner_id, title, content, created_at
            """,
            (user["id"], payload.title, payload.content),
        ).fetchone()

        connection.execute(
            """
            INSERT INTO audit_events (
                actor_user_id, event_type, target_type,
                target_id, ip_address
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user["id"],
                "record_created",
                "user_record",
                str(record[0]),
                request.client.host if request.client else "unknown",
            ),
        )

    return {
        "id": str(record[0]),
        "owner_id": str(record[1]),
        "title": record[2],
        "content": record[3],
        "created_at": record[4],
    }


@router.get("")
def list_records(user: ReadUser):
    """List records according to the user's role."""

    with get_connection() as connection:
        if has_permission(user, "records:read_any"):
            records = connection.execute(
                """
                SELECT id, owner_id, title, content, created_at
                FROM user_records
                ORDER BY created_at DESC
                """
            ).fetchall()
        else:
            records = connection.execute(
                """
                SELECT id, owner_id, title, content, created_at
                FROM user_records
                WHERE owner_id = %s
                ORDER BY created_at DESC
                """,
                (user["id"],),
            ).fetchall()

    return [
        {
            "id": str(row[0]),
            "owner_id": str(row[1]),
            "title": row[2],
            "content": row[3],
            "created_at": row[4],
        }
        for row in records
    ]


@router.get("/{record_id}")
def get_record(
    record_id: UUID,
    request: Request,
    user: ReadUser,
):
    """Retrieve a record only when the role and ownership allow it."""

    denied = False

    with get_connection() as connection:
        record = connection.execute(
            """
            SELECT id, owner_id, title, content, created_at
            FROM user_records
            WHERE id = %s
            """,
            (record_id,),
        ).fetchone()

        if record is not None:
            denied = record[1] != user["id"] and not has_permission(user, "records:read_any")

            if denied:
                connection.execute(
                    """
                    INSERT INTO audit_events (
                        actor_user_id, event_type, target_type,
                        target_id, ip_address
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        user["id"],
                        "record_access_denied",
                        "user_record",
                        str(record_id),
                        request.client.host if request.client else "unknown",
                    ),
                )

    if record is None or denied:
        # Return the same response to avoid revealing another user's record.
        raise HTTPException(status_code=404, detail="Record not found")

    return {
        "id": str(record[0]),
        "owner_id": str(record[1]),
        "title": record[2],
        "content": record[3],
        "created_at": record[4],
    }
