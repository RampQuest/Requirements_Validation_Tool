# Requirements_Validation_Tool

First-phase foundation for AI-driven HMI validation input ingestion.

## Use cases

- Convert mixed HMI requirement artifacts into a single normalized data model.
- Catch missing or malformed requirement fields early in the validation lifecycle.
- Build a machine-readable baseline for downstream test generation and traceability.
- Align functional, UX/UI, safety, use-case, and acceptance inputs into one source of truth.

## Supported requirement input categories

The ingestion flow requires all of the following top-level categories:

- `functional_hmi_requirements`
- `ux_ui_specifications`
- `safety_regulatory_requirements`
- `use_case_definitions`
- `acceptance_criteria`

Each item in every category must include:

- `id`
- `title`
- `description`

Optional fields are preserved in normalized output as `metadata`.

## Input format

JSON is supported out of the box. YAML (`.yaml` / `.yml`) is also supported when `PyYAML` is installed.

Example input (`requirements_input.json`):

```json
{
  "functional_hmi_requirements": [
    {
      "id": "F-001",
      "title": "Display speed",
      "description": "Speed widget updates within 250 ms"
    }
  ],
  "ux_ui_specifications": [
    {
      "id": "UX-001",
      "title": "Contrast",
      "description": "Primary text contrast ratio is >= 4.5:1"
    }
  ],
  "safety_regulatory_requirements": [
    {
      "id": "S-001",
      "title": "Warning persistence",
      "description": "Critical warning remains visible for 3 seconds"
    }
  ],
  "use_case_definitions": [
    {
      "id": "UC-001",
      "title": "Start navigation",
      "description": "Driver starts route guidance from home screen"
    }
  ],
  "acceptance_criteria": [
    {
      "id": "AC-001",
      "title": "Speed acceptance",
      "description": "Given speed changes, then display updates within 250 ms",
      "related_requirement_ids": ["F-001"]
    }
  ]
}
```

## Run ingestion

Print normalized output to stdout:

```bash
python -m requirements_validation_tool requirements_input.json
```

Write normalized output to file:

```bash
python -m requirements_validation_tool requirements_input.json --output normalized_requirements.json
```

## Run tests

```bash
python -m unittest discover -s tests -v
```
