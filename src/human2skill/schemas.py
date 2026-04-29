from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


class SchemaValidationError(ValueError):
    pass


def _resource_path(subdir: str, name: str) -> Path:
    """Resolve a resource path, works in both dev and installed environments."""
    try:
        from importlib.resources import files

        return files("human2skill").joinpath(subdir, name)
    except Exception:
        return Path(__file__).resolve().parent / subdir / name


def load_schema(name: str) -> dict:
    path = _resource_path("schemas", name)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_document(schema_name: str, document: dict) -> None:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        path = ".".join(str(part) for part in first.path) or "<root>"
        raise SchemaValidationError(f"{schema_name} validation failed at {path}: {first.message}")
