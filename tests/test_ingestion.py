import json
import tempfile
import unittest
from pathlib import Path

from requirements_validation_tool.ingestion import RequirementIngestionError, ingest_requirements_file


class IngestionTests(unittest.TestCase):
    def write_json(self, payload: dict) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        file_path = Path(temp_dir.name) / "requirements.json"
        file_path.write_text(json.dumps(payload), encoding="utf-8")
        return str(file_path)

    def valid_payload(self) -> dict:
        return {
            "functional_hmi_requirements": [
                {
                    "id": "F-001",
                    "title": "Display current speed",
                    "description": "The speed widget shall update within 250 ms.",
                }
            ],
            "ux_ui_specifications": [
                {
                    "id": "UX-001",
                    "title": "Contrast requirements",
                    "description": "Primary text contrast ratio must be >= 4.5:1.",
                    "metadata_source": "design-system-v2",
                }
            ],
            "safety_regulatory_requirements": [
                {
                    "id": "S-001",
                    "title": "Warning visibility",
                    "description": "Critical warnings must remain visible for 3 seconds.",
                }
            ],
            "use_case_definitions": [
                {
                    "id": "UC-001",
                    "title": "Start navigation",
                    "description": "Driver initiates route guidance from home screen.",
                }
            ],
            "acceptance_criteria": [
                {
                    "id": "AC-001",
                    "title": "Speed widget acceptance",
                    "description": "Given speed changes, then displayed value updates within 250 ms.",
                    "related_requirement_ids": ["F-001"],
                }
            ],
        }

    def test_ingests_and_normalizes_requirements(self):
        path = self.write_json(self.valid_payload())

        result = ingest_requirements_file(path)

        self.assertEqual(result["summary"]["total_requirements"], 5)
        self.assertEqual(result["summary"]["by_type"]["functional_hmi"], 1)
        self.assertEqual(result["requirements"][0]["source_path"], path)
        acceptance = [r for r in result["requirements"] if r["requirement_type"] == "acceptance_criteria"][0]
        self.assertEqual(acceptance["related_requirement_ids"], ["F-001"])

    def test_missing_required_category_raises_error(self):
        payload = self.valid_payload()
        del payload["acceptance_criteria"]
        path = self.write_json(payload)

        with self.assertRaises(RequirementIngestionError) as context:
            ingest_requirements_file(path)

        self.assertIn("Missing required top-level field: acceptance_criteria", str(context.exception))

    def test_missing_required_item_fields_raise_error(self):
        payload = self.valid_payload()
        payload["functional_hmi_requirements"][0].pop("title")
        path = self.write_json(payload)

        with self.assertRaises(RequirementIngestionError) as context:
            ingest_requirements_file(path)

        self.assertIn("functional_hmi_requirements[0] is missing required fields: title", str(context.exception))


if __name__ == "__main__":
    unittest.main()
