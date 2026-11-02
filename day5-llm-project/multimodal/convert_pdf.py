from pathlib import Path

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILE = (
    PROJECT_ROOT
    / "sample_data"
    / "multimodal_assets"
    / "day5_samples"
    / "scanned_page"
    / "invoice_scan.pdf"
)

OUTPUT_FOLDER = PDF_FILE.parent


def convert_pdf_to_images(pdf_path: Path) -> list[Path]:
    """Convert every PDF page into a PNG image."""

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_paths = []

    with pymupdf.open(pdf_path) as document:
        print(f"PDF pages: {len(document)}")

        for page_number, page in enumerate(document, start=1):
            # Render at 2x resolution for better text readability.
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False,
            )

            output_file = OUTPUT_FOLDER / f"invoice_scan_page_{page_number}.png"

            pixmap.save(output_file)
            output_paths.append(output_file)

            print(f"Saved: {output_file.name}")

    return output_paths


def main() -> None:
    images = convert_pdf_to_images(PDF_FILE)

    print(f"\nSuccessfully converted {len(images)} PDF page(s).")


if __name__ == "__main__":
    main()
