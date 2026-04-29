from __future__ import annotations

import json
from pathlib import Path

from human2skill.constants import SOURCE_KINDS
from human2skill.schemas import validate_document
from human2skill.timeutils import utc_now_iso

SUPPORTED_SUFFIX_MAP: dict[str, str] = {
    ".md": "markdown",
    ".txt": "txt",
    ".pdf": "pdf_text",
}


def source_index_path(base: Path) -> Path:
    return base / "private_evidence" / "source_index.json"


def load_source_index(base: Path) -> dict:
    path = source_index_path(base)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "schema_version": "1",
        "person_slug": base.name,
        "sources": [],
    }


def write_source_index(base: Path, payload: dict) -> None:
    validate_document("source_index.schema.json", payload)
    path = source_index_path(base)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def next_source_id(index: dict) -> str:
    count = len(index.get("sources", []))
    return f"src-{count + 1:04d}"


def _build_source_entry(
    *,
    source_kind: str,
    title: str,
    text: str,
    provided_by: str,
    created_at: str,
    index: dict,
) -> dict:
    return {
        "source_id": next_source_id(index),
        "source_kind": source_kind,
        "title": title,
        "provided_by": provided_by,
        "retention": "summary_only",
        "contains_private_data": True,
        "allowed_in_public_skill": False,
        "summary": text.strip()[:500],
        "created_at": created_at,
    }


def add_text_source(
    base: Path,
    *,
    title: str,
    text: str,
    source_kind: str,
    now: str | None = None,
    provided_by: str = "unknown",
) -> dict:
    if source_kind not in SOURCE_KINDS:
        raise ValueError(f"Unknown source kind: {source_kind!r}")

    created_at = now if now is not None else utc_now_iso()
    index = load_source_index(base)
    source = _build_source_entry(
        source_kind=source_kind,
        title=title,
        text=text,
        provided_by=provided_by,
        created_at=created_at,
        index=index,
    )
    index["sources"].append(source)
    write_source_index(base, index)
    return source


def ingest_file(
    base: Path,
    file_path: Path,
    *,
    now: str | None = None,
    provided_by: str = "file_ingestion",
) -> dict:
    suffix = file_path.suffix.lower()
    source_kind = SUPPORTED_SUFFIX_MAP.get(suffix)
    if source_kind is None:
        raise ValueError(f"Unsupported file type: {file_path}")

    # Extract text based on file type
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(file_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if not text.strip():
            raise ValueError(f"PDF text extraction produced no text: {file_path}")
    else:
        text = file_path.read_text(encoding="utf-8")

    title = file_path.name
    created_at = now if now is not None else utc_now_iso()
    index = load_source_index(base)
    source = _build_source_entry(
        source_kind=source_kind,
        title=title,
        text=text,
        provided_by=provided_by,
        created_at=created_at,
        index=index,
    )
    index["sources"].append(source)
    write_source_index(base, index)
    return source
