"""Evaluate exact-chunk retrieval against the Day 9 golden set."""

import json
import logging
import time
from pathlib import Path

from src.retrieval import search_similar

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_PATH = PROJECT_ROOT / "data" / "day9_golden_set.json"
RESULTS_PATH = PROJECT_ROOT / "results" / "day9_retrieval_evaluation.json"
REPORT_PATH = PROJECT_ROOT / "docs" / "day9-retrieval-evaluation.md"

# This is the initial diagnostic threshold, not a universal distance rule.
INITIAL_DISTANCE_THRESHOLD = 0.40


def evaluate_question(
    question_data: dict,
    tenant_id: str,
    user_roles: list[str],
    retrieval_limit: int,
) -> dict:
    """Retrieve chunks and evaluate one golden-set question."""
    start_time = time.perf_counter()

    retrieved = search_similar(
        question=question_data["question"],
        tenant_id=tenant_id,
        user_roles=user_roles,
        limit=retrieval_limit,
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    retrieved_ids = [chunk["id"] for chunk in retrieved]
    expected_ids = question_data["expected_chunk_ids"]

    result = {
        "id": question_data["id"],
        "question": question_data["question"],
        "answerable": question_data["answerable"],
        "expected_chunk_ids": expected_ids,
        "retrieved_chunks": [
            {
                "chunk_id": chunk["id"],
                "source": chunk["source"],
                "distance": round(chunk["distance"], 4),
            }
            for chunk in retrieved
        ],
        "retrieved_chunk_ids": retrieved_ids,
        "latency_ms": round(elapsed_ms, 2),
    }

    if question_data["answerable"]:
        result["hits_at_k"] = {
            str(k): any(expected_id in retrieved_ids[:k] for expected_id in expected_ids)
            for k in (1, 3, 5)
        }
    else:
        nearest_distance = retrieved[0]["distance"] if retrieved else None
        result["nearest_distance"] = (
            round(nearest_distance, 4) if nearest_distance is not None else None
        )
        result["within_initial_distance_threshold"] = (
            nearest_distance <= INITIAL_DISTANCE_THRESHOLD
            if nearest_distance is not None
            else False
        )

    return result


def build_markdown_report(
    results: list[dict],
    metrics: dict,
    answerable_count: int,
    unanswerable_count: int,
) -> str:
    """Build a human-readable Markdown evaluation report."""
    lines = [
        "# Day 9 Retrieval Evaluation",
        "",
        "## Evaluation summary",
        "",
        f"- Total questions: {len(results)}",
        f"- Answerable questions: {answerable_count}",
        f"- Unanswerable questions: {unanswerable_count}",
        "- Metric: exact expected-chunk Recall@k",
        "",
        "## Recall results",
        "",
        "| Metric | Hits | Questions | Recall |",
        "|---|---:|---:|---:|",
    ]

    for k in (1, 3, 5):
        metric = metrics[str(k)]
        lines.append(
            f"| Recall@{k} | {metric['hits']} | {answerable_count} | {metric['recall']:.2%} |"
        )

    lines.extend(
        [
            "",
            "## Per-question results",
            "",
            "| ID | Answerable | Expected chunk | Retrieved chunks | Result |",
            "|---|---|---:|---|---|",
        ]
    )

    for result in results:
        expected = result["expected_chunk_ids"]
        retrieved = result["retrieved_chunk_ids"]

        if result["answerable"]:
            status = "Hit@5" if result["hits_at_k"]["5"] else "Miss@5"
        else:
            status = "Unanswerable - diagnostic only"

        lines.append(
            f"| {result['id']} | {result['answerable']} | {expected} | {retrieved} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Recall@k measures whether at least one expected chunk appears "
            "in the top k results for each answerable question. "
            "Unanswerable questions are excluded from the recall denominator. "
            "Their nearest distances are recorded separately as a diagnostic; "
            "retrieval distance alone does not prove that an answer is safe "
            "to provide.",
            "",
            f"The initial distance threshold used for diagnostic comparison "
            f"was {INITIAL_DISTANCE_THRESHOLD:.2f}. It should be calibrated "
            "against the evaluation results rather than treated as a "
            "universal cutoff.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    """Run the Day 9 golden-set retrieval evaluation."""
    with GOLDEN_SET_PATH.open(encoding="utf-8") as file:
        golden_set = json.load(file)

    questions = golden_set["questions"]
    tenant_id = golden_set["tenant_id"]
    user_roles = golden_set["user_roles"]
    retrieval_limit = golden_set["retrieval_limit"]

    results = [
        evaluate_question(
            question_data=question,
            tenant_id=tenant_id,
            user_roles=user_roles,
            retrieval_limit=retrieval_limit,
        )
        for question in questions
    ]

    answerable_results = [result for result in results if result["answerable"]]
    unanswerable_count = sum(not result["answerable"] for result in results)

    metrics = {}
    for k in (1, 3, 5):
        hits = sum(result["hits_at_k"][str(k)] for result in answerable_results)
        metrics[str(k)] = {
            "hits": hits,
            "total": len(answerable_results),
            "recall": (hits / len(answerable_results) if answerable_results else 0.0),
        }

    evaluation = {
        "title": golden_set["title"],
        "tenant_id": tenant_id,
        "retrieval_limit": retrieval_limit,
        "total_questions": len(results),
        "answerable_questions": len(answerable_results),
        "unanswerable_questions": unanswerable_count,
        "initial_distance_threshold_diagnostic": (INITIAL_DISTANCE_THRESHOLD),
        "metrics": metrics,
        "questions": results,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(evaluation, file, indent=2)
        file.write("\n")

    report = build_markdown_report(
        results=results,
        metrics=metrics,
        answerable_count=len(answerable_results),
        unanswerable_count=unanswerable_count,
    )
    REPORT_PATH.write_text(report, encoding="utf-8")

    logger.info("Day 9 golden-set evaluation completed.")
    logger.info("Total questions: %s", len(results))
    logger.info("Answerable: %s", len(answerable_results))
    logger.info("Unanswerable: %s", unanswerable_count)

    for k in (1, 3, 5):
        metric = metrics[str(k)]
        logger.info(
            "Recall@%s: %s/%s (%.2f%%)",
            k,
            metric["hits"],
            metric["total"],
            metric["recall"] * 100,
        )

    logger.info("JSON results: %s", RESULTS_PATH)
    logger.info("Markdown report: %s", REPORT_PATH)


if __name__ == "__main__":
    main()
