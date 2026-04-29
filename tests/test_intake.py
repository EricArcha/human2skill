import json
from pathlib import Path

from human2skill.intake import create_person


def test_create_person_writes_meta_with_defaults(tmp_path: Path):
    base = create_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review perspective",
        voice_mode="both",
        now="2026-04-29T00:00:00+00:00",
    )

    meta = json.loads((base / "person.meta.json").read_text(encoding="utf-8"))

    assert meta["slug"] == "li-ming"
    assert meta["voice_mode"] == "both"
    assert meta["privacy_policy"]["raw_retention"] == "summary_only"
    assert meta["privacy_policy"]["public_skill_allows_private_quotes"] is False
    assert meta["export_policy"]["shareable_variants"] == ["advisor"]


def test_create_person_creates_full_layout(tmp_path: Path):
    base = create_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review perspective",
        now="2026-04-29T00:00:00+00:00",
    )

    assert (base / "public_skill/variants/advisor").is_dir()
    assert (base / "public_skill/variants/first_person").is_dir()
    assert (base / "private_evidence/interviews").is_dir()
    assert (base / "private_evidence/reviews").is_dir()
    assert (base / "private_evidence/changelog").is_dir()
    assert (base / "exports/codex").is_dir()
    assert (base / "exports/claude-code").is_dir()
    assert (base / "exports/openclaw").is_dir()
    assert (base / "exports/hermes").is_dir()
    assert (base / "versions").is_dir()
