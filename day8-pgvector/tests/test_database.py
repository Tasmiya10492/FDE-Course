"""Tests for PostgreSQL connectivity."""

from src.database import check_connection


def test_database_connection() -> None:
    """Verify that the application can connect to PostgreSQL."""
    assert check_connection() is True
