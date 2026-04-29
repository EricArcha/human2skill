from __future__ import annotations

import json
import shutil
from pathlib import Path

from human2skill.constants import HOSTS
from human2skill.schemas import validate_document
from human2skill.timeutils import utc_now_iso

PRIVATE_MARKERS = ("完整聊天记录", "身份证", "手机号", "原始私聊", "朋友圈原文")


def latest_review_passed(base: Path) -> bool:
    reviews_dir = base / "private_evidence" / "reviews"
    if not reviews_dir.is_dir():
        return False

    review_files = sorted(reviews_dir.glob("*.json"))
    if not review_files:
        return False

    latest = json.loads(review_files[-1].read_text(encoding="utf-8"))
    return latest.get("passed", False)


def variant_skill_path(base: Path, variant: str) -> Path:
    return base / "public_skill" / "variants" / variant / "SKILL.md"


def _privacy_check_passed(skill_path: Path) -> bool:
    if not skill_path.exists():
        return False
    content = skill_path.read_text(encoding="utf-8")
    return not any(marker in content for marker in PRIVATE_MARKERS)


def export_skill(
    base: Path,
    host: str,
    variant: str = "advisor",
    created_at: str | None = None,
) -> Path:
    if host not in HOSTS:
        raise ValueError(f"Unknown host: {host!r}. Supported: {HOSTS}")

    if not latest_review_passed(base):
        raise ValueError("Cannot export: latest review is missing or did not pass.")

    skill_path = variant_skill_path(base, variant)
    if not skill_path.exists():
        raise ValueError(f"Variant skill not found: {skill_path}")

    export_dir = base / "exports" / host
    export_dir.mkdir(parents=True, exist_ok=True)

    dest_skill = export_dir / "SKILL.md"
    shutil.copy2(skill_path, dest_skill)

    resolved_created_at = created_at or utc_now_iso()
    person_slug = base.name

    manifest = {
        "schema_version": "1",
        "host": host,
        "person_slug": person_slug,
        "variant": variant,
        "created_at": resolved_created_at,
        "files": ["SKILL.md"],
        "install_hint": f"Copy SKILL.md into your {host} skills directory.",
        "review_passed": latest_review_passed(base),
        "privacy_check_passed": _privacy_check_passed(dest_skill),
    }

    validate_document("export_manifest.schema.json", manifest)

    manifest_path = export_dir / "export_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return export_dir
