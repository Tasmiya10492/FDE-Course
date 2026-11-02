from pathlib import Path

from cv_extractor.extractor import ExtractionError, extract_cv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CV_FOLDER = PROJECT_ROOT / "sample_data" / "cvs"
RESULTS_FOLDER = PROJECT_ROOT / "results"


def process_all_cvs():
    """Extract information from every CV and save JSON results."""

    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

    cv_files = sorted(CV_FOLDER.glob("cv_*.txt"))

    if not cv_files:
        print("No CV files found.")
        return

    successful = 0
    failed = 0

    for cv_file in cv_files:
        print(f"\nProcessing: {cv_file.name}")

        try:
            result = extract_cv(cv_file)

            output_file = RESULTS_FOLDER / f"{cv_file.stem}.json"

            output_file.write_text(
                result.model_dump_json(indent=2),
                encoding="utf-8",
            )

            print(f"Saved: {output_file.name}")
            successful += 1

        except (ExtractionError, FileNotFoundError, ValueError) as error:
            print(f"Failed: {cv_file.name}")
            print(f"Reason: {error}")
            failed += 1

    print("\n========== BATCH SUMMARY ==========")
    print(f"Total CVs: {len(cv_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Results folder: {RESULTS_FOLDER}")


if __name__ == "__main__":
    process_all_cvs()
