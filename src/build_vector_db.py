import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = Path("data/processed/regulations_chunks.json")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "sama_regulations"


def load_chunks():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            "regulations_chunks.json not found. Run src/chunk_text.py first."
        )

    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_vector_database():
    chunks = load_chunks()

    print(f"Loaded chunks: {len(chunks)}")

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["text"])
        metadatas.append(
            {
                "source_file": chunk["source_file"],
                "source_title": chunk["source_title"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"]
            }
        )

    print("Creating embeddings...")
    embeddings = model.encode(documents).tolist()

    print("Adding chunks to ChromaDB...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print("Vector database created successfully.")
    print(f"Collection name: {COLLECTION_NAME}")
    print(f"Stored chunks: {collection.count()}")


if __name__ == "__main__":
    build_vector_database()