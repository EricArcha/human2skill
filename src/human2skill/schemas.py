from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, exceptions


class SchemaValidationError(ValueError):
    pass


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def schema_dir() -> Path:
    return project_root() / "schemas"


def load_schema(name: str) -> dict:
    path = schema_dir() / name
    return json.loads(path.read_text(encoding="utf-8"))


def validate_document(schema_name: str, document: dict) -> None:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        path = ".".join(str(part) for part in first.path) or "<root>"
        raise SchemaValidationError(f"{schema_name} validation failed at {path}: {first.message}")
