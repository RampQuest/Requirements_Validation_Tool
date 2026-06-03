from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


REQUIREMENT_CATEGORIES = {
    "functional_hmi_requirements": "functional_hmi",
    "ux_ui_specifications": "ux_ui",
    "safety_regulatory_requirements": "safety_regulatory",
    "use_case_definitions": "use_case",
    "acceptance_criteria": "acceptance_criteria",
}


class RequirementIngestionError(ValueError):
    """Raised when input data cannot be ingested into requirement records."""


@dataclass(frozen=True)
class RequirementRecord:
    requirement_id: str
    requirement_type: str
    title: str
    description: str
    source_path: str
    related_requirement_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def _load_data(input_path: Path) -> dict[str, Any]:
    suffix = input_path.suffix.lower()

    if suffix == ".json":
        with input_path.open("r", encoding="utf-8") as file_obj:
            payload = json.load(file_obj)
            if not isinstance(payload, dict):
                raise RequirementIngestionError("Input file must contain a JSON object at the root.")
            return payload

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as error:
            raise RequirementIngestionError(
                "YAML input requires PyYAML. Install it or provide a JSON file."
            ) from error

        with input_path.open("r", encoding="utf-8") as file_obj:
            payload = yaml.safe_load(file_obj)
            if not isinstance(payload, dict):
                raise RequirementIngestionError("Input file must contain a mapping at the root.")
            return payload

    raise RequirementIngestionError(f"Unsupported file format '{input_path.suffix}'. Use JSON or YAML.")


def _validate_item(category: str, item: Any, index: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise RequirementIngestionError(
            f"{category}[{index}] must be an object, got {type(item).__name__}."
        )

    missing_fields = [field_name for field_name in ("id", "title", "description") if not item.get(field_name)]
    if missing_fields:
        raise RequirementIngestionError(
            f"{category}[{index}] is missing required fields: {', '.join(missing_fields)}."
        )

    return item


def ingest_requirements_file(input_file: str) -> dict[str, Any]:
    """Load requirement inputs, validate schema, and normalize for downstream workflows."""
    input_path = Path(input_file)
    if not input_path.exists():
        raise RequirementIngestionError(f"Input file not found: {input_file}")

    payload = _load_data(input_path)

    normalized_records: list[RequirementRecord] = []
    counts: dict[str, int] = {}

    for category, normalized_type in REQUIREMENT_CATEGORIES.items():
        raw_items = payload.get(category)
        if raw_items is None:
            raise RequirementIngestionError(f"Missing required top-level field: {category}")
        if not isinstance(raw_items, list):
            raise RequirementIngestionError(f"'{category}' must be a list.")

        counts[normalized_type] = len(raw_items)
        for index, item in enumerate(raw_items):
            validated_item = _validate_item(category, item, index)
            related_ids = validated_item.get("related_requirement_ids") or []
            if not isinstance(related_ids, list):
                raise RequirementIngestionError(
                    f"{category}[{index}].related_requirement_ids must be a list when provided."
                )

            metadata = {
                key: value
                for key, value in validated_item.items()
                if key not in {"id", "title", "description", "related_requirement_ids"}
            }

            normalized_records.append(
                RequirementRecord(
                    requirement_id=str(validated_item["id"]),
                    requirement_type=normalized_type,
                    title=str(validated_item["title"]),
                    description=str(validated_item["description"]),
                    source_path=str(input_path),
                    related_requirement_ids=[str(value) for value in related_ids],
                    metadata=metadata,
                )
            )

    return {
        "source": str(input_path),
        "summary": {
            "total_requirements": len(normalized_records),
            "by_type": counts,
        },
        "requirements": [asdict(record) for record in normalized_records],
    }
