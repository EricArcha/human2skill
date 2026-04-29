import json
from pathlib import Path

from human2skill.exporter import export_skill
from human2skill.storage import initialize_person_dir, write_json


def prepare_skill(base: Path):
    (base / "public_skill/variants/advisor").mkdir(parents=True, exist_ok=True)
    (base / "public_skill/variants/advisor/SKILL.md").write_text("# advisor", encoding="utf-8")
    write_json(base / "private_evidence/reviews/review-v1.json", {"passed": True})


def test_export_codex_writes_manifest_and_skill(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    prepare_skill(base)

    export_dir = export_skill(
        base,
        host="codex",
        variant="advisor",
        created_at="2026-04-29T00:00:00+00:00",
    )

    assert (export_dir / "SKILL.md").exists()
    manifest = json.loads((export_dir / "export_manifest.json").read_text(encoding="utf-8"))
    assert manifest["host"] == "codex"
    assert manifest["review_passed"] is True
    assert manifest["privacy_check_passed"] is True


def test_export_rejects_unknown_host(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    prepare_skill(base)

    try:
        export_skill(base, host="unknown", variant="advisor")
    except ValueError as error:
        assert "Unknown host" in str(error)
    else:
        raise AssertionError("unknown host did not fail")
