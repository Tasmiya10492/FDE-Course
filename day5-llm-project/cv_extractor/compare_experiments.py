import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_FOLDER = PROJECT_ROOT / "results" / "experiments"

EXPERIMENTS = [
    "temperature_0",
    "temperature_0_8",
]

RUNS = [1, 2, 3]


def load_result(experiment, run_number):
    file_path = RESULTS_FOLDER / experiment / f"run_{run_number}.json"

    if not file_path.is_file():
        raise FileNotFoundError(f"Missing file: {file_path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def compare_results(first, second):
    differences = []

    all_fields = set(first) | set(second)

    for field in sorted(all_fields):
        if first.get(field) != second.get(field):
            differences.append(field)

    return differences


def main():
    results = {}

    print("========== EXPERIMENT COMPARISON ==========")

    for experiment in EXPERIMENTS:
        print(f"\nExperiment: {experiment}")

        runs = {run_number: load_result(experiment, run_number) for run_number in RUNS}

        results[experiment] = runs

        baseline = runs[1]

        for run_number in RUNS[1:]:
            differences = compare_results(
                baseline,
                runs[run_number],
            )

            if differences:
                print(f"Run 1 vs Run {run_number}: Different fields: {differences}")
            else:
                print(f"Run 1 vs Run {run_number}: Identical extracted data")

    print("\n========== TEMPERATURE COMPARISON ==========")

    low_temperature = results["temperature_0"][1]
    high_temperature = results["temperature_0_8"][1]

    differences = compare_results(
        low_temperature,
        high_temperature,
    )

    if differences:
        print("Fields that changed:", differences)
    else:
        print("Both experiments produced identical extracted data.")

    print("\nComparison completed.")


if __name__ == "__main__":
    main()
