"""PostgreSQL connection management."""

import os

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()


def get_connection() -> psycopg.Connection:
    """Create and return a PostgreSQL connection."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not configured")

    connection = psycopg.connect(database_url)
    register_vector(connection)

    return connection


def check_connection() -> bool:
    """Check whether PostgreSQL is reachable."""
    with get_connection() as connection:
        result = connection.execute("SELECT 1").fetchone()

    return result == (1,)
