from __future__ import annotations

import argparse
import json
import sys

from .ingestion import RequirementIngestionError, ingest_requirements_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest and validate HMI requirement inputs into a normalized representation."
    )
    parser.add_argument("input", help="Path to a JSON or YAML requirements file")
    parser.add_argument("--output", help="Optional path to write normalized JSON output")
    args = parser.parse_args()

    try:
        normalized = ingest_requirements_file(args.input)
    except RequirementIngestionError as error:
        print(f"Ingestion failed: {error}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file_obj:
            json.dump(normalized, file_obj, indent=2)
            file_obj.write("\n")
    else:
        print(json.dumps(normalized, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
