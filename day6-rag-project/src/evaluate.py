import json
from pathlib import Path

from src.rag import retrieve_context


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_FOLDER = PROJECT_ROOT / "results"


QUESTIONS = [
    {
        "question": "Who is eligible for annual leave?",
        "expected_policy": "HR001",
    },
    {
        "question": "How many days of annual leave are employees entitled to?",
        "expected_policy": "HR002",
    },
    {
        "question": "How can employees submit an annual leave request?",
        "expected_policy": "HR003",
    },
    {
        "question": "Who reviews and approves leave requests?",
        "expected_policy": "HR004",
    },
    {
        "question": "How can an employee cancel an approved leave request?",
        "expected_policy": "HR005",
    },
    {
        "question": "What are the eligibility rules for sick leave?",
        "expected_policy": "HR006",
    },
    {
        "question": "What documents are required for sick leave?",
        "expected_policy": "HR007",
    },
    {
        "question": "How should employees request emergency leave?",
        "expected_policy": "HR008",
    },
    {
        "question": "What maternity leave provisions are available?",
        "expected_policy": "HR009",
    },
    {
        "question": "What paternity leave provisions are available?",
        "expected_policy": "HR010",
    },
]


METHODS = ["fixed", "sentence", "paragraph"]


def evaluate_retrieval():
    all_results = []

    for method in METHODS:
        print(f"\nEvaluating: {method}")

        hits = 0

        for item in QUESTIONS:
            matches = retrieve_context(
                question=item["question"],
                method=method,
                top_k=3,
            )

            retrieved_ids = [match["metadata"]["policy_id"] for match in matches]

            hit = item["expected_policy"] in retrieved_ids

            if hit:
                hits += 1

            result = {
                "method": method,
                "question": item["question"],
                "expected_policy": item["expected_policy"],
                "retrieved_policy_ids": retrieved_ids,
                "hit_at_3": hit,
            }

            all_results.append(result)

            print(f"{item['expected_policy']} | Retrieved: {retrieved_ids} | Hit@3: {hit}")

        print(f"Hit@3: {hits}/{len(QUESTIONS)}")

    output_file = RESULTS_FOLDER / "retrieval_evaluation.json"

    output_file.write_text(
        json.dumps(all_results, indent=4),
        encoding="utf-8",
    )

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    evaluate_retrieval()
