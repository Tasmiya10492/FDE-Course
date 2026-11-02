import csv
import time
from pathlib import Path

from cv_extractor.extractor import ExtractionError, extract_cv
from llm_client.config import get_settings
from llm_client.exceptions import LLMError

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CV_FILE = PROJECT_ROOT / "sample_data" / "cvs" / "cv_01.txt"
RESULTS_FOLDER = PROJECT_ROOT / "results" / "experiments"

FIXED_SEED = 42
RUNS_PER_TEMPERATURE = 3

EXPERIMENTS = [
    {
        "name": "temperature_0",
        "temperature": 0.0,
    },
    {
        "name": "temperature_0_8",
        "temperature": 0.8,
    },
]


def run_experiments():
    settings = get_settings()

    if settings.provider != "ollama":
        raise ValueError(
            "These experiments must be run with Ollama. Please update your .env configuration."
        )

    if not CV_FILE.is_file():
        raise FileNotFoundError(f"CV file not found: {CV_FILE}")

    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

    report_rows = []

    print("========== TEMPERATURE AND SEED EXPERIMENT ==========")
    print(f"Provider: {settings.provider}")
    print(f"Model: {settings.model}")
    print(f"CV: {CV_FILE.name}")
    print(f"Fixed seed: {FIXED_SEED}")

    for experiment in EXPERIMENTS:
        experiment_name = experiment["name"]
        temperature = experiment["temperature"]

        output_folder = RESULTS_FOLDER / experiment_name
        output_folder.mkdir(parents=True, exist_ok=True)

        print(f"\nExperiment: {experiment_name}")
        print(f"Temperature: {temperature}")

        for run_number in range(1, RUNS_PER_TEMPERATURE + 1):
            output_file = output_folder / f"run_{run_number}.json"

            print(f"\nRunning {experiment_name}, run {run_number}...")

            start_time = time.perf_counter()

            try:
                result = extract_cv(
                    CV_FILE,
                    temperature=temperature,
                    seed=FIXED_SEED,
                )

                duration = time.perf_counter() - start_time

                output_file.write_text(
                    result.model_dump_json(indent=2),
                    encoding="utf-8",
                )

                status = "SUCCESS"
                error_message = ""

                print(f"Saved: {output_file.name}")
                print(f"Time taken: {duration:.2f} seconds")

            except (ExtractionError, LLMError, OSError) as error:
                duration = time.perf_counter() - start_time

                status = "FAILED"
                error_message = str(error)

                print(f"Failed: {error_message}")

            report_rows.append(
                {
                    "experiment": experiment_name,
                    "temperature": temperature,
                    "seed": FIXED_SEED,
                    "run": run_number,
                    "status": status,
                    "duration_seconds": round(duration, 2),
                    "error": error_message,
                }
            )

    report_file = RESULTS_FOLDER / "experiment_report.csv"

    with report_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        fieldnames = [
            "experiment",
            "temperature",
            "seed",
            "run",
            "status",
            "duration_seconds",
            "error",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_rows)

    successful = sum(row["status"] == "SUCCESS" for row in report_rows)

    failed = len(report_rows) - successful

    print("\n========== EXPERIMENT SUMMARY ==========")
    print(f"Total runs: {len(report_rows)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Report saved: {report_file}")


if __name__ == "__main__":
    run_experiments()
