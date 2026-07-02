import json
from pyexpat import model
import unicodedata
from pypdf import PdfReader
import re
from pathlib import Path
from typing import Any

from sentence_transformers import SentenceTransformer, util

from src.checklist import load_checklist, get_total_weight


CONTRACT_PATH = Path("data/contracts/sample_arabic_contract.pdf")
OUTPUT_PATH = Path("data/analysis_result.json")

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def normalize_arabic_text(text: str) -> str:
    """
    Normalize Arabic text extracted from PDFs.
    This fixes presentation-form Arabic letters like ﻋﻘﺪ into normal Arabic عقد.
    """
    text = unicodedata.normalize("NFKC", text)

    # Remove Arabic diacritics
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)

    # Normalize common Arabic letter variants
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي")
    text = text.replace("ة", "ه")

    # Normalize spacing
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def normalize_for_matching(text: str) -> str:
    """
    Extra normalization for keyword matching.
    """
    text = normalize_arabic_text(text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def light_stem_arabic_word(word: str) -> str:
    """
    Very simple Arabic light stemming to reduce keyword mismatch.
    Example: البيانات / للبيانات -> بيانات
    """
    prefixes = ["وال", "بال", "كال", "فال", "لل", "ال", "و", "ف", "ب", "ك", "ل"]
    suffixes = ["هما", "كما", "نا", "ها", "هم", "كم", "ات", "ون", "ين", "ان", "ه", "ي"]

    for prefix in prefixes:
        if len(word) > len(prefix) + 3 and word.startswith(prefix):
            word = word[len(prefix):]
            break

    for suffix in suffixes:
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            word = word[:-len(suffix)]
            break

    return word


def keyword_matches_clause(keyword: str, clause: str) -> bool:
    """
    Match keyword phrase against clause using normalized phrase + token matching.
    """
    keyword_norm = normalize_for_matching(keyword)
    clause_norm = normalize_for_matching(clause)

    if keyword_norm in clause_norm:
        return True

    keyword_tokens = [token for token in keyword_norm.split() if len(token) >= 3]
    clause_tokens = [token for token in clause_norm.split() if len(token) >= 3]

    clause_stems = {light_stem_arabic_word(token) for token in clause_tokens}

    matched = 0

    for token in keyword_tokens:
        stem = light_stem_arabic_word(token)

        if token in clause_tokens or stem in clause_stems:
            matched += 1
            continue

        for clause_stem in clause_stems:
            if len(stem) >= 4 and (stem in clause_stem or clause_stem in stem):
                matched += 1
                break

    if not keyword_tokens:
        return False

    required_matches = max(1, int(len(keyword_tokens) * 0.7))
    return matched >= required_matches
print("Loading semantic model once...")
MODEL = SentenceTransformer(MODEL_NAME)

COMPLIANT_THRESHOLD = 0.62
PARTIAL_THRESHOLD = 0.48


def read_contract(path: Path) -> str:
    """
    Read Arabic contract text from TXT or PDF file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Contract file not found: {path}")

    if path.suffix.lower() == ".txt":
        with path.open("r", encoding="utf-8") as file:
            return normalize_arabic_text(file.read())

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        pages_text = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        full_text = "\n".join(pages_text)
        return normalize_arabic_text(full_text)

    raise ValueError("Unsupported contract file type. Use .txt or .pdf")

def split_contract_into_clauses(contract_text: str) -> list[str]:
    """
    Split Arabic contract into clauses.
    Supports contracts written with المادة or البند.
    """
    text = normalize_arabic_text(contract_text)

    # Add a separator before common legal clause markers
    text = re.sub(r"\s+(?=(البند|الماده)\s*:?\s*\d*)", "\n", text)

    raw_parts = re.split(r"\n+|(?=البند\s*:?\s*\d*)|(?=الماده\s*:?\s*\d*)", text)

    clauses = []

    for part in raw_parts:
        cleaned = part.strip()
        if len(cleaned) >= 25:
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
    Analyze one requirement using semantic similarity + fuzzy keyword boosting.
    """

    requirement_query = normalize_arabic_text(build_requirement_query(requirement))
    requirement_embedding = model.encode(requirement_query, convert_to_tensor=True)

    similarities = util.cos_sim(requirement_embedding, clause_embeddings)[0]

    original_keywords = requirement["keywords_ar"]

    best_score = 0
    best_clause = ""
    best_matched_keywords = []
    best_combined_score = -1

    for index, clause in enumerate(clauses):
        matched_keywords = []

        for keyword in original_keywords:
            if keyword_matches_clause(keyword, clause):
                matched_keywords.append(keyword)

        semantic_score = float(similarities[index])
        keyword_count = len(matched_keywords)

        # Boost clauses that contain real legal signals
        keyword_boost = min(keyword_count * 0.12, 0.36)
        combined_score = semantic_score + keyword_boost

        if combined_score > best_combined_score:
            best_combined_score = combined_score
            best_score = semantic_score
            best_clause = clause
            best_matched_keywords = matched_keywords

    keyword_count = len(best_matched_keywords)

    if keyword_count >= 2 and best_score >= 0.40:
        status = "Compliant"
        score = requirement["weight"]

    elif keyword_count >= 1 and best_score >= 0.52:
        status = "Compliant"
        score = requirement["weight"]

    elif keyword_count >= 1 and best_score >= 0.40:
        status = "Partial"
        score = requirement["weight"] * 0.5

    elif best_score >= 0.74:
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
        "matched_keywords": best_matched_keywords,
        "recommendation": requirement["recommended_clause_ar"]
    }


def analyze_contract_semantic(contract_path: Path) -> None:
    """
    Analyze Arabic contract using semantic similarity.
    """
    checklist = load_checklist()
    contract_text = read_contract(contract_path)

    print("EXTRACTED TEXT PREVIEW:")
    print(contract_text[:1000])

    clauses = split_contract_into_clauses(contract_text)

    if not clauses:
        raise ValueError("No valid clauses found in the contract.")

    print(f"عدد فقرات العقد المستخرجة: {len(clauses)}")
    print("تحميل مودل المعاني...")
    model = MODEL

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
    compliant_count = sum(1 for result in results if result["status"] == "Compliant")
    partial_count = sum(1 for result in results if result["status"] == "Partial")
    missing_count = sum(1 for result in results if result["status"] == "Missing")

    analysis_output = {
        "contract_file": str(contract_path),
        "score": achieved_score,
        "total_weight": total_weight,
        "compliance_percentage": round(compliance_percentage, 2),
        "summary": {
            "compliant": compliant_count,
            "partial": partial_count,
            "missing": missing_count
        },
        "results": results
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(analysis_output, file, ensure_ascii=False, indent=2)

    print("\nنتيجة تحليل العقد بالمعنى")
    print("=" * 80)
    print(f"الدرجة: {achieved_score} / {total_weight}")
    print(f"نسبة الامتثال: {compliance_percentage:.2f}%")
    print(f"تم حفظ النتيجة في: {OUTPUT_PATH}")
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