"""Tests for tenant and role access validation."""

from typing import cast

import pytest
from src.access_control import validate_access_context


def test_valid_access_context() -> None:
    """Accept a valid tenant and role context."""
    validate_access_context("tenant_a", ["HR", "Employee"])


def test_rejects_empty_tenant() -> None:
    """Reject a missing tenant."""
    with pytest.raises(ValueError, match="tenant_id"):
        validate_access_context("", ["HR"])


def test_rejects_empty_roles() -> None:
    """Reject a user without roles."""
    with pytest.raises(ValueError, match="role"):
        validate_access_context("tenant_a", [])


def test_rejects_blank_role() -> None:
    """Reject blank role names."""
    with pytest.raises(ValueError, match="non-empty"):
        validate_access_context("tenant_a", ["HR", " "])


def test_rejects_non_string_role() -> None:
    """Reject invalid role values."""
    invalid_roles = cast(list[str], ["HR", None])

    with pytest.raises(ValueError, match="non-empty"):
        validate_access_context("tenant_a", invalid_roles)
