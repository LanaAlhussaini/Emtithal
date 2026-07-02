from pathlib import Path
import json
from src.semantic_arabic_analyzer import analyze_contract_semantic, OUTPUT_PATH
from src.rag_retriever import retrieve_sama_evidence


def run_pipeline(contract_path: str | Path) -> dict:
    contract_path = Path(contract_path)
    print("Analyzing uploaded file:", contract_path)

    analyze_contract_semantic(contract_path)

    with OUTPUT_PATH.open("r", encoding="utf-8") as file:
        result = json.load(file)

    for item in result["results"]:
        query = f"{item['name_ar']} {item.get('recommendation', '')}"
        try:
            item["sama_evidence"] = retrieve_sama_evidence(query, top_k=2)
        except Exception:
            item["sama_evidence"] = []

    return result