import json
from pathlib import Path

import tiktoken

OUTPUT_FILE = Path("results/token_counts.json")

TEXTS = {
    "prose": "Employees can apply for annual leave through the HR portal.",
    "code": """
def apply_leave(employee_name, days):
    return f"{employee_name} applied for {days} days"
""",
    "json": """
{
    "employee": "John",
    "leave_type": "Annual",
    "days": 5
}
""",
    "english": "Employees must submit their leave requests before the deadline.",
    "hindi": "कर्मचारी छुट्टी के लिए आवेदन कर सकते हैं।",
    "french": "Les employés peuvent demander un congé annuel.",
}


def count_tokens(text, encoding):
    return len(encoding.encode(text))


def main():
    encoding = tiktoken.get_encoding("cl100k_base")

    results = {}

    for text_type, text in TEXTS.items():
        results[text_type] = {
            "character_count": len(text),
            "token_count": count_tokens(text, encoding),
        }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(json.dumps(results, indent=4, ensure_ascii=False), encoding="utf-8")

    for text_type, details in results.items():
        print(
            f"{text_type}: "
            f"{details['character_count']} characters, "
            f"{details['token_count']} tokens"
        )


if __name__ == "__main__":
    main()
