import csv
import time
from pathlib import Path

from cv_extractor.extractor import ExtractionError, extract_cv
from llm_client.config import get_settings
from llm_client.exceptions import LLMError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CV_FOLDER = PROJECT_ROOT / "sample_data" / "cvs"
RESULTS_FOLDER = PROJECT_ROOT / "results"


def run_benchmark():
    settings = get_settings()

    provider = settings.provider
    model = settings.model

    output_folder = RESULTS_FOLDER / provider
    output_folder.mkdir(parents=True, exist_ok=True)

    performance_file = output_folder / "performance.csv"

    fieldnames = [
        "cv_file",
        "provider",
        "model",
        "status",
        "duration_seconds",
        "error",
    ]

    # Preserve previous benchmark results.
    previous_rows = []

    if performance_file.exists():
        with performance_file.open(newline="", encoding="utf-8") as file:
            previous_rows = list(csv.DictReader(file))

    rows_by_cv = {
        row["cv_file"]: row
        for row in previous_rows
        if row["provider"] == provider and row["model"] == model
    }

    cv_files = [CV_FOLDER / f"cv_{number:02d}.txt" for number in range(1, 11)]

    successful = 0
    skipped = 0

    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print("Retrying only missing or failed CVs.")

    for cv_file in cv_files:
        output_file = output_folder / f"{cv_file.stem}.json"

        # Skip CVs that already have a successful result.
        if output_file.exists():
            previous = rows_by_cv.get(cv_file.name)

            if previous and previous["status"] == "SUCCESS":
                print(f"\nSkipping: {cv_file.name} (already successful)")
                successful += 1
                skipped += 1
                continue

        print(f"\nProcessing: {cv_file.name}")

        start_time = time.perf_counter()

        try:
            result = extract_cv(cv_file)

            duration = time.perf_counter() - start_time

            output_file.write_text(
                result.model_dump_json(indent=2),
                encoding="utf-8",
            )

            rows_by_cv[cv_file.name] = {
                "cv_file": cv_file.name,
                "provider": provider,
                "model": model,
                "status": "SUCCESS",
                "duration_seconds": round(duration, 2),
                "error": "",
            }

            print(f"Saved: {output_file.name}")
            print(f"Time taken: {duration:.2f} seconds")

        except (ExtractionError, LLMError, OSError) as error:
            duration = time.perf_counter() - start_time

            rows_by_cv[cv_file.name] = {
                "cv_file": cv_file.name,
                "provider": provider,
                "model": model,
                "status": "FAILED",
                "duration_seconds": round(duration, 2),
                "error": f"{type(error).__name__}: {error}",
            }

            print(f"Failed: {cv_file.name}")
            print(f"Reason: {error}")

        # Wait before sending the next API request.
        time.sleep(10)

    # Keep all previous results and update retried CVs.
    ordered_rows = [
        rows_by_cv[cv_file.name] for cv_file in cv_files if cv_file.name in rows_by_cv
    ]

    with performance_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered_rows)

    successful_count = sum(row["status"] == "SUCCESS" for row in ordered_rows)
    failed_count = sum(row["status"] == "FAILED" for row in ordered_rows)

    successful_times = [
        float(row["duration_seconds"])
        for row in ordered_rows
        if row["status"] == "SUCCESS"
    ]

    print("\n========== BENCHMARK SUMMARY ==========")
    print(f"Total CVs: {len(cv_files)}")
    print(f"Successful: {successful_count}")
    print(f"Failed: {failed_count}")
    print(f"Previously successful and skipped: {skipped}")

    if successful_times:
        print(
            f"Average successful response time: "
            f"{sum(successful_times) / len(successful_times):.2f} seconds"
        )

    print(f"Performance report: {performance_file}")


if __name__ == "__main__":
    run_benchmark()
