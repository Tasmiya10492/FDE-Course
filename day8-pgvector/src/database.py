"""PostgreSQL connection management."""

import psycopg
from pgvector.psycopg import register_vector

from src.config import get_settings


def get_connection() -> psycopg.Connection:
    """Create and return a PostgreSQL connection."""
    settings = get_settings()

    connection = psycopg.connect(settings.database_url)
    register_vector(connection)

    return connection


def check_connection() -> bool:
    """Check whether PostgreSQL is reachable."""
    with get_connection() as connection:
        result = connection.execute("SELECT 1").fetchone()

    return result == (1,)
