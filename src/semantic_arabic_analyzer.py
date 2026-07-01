import re
from pathlib import Path
from typing import Any

from sentence_transformers import SentenceTransformer, util

from checklist import load_checklist, get_total_weight


CONTRACT_PATH = Path("data/sample_contracts/sample_arabic_contract.txt")

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

COMPLIANT_THRESHOLD = 0.62
PARTIAL_THRESHOLD = 0.48


def read_contract(path: Path) -> str:
    """
    Read Arabic contract text from a TXT file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Contract file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return file.read()


def split_contract_into_clauses(contract_text: str) -> list[str]:
    """
    Split Arabic contract into smaller clauses/paragraphs.
    """
    # نقسم على السطور الفارغة أو النقاط أو الفواصل الطويلة
    raw_parts = re.split(r"\n+|\.|؛", contract_text)

    clauses = []

    for part in raw_parts:
        cleaned = part.strip()
        if len(cleaned) >= 20:
            clauses.append(cleaned)

    return clauses


def build_requirement_query(requirement: dict[str, Any]) -> str:
    """
    Build a semantic Arabic query for each requirement.
    """
    keywords = "، ".join(requirement["keywords_ar"])

    return (
        f"{requirement['name_ar']}. "
        f"{requirement['description_ar']} "
        f"معيار التحقق: {requirement['pass_criteria_ar']} "
        f"كلمات مرتبطة: {keywords}"
    )


def analyze_requirement_semantic(
    requirement: dict[str, Any],
    clauses: list[str],
    model: SentenceTransformer,
    clause_embeddings
) -> dict[str, Any]:
    """
    Analyze one requirement using hybrid semantic similarity + Arabic keywords.
    """
    requirement_query = build_requirement_query(requirement)
    requirement_embedding = model.encode(requirement_query, convert_to_tensor=True)

    similarities = util.cos_sim(requirement_embedding, clause_embeddings)[0]

    best_index = int(similarities.argmax())
    best_score = float(similarities[best_index])
    best_clause = clauses[best_index]

    keywords = requirement["keywords_ar"]
    matched_keywords = []

    for keyword in keywords:
        if keyword in best_clause:
            matched_keywords.append(keyword)

    keyword_count = len(matched_keywords)

    # Hybrid decision:
    # 1. High semantic similarity + at least 1 keyword = Compliant
    # 2. Medium semantic similarity + at least 1 keyword = Partial
    # 3. Very high semantic similarity without keyword = Partial only
    # 4. Otherwise Missing

    if best_score >= COMPLIANT_THRESHOLD and keyword_count >= 1:
        status = "Compliant"
        score = requirement["weight"]

    elif best_score >= 0.55 and keyword_count >= 2:
        status = "Compliant"
        score = requirement["weight"]

    elif best_score >= PARTIAL_THRESHOLD and keyword_count >= 1:
        status = "Partial"
        score = requirement["weight"] * 0.5

    elif best_score >= 0.70:
        status = "Partial"
        score = requirement["weight"] * 0.5

    else:
        status = "Missing"
        score = 0

    return {
        "id": requirement["id"],
        "name_ar": requirement["name_ar"],
        "risk_level": requirement["risk_level"],
        "weight": requirement["weight"],
        "status": status,
        "score": score,
        "similarity": round(best_score, 3),
        "best_clause": best_clause,
        "matched_keywords": matched_keywords,
        "recommendation": requirement["recommended_clause_ar"]
    }


def analyze_contract_semantic(contract_path: Path) -> None:
    """
    Analyze Arabic contract using semantic similarity.
    """
    checklist = load_checklist()
    contract_text = read_contract(contract_path)
    clauses = split_contract_into_clauses(contract_text)

    if not clauses:
        raise ValueError("No valid clauses found in the contract.")

    print(f"عدد فقرات العقد المستخرجة: {len(clauses)}")
    print("تحميل مودل المعاني...")
    model = SentenceTransformer(MODEL_NAME)

    print("تحويل فقرات العقد إلى embeddings...")
    clause_embeddings = model.encode(clauses, convert_to_tensor=True)

    total_weight = get_total_weight(checklist)
    achieved_score = 0
    results = []

    for requirement in checklist:
        result = analyze_requirement_semantic(
            requirement=requirement,
            clauses=clauses,
            model=model,
            clause_embeddings=clause_embeddings
        )
        results.append(result)
        achieved_score += result["score"]

    compliance_percentage = (achieved_score / total_weight) * 100

    print("\nنتيجة تحليل العقد بالمعنى")
    print("=" * 80)
    print(f"الدرجة: {achieved_score} / {total_weight}")
    print(f"نسبة الامتثال: {compliance_percentage:.2f}%")
    print("=" * 80)

    for result in results:
        print(
            f"{result['id']} | {result['status']} | "
            f"{result['score']}/{result['weight']} | "
            f"Similarity: {result['similarity']} | {result['name_ar']}"
        )

        print("أفضل فقرة مطابقة:")
        print(result["best_clause"])
        if result["matched_keywords"]:
          print(f"كلمات داعمة: {', '.join(result['matched_keywords'])}")
        else:
          print("كلمات داعمة: لا يوجد")

        if result["status"] == "Missing":
            print("التوصية:")
            print(result["recommendation"])

        print("-" * 80)


if __name__ == "__main__":
    analyze_contract_semantic(CONTRACT_PATH)