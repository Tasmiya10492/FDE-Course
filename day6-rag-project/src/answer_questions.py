import json
from pathlib import Path

from src.evaluate import QUESTIONS
from src.rag import answer_question


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_FOLDER = PROJECT_ROOT / "results"

# Change this after reviewing the retrieval comparison.
CHOSEN_METHOD = "paragraph"


def generate_answers():
    all_answers = []

    for index, item in enumerate(QUESTIONS, start=1):
        print(f"\nQuestion {index}/10")
        print(item["question"])

        result = answer_question(
            question=item["question"],
            method=CHOSEN_METHOD,
            top_k=3,
        )

        answer_record = {
            "question": result["question"],
            "answer": result["answer"],
            "retrieved_policy_ids": [
                match["metadata"]["policy_id"] for match in result["retrieved_chunks"]
            ],
            "retrieved_chunks": [match["document"] for match in result["retrieved_chunks"]],
        }

        all_answers.append(answer_record)

        print("\nAnswer:")
        print(result["answer"])

    output_file = RESULTS_FOLDER / "rag_answers.json"

    output_file.write_text(
        json.dumps(all_answers, indent=4),
        encoding="utf-8",
    )

    print(f"\nAnswers saved to: {output_file}")


if __name__ == "__main__":
    generate_answers()
