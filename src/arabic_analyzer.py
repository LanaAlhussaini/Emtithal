from checklist import load_checklist, get_total_weight


CONTRACT_PATH = "data/sample_contracts/sample_arabic_contract.txt"


def read_contract(path: str) -> str:
    """
    Read Arabic contract text from a TXT file.
    """
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def analyze_requirement_ar(contract_text: str, requirement: dict) -> dict:
    """
    Analyze one requirement against an Arabic contract using Arabic keywords.
    """
    keywords = requirement["keywords_ar"]
    matched_keywords = []

    for keyword in keywords:
        if keyword in contract_text:
            matched_keywords.append(keyword)

    if len(matched_keywords) >= 2:
        status = "Compliant"
        score = requirement["weight"]
    elif len(matched_keywords) == 1:
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
        "matched_keywords": matched_keywords,
        "recommendation": requirement["recommended_clause_ar"]
    }


def analyze_contract_ar(contract_path: str) -> None:
    checklist = load_checklist()
    contract_text = read_contract(contract_path)

    total_weight = get_total_weight(checklist)
    achieved_score = 0
    results = []

    for requirement in checklist:
        result = analyze_requirement_ar(contract_text, requirement)
        results.append(result)
        achieved_score += result["score"]

    compliance_percentage = (achieved_score / total_weight) * 100

    print("نتيجة تحليل العقد")
    print("=" * 70)
    print(f"الدرجة: {achieved_score} / {total_weight}")
    print(f"نسبة الامتثال: {compliance_percentage:.2f}%")
    print("=" * 70)

    for result in results:
        print(
            f"{result['id']} | {result['status']} | "
            f"{result['score']}/{result['weight']} | {result['name_ar']}"
        )

        if result["matched_keywords"]:
            print(f"الكلمات المطابقة: {', '.join(result['matched_keywords'])}")
        else:
            print("الكلمات المطابقة: لا يوجد")
            print(f"التوصية: {result['recommendation']}")

        print("-" * 70)


if __name__ == "__main__":
    analyze_contract_ar(CONTRACT_PATH)