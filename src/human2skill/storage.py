import json
import shutil
from pathlib import Path


def person_dir(root: Path, slug: str) -> Path:
    return root / "people" / slug


def initialize_person_dir(root: Path, slug: str) -> Path:
    base = person_dir(root, slug)
    for relative in (
        "public_skill",
        "private_evidence/interviews",
        "private_evidence/reviews",
        "versions",
    ):
        (base / relative).mkdir(parents=True, exist_ok=True)
    return base


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def snapshot_version(base: Path, version: str) -> Path:
    target = base / "versions" / version
    target.mkdir(parents=True, exist_ok=True)
    for relative in ("person.meta.json", "public_skill/SKILL.md", "private_evidence/evidence_pack.json"):
        source = base / relative
        if source.exists():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    return target
