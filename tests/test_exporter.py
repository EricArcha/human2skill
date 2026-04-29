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


def write_variant(base: Path, variant: str, content: str = "# skill") -> None:
    path = base / "public_skill" / "variants" / variant
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(content, encoding="utf-8")


def write_review(base: Path, filename: str, *, variant: str, passed: bool) -> None:
    write_json(
        base / "private_evidence" / "reviews" / filename,
        {
            "schema_version": "1",
            "person_slug": base.name,
            "variant": variant,
            "generated_at": "2026-04-30T00:00:00+00:00",
            "passed": passed,
            "hard_failures": [],
            "scores": {
                "evidence_consistency": 4,
                "confidence_calibration": 4,
                "honest_boundary": 5,
                "privacy_safety": 5,
                "expression_similarity": 4,
                "thinking_utility": 4,
                "profile_fit": 4,
            },
            "required_changes": [],
            "notes": [],
        },
    )


def test_export_first_person_requires_first_person_review(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_variant(base, "first_person")
    write_review(base, "advisor.json", variant="advisor", passed=True)

    try:
        export_skill(base, host="codex", variant="first_person")
    except ValueError as error:
        assert "first_person" in str(error)
    else:
        raise AssertionError("first_person export passed without first_person review")


def test_export_first_person_rejects_failed_first_person_review(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_variant(base, "first_person")
    write_review(base, "first_person.json", variant="first_person", passed=False)

    try:
        export_skill(base, host="codex", variant="first_person")
    except ValueError as error:
        assert "did not pass" in str(error)
    else:
        raise AssertionError("failed first_person review allowed export")


def test_export_advisor_ignores_failed_first_person_review(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_variant(base, "advisor")
    write_review(base, "advisor.json", variant="advisor", passed=True)
    write_review(base, "first_person.json", variant="first_person", passed=False)

    export_dir = export_skill(
        base,
        host="codex",
        variant="advisor",
        created_at="2026-04-30T00:00:00+00:00",
    )

    manifest = json.loads((export_dir / "export_manifest.json").read_text(encoding="utf-8"))
    assert manifest["variant"] == "advisor"
    assert manifest["review_passed"] is True


def test_export_rejects_review_variant_mismatch(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_variant(base, "advisor")
    write_review(base, "advisor.json", variant="first_person", passed=True)

    try:
        export_skill(base, host="codex", variant="advisor")
    except ValueError as error:
        assert "variant" in str(error)
    else:
        raise AssertionError("mismatched review variant allowed export")
