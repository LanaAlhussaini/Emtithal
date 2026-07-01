import json
from pathlib import Path
from typing import Any


INPUT_FILE = Path("data/processed/regulations_pages.json")
OUTPUT_FILE = Path("data/processed/regulations_chunks.json")


CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def load_pages() -> list[dict[str, Any]]:
    """
    Load extracted regulation pages.
    """
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "regulations_pages.json not found. "
            "Run py src/extract_text.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks by characters.
    """
    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0

        if start >= text_length:
            break

    return chunks


def create_chunks(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Convert page-level text into smaller chunks.
    """
    all_chunks = []

    for page in pages:
        page_chunks = split_text(page["text"])

        for chunk_index, chunk_text in enumerate(page_chunks, start=1):
            chunk_id = (
                f"{page['source_file'].replace('.pdf', '')}"
                f"_p{page['page_number']}_c{chunk_index}"
            )

            all_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "source_file": page["source_file"],
                    "source_title": page["source_title"],
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                    "text": chunk_text
                }
            )

    return all_chunks


def save_chunks(chunks: list[dict[str, Any]]) -> None:
    """
    Save chunks to JSON.
    """
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    print(f"Saved chunks to: {OUTPUT_FILE}")


def main() -> None:
    pages = load_pages()
    chunks = create_chunks(pages)
    save_chunks(chunks)

    print("-" * 60)
    print("Chunking completed successfully.")
    print(f"Total pages: {len(pages)}")
    print(f"Total chunks: {len(chunks)}")

    print("-" * 60)
    print("Sample chunk:")
    print(chunks[0]["chunk_id"])
    print(chunks[0]["source_title"])
    print(f"Page: {chunks[0]['page_number']}")
    print(chunks[0]["text"][:500])


if __name__ == "__main__":
    main()