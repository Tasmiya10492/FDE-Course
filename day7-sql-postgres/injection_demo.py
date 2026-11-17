import logging
import os

import psycopg

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def vulnerable_search(conn, username):
    # Intentionally vulnerable: this demonstrates SQL injection.
    query = f"SELECT id, username, role FROM demo_users WHERE username = '{username}'"  # noqa: S608

    return conn.execute(query).fetchall()


def safe_search(conn, username):
    query = """
        SELECT id, username, role
        FROM demo_users
        WHERE username = %s
    """
    return conn.execute(query, (username,)).fetchall()


def upsert_user(conn, username, role):
    query = """
        INSERT INTO demo_users (username, role)
        VALUES (%s, %s)
        ON CONFLICT (username)
        DO UPDATE SET role = EXCLUDED.role
    """
    conn.execute(query, (username, role))


def main():
    database_url = os.environ["DATABASE_URL"]

    with psycopg.connect(database_url) as conn:
        upsert_user(conn, "alice", "employee")
        upsert_user(conn, "bob", "manager")
        upsert_user(conn, "admin", "administrator")

        logger.info("Normal search:")
        logger.info("%s", vulnerable_search(conn, "alice"))

        malicious_input = "' OR '1'='1' --"

        logger.info("\nSQL injection using vulnerable query:")
        logger.info("%s", vulnerable_search(conn, malicious_input))

        logger.info("\nSame input using parameterised query:")
        logger.info("%s", safe_search(conn, malicious_input))

        logger.info("\nUpsert completed successfully.")


if __name__ == "__main__":
    main()
