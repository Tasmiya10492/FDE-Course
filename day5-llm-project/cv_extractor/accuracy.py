import csv
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CV_FOLDER = PROJECT_ROOT / "sample_data" / "cvs"
RESULTS_FOLDER = PROJECT_ROOT / "results"

FIELDS = [
    "full_name",
    "email",
    "phone",
    "location",
    "summary",
    "skills",
    "experience",
    "education",
]


def get_section(lines, heading):
    """Return the text between a heading and the next section heading."""

    headings = {"SUMMARY", "SKILLS", "EXPERIENCE", "EDUCATION"}

    try:
        start = lines.index(heading) + 1
    except ValueError:
        raise ValueError(f"Missing section: {heading}")

    section_lines = []

    for line in lines[start:]:
        if line in headings:
            break
        if line.strip():
            section_lines.append(line.strip())

    return section_lines


def parse_year(value):
    """Convert a year to an integer, or return None for Present."""

    if value.strip().lower() in ("present", "current"):
        return None

    return int(value)


def read_expected_cv(file_path):
    """Read a CV and convert its contents into the expected JSON structure."""

    lines = [
        line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()
    ]

    lines = [line for line in lines if line]

    if not lines:
        raise ValueError(f"Empty CV: {file_path.name}")

    expected = {
        "full_name": lines[0],
        "email": None,
        "phone": None,
        "location": None,
    }

    # Read contact details.
    for line in lines:
        if line.startswith("Email:"):
            expected["email"] = line.split(":", 1)[1].strip()

        elif line.startswith("Phone:"):
            expected["phone"] = line.split(":", 1)[1].strip()

        elif line.startswith("Location:"):
            expected["location"] = line.split(":", 1)[1].strip()

    # Read summary.
    summary_lines = get_section(lines, "SUMMARY")
    expected["summary"] = " ".join(summary_lines) if summary_lines else None

    # Read skills.
    skills_lines = get_section(lines, "SKILLS")
    expected["skills"] = [
        skill.strip()
        for line in skills_lines
        for skill in line.split(",")
        if skill.strip()
    ]

    # Read experience.
    experience_lines = get_section(lines, "EXPERIENCE")
    expected["experience"] = []

    for line in experience_lines:
        match = re.fullmatch(
            r"-\s*(.+?),\s*(.+?),\s*(\d{4}|Present|Current)"
            r"\s+to\s+(\d{4}|Present|Current)",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            raise ValueError(
                f"Could not understand experience entry in {file_path.name}: {line}"
            )

        job_title, company, start_year, end_year = match.groups()

        expected["experience"].append(
            {
                "job_title": job_title.strip(),
                "company": company.strip(),
                "start_year": parse_year(start_year),
                "end_year": parse_year(end_year),
            }
        )

    # Read education.
    education_lines = get_section(lines, "EDUCATION")

    if education_lines:
        education_match = re.fullmatch(
            r"-\s*(.+?),\s*graduated\s+(\d{4})",
            education_lines[0],
            flags=re.IGNORECASE,
        )

        if not education_match:
            raise ValueError(
                f"Could not understand education entry in {file_path.name}: {education_lines[0]}"
            )

        degree, graduation_year = education_match.groups()

        expected["education"] = {
            "degree": degree.strip(),
            "graduation_year": int(graduation_year),
        }
    else:
        expected["education"] = None

    return expected


def normalize(value):
    """Normalize values before comparing them."""

    if isinstance(value, str):
        return " ".join(value.split()).casefold()

    if isinstance(value, list):
        return [normalize(item) for item in value]

    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items()}

    return value


def display_value(value):
    """Convert lists and dictionaries into readable CSV values."""

    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)

    return "" if value is None else str(value)


def main():
    rows = []
    errors = []

    for number in range(1, 11):
        cv_name = f"cv_{number:02d}"
        cv_file = CV_FOLDER / f"{cv_name}.txt"
        json_file = RESULTS_FOLDER / "ollama" / f"{cv_name}.json"

        if not cv_file.is_file():
            errors.append(f"Missing original CV: {cv_file.name}")
            continue

        if not json_file.is_file():
            errors.append(f"Missing extracted JSON: {json_file.name}")
            continue

        try:
            expected = read_expected_cv(cv_file)
            extracted = json.loads(json_file.read_text(encoding="utf-8"))

            for field in FIELDS:
                expected_value = expected.get(field)
                extracted_value = extracted.get(field)

                correct = normalize(expected_value) == normalize(extracted_value)

                rows.append(
                    {
                        "cv_file": cv_file.name,
                        "field": field,
                        "expected_value": display_value(expected_value),
                        "extracted_value": display_value(extracted_value),
                        "correct": str(correct).upper(),
                    }
                )

        except (ValueError, json.JSONDecodeError) as error:
            errors.append(f"{cv_name}: {error}")

    if errors:
        print("Could not complete the evaluation:")
        for error in errors:
            print(f"- {error}")
        print("\nPlease review these CVs before trusting the accuracy report.")
        return

    output_file = RESULTS_FOLDER / "ollama" / "accuracy.csv"

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "cv_file",
                "field",
                "expected_value",
                "extracted_value",
                "correct",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    checked = len(rows)
    correct_count = sum(row["correct"] == "TRUE" for row in rows)
    incorrect_count = checked - correct_count

    print("\n========== ACCURACY REPORT ==========")
    print(f"CVs evaluated: {checked // len(FIELDS)}")
    print(f"Fields checked: {checked}")
    print(f"Correct fields: {correct_count}")
    print(f"Incorrect fields: {incorrect_count}")

    if checked:
        print(f"Accuracy: {correct_count / checked * 100:.2f}%")

    print(f"\nAccuracy CSV saved to: {output_file}")

    if incorrect_count:
        print("\nFields needing manual review:")

        for row in rows:
            if row["correct"] == "FALSE":
                print(f"- {row['cv_file']} | {row['field']}")


if __name__ == "__main__":
    main()
