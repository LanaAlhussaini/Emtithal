import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REGULATIONS_DIR = Path("data/regulations")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "regulations_pages.json"


DOCUMENT_NAMES = {
    "outsourcing_instructions.pdf": "SAMA Outsourcing Instructions",
    "cyber_security_framework.pdf": "SAMA Cyber Security Framework",
    "central_bank_law.pdf": "Saudi Central Bank Law",
    "aml_ctf_guide.pdf": "SAMA AML/CTF Guide"
}


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """
    if not text:
        return ""

    text = text.replace("\u200f", " ")
    text = text.replace("\u200e", " ")
    text = text.replace("\xa0", " ")

    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text


def extract_pdf_pages(pdf_path: Path) -> list[dict[str, Any]]:
    """
    Extract text page by page from a PDF file.
    """
    reader = PdfReader(str(pdf_path))
    document_title = DOCUMENT_NAMES.get(pdf_path.name, pdf_path.stem)

    pages = []

    for page_index, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text()
        cleaned_text = clean_text(raw_text)

        if cleaned_text:
            pages.append(
                {
                    "source_file": pdf_path.name,
                    "source_title": document_title,
                    "page_number": page_index,
                    "text": cleaned_text
                }
            )

    return pages


def extract_all_regulations() -> list[dict[str, Any]]:
    """
    Extract all PDFs inside data/regulations.
    """
    all_pages = []

    pdf_files = list(REGULATIONS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF files found in data/regulations. "
            "Please add the SAMA PDF files first."
        )

    for pdf_file in pdf_files:
        print(f"Extracting: {pdf_file.name}")
        pages = extract_pdf_pages(pdf_file)
        print(f"Extracted {len(pages)} pages from {pdf_file.name}")
        all_pages.extend(pages)

    return all_pages


def save_pages(pages: list[dict[str, Any]]) -> None:
    """
    Save extracted pages into a JSON file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(pages, file, ensure_ascii=False, indent=2)

    print(f"Saved extracted pages to: {OUTPUT_FILE}")


def main() -> None:
    pages = extract_all_regulations()
    save_pages(pages)

    print("-" * 60)
    print("Text extraction completed successfully.")
    print(f"Total extracted pages: {len(pages)}")


if __name__ == "__main__":
    main()