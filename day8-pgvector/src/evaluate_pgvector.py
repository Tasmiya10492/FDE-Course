"""Evaluate pgvector retrieval using the Day 6 HR policy questions."""

import json
import logging
from pathlib import Path
from time import perf_counter

from src.retrieval import search_similar

logger = logging.getLogger(__name__)

QUESTIONS = [
    ("Who is eligible for annual leave?", "HR001"),
    ("How many days of annual leave are employees entitled to?", "HR002"),
    ("How can employees submit an annual leave request?", "HR003"),
    ("Who reviews and approves leave requests?", "HR004"),
    ("How can an employee cancel an approved leave request?", "HR005"),
    ("What are the eligibility rules for sick leave?", "HR006"),
    ("What documents are required for sick leave?", "HR007"),
    ("How should employees request emergency leave?", "HR008"),
    ("What maternity leave provisions are available?", "HR009"),
    ("What paternity leave provisions are available?", "HR010"),
]


def main() -> None:
    """Run the retrieval evaluation and save its results."""
    results = []
    hits = 0

    for question, expected_policy in QUESTIONS:
        start = perf_counter()

        retrieved = search_similar(
            question=question,
            tenant_id="tenant_eval",
            user_roles=["HR"],
            limit=3,
        )

        elapsed = perf_counter() - start

        retrieved_policies = []

        for result in retrieved:
            source = result["source"]

            if not isinstance(source, str):
                raise TypeError("Retrieved source must be a string")

            retrieved_policies.append(Path(source).stem)

        hit = expected_policy in retrieved_policies

        if hit:
            hits += 1

        results.append(
            {
                "question": question,
                "expected_policy": expected_policy,
                "retrieved_policies": retrieved_policies,
                "hit_at_3": hit,
                "retrieval_time_seconds": round(elapsed, 4),
            }
        )

        logger.info(
            "%s: %s | Retrieved: %s | Time: %.4fs",
            expected_policy,
            "HIT" if hit else "MISS",
            retrieved_policies,
            elapsed,
        )

    summary = {
        "database": "pgvector",
        "tenant_id": "tenant_eval",
        "chunking_method": "paragraph",
        "total_questions": len(QUESTIONS),
        "hits_at_3": hits,
        "hit_at_3_percentage": round(hits / len(QUESTIONS) * 100, 2),
        "results": results,
    }

    output_path = Path("results/pgvector_evaluation.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    logger.info("Evaluation summary")
    logger.info("Hits: %s/%s", hits, len(QUESTIONS))
    logger.info("Hit@3: %s%%", summary["hit_at_3_percentage"])
    logger.info("Saved to: %s", output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
