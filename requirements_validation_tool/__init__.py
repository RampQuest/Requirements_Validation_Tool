"""Requirements validation ingestion package."""

from .ingestion import RequirementIngestionError, ingest_requirements_file

__all__ = ["RequirementIngestionError", "ingest_requirements_file"]
