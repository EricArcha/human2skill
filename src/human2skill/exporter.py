from __future__ import annotations

import json
import shutil
from pathlib import Path

from human2skill.constants import HOSTS
from human2skill.schemas import validate_document
from human2skill.timeutils import utc_now_iso

PRIVATE_MARKERS = ("完整聊天记录", "身份证", "手机号", "原始私聊", "朋友圈原文")


def review_path_for_variant(base: Path, variant: str) -> Path | None:
    reviews_dir = base / "private_evidence" / "reviews"
    direct = reviews_dir / f"{variant}.json"
    if direct.exists():
        return direct

    legacy = reviews_dir / "review-v1.json"
    if variant == "advisor" and legacy.exists():
        return legacy

    return None


def load_review_for_variant(base: Path, variant: str) -> dict:
    path = review_path_for_variant(base, variant)
    if path is None:
        raise ValueError(f"Cannot export {variant}: review report is missing.")

    report = json.loads(path.read_text(encoding="utf-8"))
    report_variant = report.get("variant")
    if report_variant is not None and report_variant != variant:
        raise ValueError(
            f"Cannot export {variant}: review report variant mismatch: {report_variant}"
        )
    return report


def review_passed_for_variant(base: Path, variant: str) -> bool:
    return bool(load_review_for_variant(base, variant).get("passed", False))


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

    review = load_review_for_variant(base, variant)
    if not review.get("passed", False):
        raise ValueError(f"Cannot export {variant}: review did not pass.")

    skill_path = variant_skill_path(base, variant)
    if not skill_path.exists():
        raise ValueError(f"Variant skill not found: {skill_path}")

    export_dir = base / "exports" / host
    export_dir.mkdir(parents=True, exist_ok=True)

    dest_skill = export_dir / "SKILL.md"
    shutil.copy2(skill_path, dest_skill)

    privacy_passed = _privacy_check_passed(dest_skill)
    if not privacy_passed:
        raise ValueError(f"Cannot export {variant}: privacy check failed.")

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
        "review_passed": bool(review.get("passed", False)),
        "privacy_check_passed": privacy_passed,
    }

    validate_document("export_manifest.schema.json", manifest)

    manifest_path = export_dir / "export_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return export_dir
