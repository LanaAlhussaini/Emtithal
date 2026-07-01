import json
from pathlib import Path
from typing import Any


CHECKLIST_PATH = Path("data/checklists/outsourcing_checklist.json")


REQUIRED_FIELDS = [
    "id",
    "category",
    "name_ar",
    "name_en",
    "description_ar",
    "description_en",
    "risk_level",
    "weight",
    "source_document",
    "source_section",
    "source_page",
    "keywords_ar",
    "keywords_en",
    "pass_criteria_ar",
    "recommended_clause_ar"
]


ALLOWED_RISK_LEVELS = {"High", "Medium", "Low"}


def load_checklist(path: Path = CHECKLIST_PATH) -> list[dict[str, Any]]:
    """
    Load the outsourcing checklist from a JSON file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Checklist file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        checklist = json.load(file)

    if not isinstance(checklist, list):
        raise ValueError("Checklist file must contain a list of requirements.")

    return checklist


def validate_checklist(checklist: list[dict[str, Any]]) -> bool:
    """
    Validate that the checklist is complete and safe for the analyzer to use.
    """
    seen_ids = set()

    for item in checklist:
        for field in REQUIRED_FIELDS:
            if field not in item:
                raise ValueError(
                    f"Missing field '{field}' in item: {item.get('id', 'UNKNOWN')}"
                )

        if item["id"] in seen_ids:
            raise ValueError(f"Duplicate requirement id: {item['id']}")
        seen_ids.add(item["id"])

        if item["risk_level"] not in ALLOWED_RISK_LEVELS:
            raise ValueError(
                f"Invalid risk level in {item['id']}: {item['risk_level']}"
            )

        if not isinstance(item["weight"], int) or item["weight"] <= 0:
            raise ValueError(
                f"Invalid weight in {item['id']}. Weight must be a positive integer."
            )

        if not isinstance(item["keywords_ar"], list):
            raise ValueError(f"keywords_ar must be a list in {item['id']}")

        if not isinstance(item["keywords_en"], list):
            raise ValueError(f"keywords_en must be a list in {item['id']}")

    return True


def get_total_weight(checklist: list[dict[str, Any]]) -> int:
    """
    Calculate the total possible compliance score weight.
    """
    return sum(item["weight"] for item in checklist)


def get_requirement_by_id(requirement_id: str) -> dict[str, Any] | None:
    """
    Return one requirement by ID.
    """
    checklist = load_checklist()

    for item in checklist:
        if item["id"] == requirement_id:
            return item

    return None


def get_requirements_by_risk(risk_level: str) -> list[dict[str, Any]]:
    """
    Return requirements by risk level: High, Medium, or Low.
    """
    checklist = load_checklist()
    return [item for item in checklist if item["risk_level"] == risk_level]


def print_summary() -> None:
    """
    Print a summary to confirm the checklist is working.
    """
    checklist = load_checklist()
    validate_checklist(checklist)

    print("Checklist loaded successfully.")
    print(f"Number of requirements: {len(checklist)}")
    print(f"Total weight: {get_total_weight(checklist)}")
    print("-" * 60)

    for item in checklist:
        print(
            f"{item['id']} | {item['risk_level']} | "
            f"{item['weight']} pts | {item['name_ar']}"
        )


if __name__ == "__main__":
    print_summary()