"""Validate the tenant and role context used for document access."""


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
