"""Inspect exact chunk retrieval for the proposed Day 9 golden questions."""

import logging

from src.retrieval import search_similar

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

QUESTIONS = [
    ("Who is eligible to apply for annual leave?", 86),
    ("What factors determine the number of annual leave days?", 94),
    ("What information must an annual leave request include?", 101),
    ("What factors does a manager consider when reviewing leave?", 108),
    ("How should an employee cancel approved leave?", 115),
    ("What determines sick leave eligibility?", 122),
    ("When may an employee need to submit medical documentation for sick leave?", 129),
    ("Under what circumstances can emergency leave be requested?", 136),
    ("What should employees contact HR to understand about maternity leave?", 144),
    ("What dates should a paternity leave request include?", 152),
    ("When may an employee request unpaid leave?", 157),
    ("Where should employees check public holiday dates?", 165),
]


def main() -> None:
    """Print the top five retrieved chunks for each golden question."""
    hits = 0

    for question, expected_id in QUESTIONS:
        results = search_similar(
            question=question,
            tenant_id="tenant_eval",
            user_roles=["HR"],
            limit=5,
        )

        retrieved_ids = [result["id"] for result in results]
        hit = expected_id in retrieved_ids
        hits += int(hit)

        logger.info("\nQuestion: %s", question)
        logger.info("Expected chunk: %s", expected_id)
        logger.info("Retrieved chunks: %s", retrieved_ids)
        logger.info("Expected chunk found: %s", "YES" if hit else "NO")

        for result in results:
            logger.info(
                "  ID=%s | %s | distance=%.4f",
                result["id"],
                result["source"],
                result["distance"],
            )

    logger.info("\nExact chunk hits: %s/%s", hits, len(QUESTIONS))
    logger.info("Recall@5: %.2f%%", hits / len(QUESTIONS) * 100)


if __name__ == "__main__":
    main()
