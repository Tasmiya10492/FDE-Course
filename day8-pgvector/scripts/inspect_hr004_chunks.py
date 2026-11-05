"""Inspect the stored HR004 passages for the Day 9 retrieval diagnostic."""

import logging

from src.database import get_connection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Display chunks 107 and 108 from the evaluation tenant."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, source, content
            FROM document_chunks
            WHERE tenant_id = %s
              AND source = %s
              AND id IN (%s, %s)
            ORDER BY id
            """,
            ("tenant_eval", "HR004.txt", 107, 108),
        ).fetchall()

    for chunk_id, source, content in rows:
        logger.info("\nChunk ID: %s", chunk_id)
        logger.info("Source: %s", source)
        logger.info("Content:\n%s", content)


if __name__ == "__main__":
    main()
