from pathlib import Path


def read_document(file_path: str | Path) -> str:
    """Read a text document and return its contents."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CV file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Expected a file, but received: {path}")

    return path.read_text(encoding="utf-8").strip()
