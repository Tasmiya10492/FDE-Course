"""Central role-based access control for Day 16."""

from typing import Annotated

from fastapi import Depends, HTTPException

from src.auth_routes import get_current_user

ROLE_PERMISSIONS = {
    "employee": {
        "records:create",
        "records:read_own",
    },
    "line_manager": {
        "records:create",
        "records:read_own",
    },
    "hr_administrator": {
        "records:create",
        "records:read_own",
        "records:read_any",
    },
}


def has_permission(user: dict, permission: str) -> bool:
    """Check permissions centrally using the user's database role."""
    return permission in ROLE_PERMISSIONS.get(user["role"], set())


def require_permission(permission: str):
    """Create a FastAPI dependency enforcing a named permission."""

    def check_permission(
        user: Annotated[dict, Depends(get_current_user)],
    ) -> dict:
        if not has_permission(user, permission):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action.",
            )
        return user

    return check_permission


def validate_access_context(
    tenant_id: str,
    user_roles: list[str],
) -> None:
    """Reject missing or invalid tenant and role information."""
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("A valid tenant_id is required")

    if not user_roles:
        raise ValueError("At least one user role is required")

    if any(not isinstance(role, str) or not role.strip() for role in user_roles):
        raise ValueError("User roles must be non-empty strings")
