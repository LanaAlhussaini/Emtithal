import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "sama_regulations"

# Multilingual model: supports Arabic and English queries
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def get_model() -> SentenceTransformer:
    """
    Load the multilingual embedding model.
    This model supports Arabic and English semantic search.
    """
    return SentenceTransformer(MODEL_NAME)


def get_collection():
    """
    Connect to the local ChromaDB collection.
    Make sure you run build_vector_db.py first.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(name=COLLECTION_NAME)


def retrieve_sama_evidence(query: str, top_k: int = 3) -> list[dict]:
    """
    Retrieve the most relevant SAMA regulation chunks for a given query.

    Args:
        query: Arabic or English search query.
        top_k: Number of relevant chunks to retrieve.

    Returns:
        A list of retrieved evidence chunks with text, metadata, and distance.
    """
    model = get_model()
    query_embedding = model.encode([query]).tolist()[0]

    collection = get_collection()

    if collection.count() == 0:
        raise ValueError(
            "ChromaDB collection is empty. "
            "Run: py src/build_vector_db.py first."
        )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved = []

    for i in range(len(results["ids"][0])):
        retrieved.append(
            {
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            }
        )

    return retrieved


def print_results(query: str, top_k: int = 3) -> None:
    """
    Print retrieved results in Arabic-friendly format.
    """
    results = retrieve_sama_evidence(query, top_k=top_k)

    print(f"الاستعلام: {query}")
    print("=" * 80)

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print(f"النتيجة رقم: {index}")
        print(f"المصدر: {metadata.get('source_title', 'غير متوفر')}")
        print(f"الملف: {metadata.get('source_file', 'غير متوفر')}")
        print(f"رقم الصفحة: {metadata.get('page_number', 'غير متوفر')}")
        print(f"رقم المقطع: {result['chunk_id']}")
        print(f"المسافة: {result['distance']}")
        print("-" * 80)
        print(result["text"][:1200])
        print("=" * 80)


if __name__ == "__main__":
    test_query = "حق التدقيق والوصول إلى السجلات في عقود إسناد المهام لطرف ثالث"
    print_results(test_query, top_k=3)