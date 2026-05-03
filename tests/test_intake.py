import json
from pathlib import Path

from human2skill.intake import create_person, normalize_profile, normalize_voice_mode, project_exists, project_status


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


def test_normalize_profile_defaults_invalid_to_relationship():
    assert normalize_profile(None) == "relationship"
    assert normalize_profile("invalid_type") == "relationship"


def test_normalize_profile_passes_valid_types():
    assert normalize_profile("colleague") == "colleague"
    assert normalize_profile("relationship") == "relationship"
    assert normalize_profile("mentor") == "mentor"
    assert normalize_profile("self") == "self"


def test_normalize_voice_mode_defaults_invalid_to_advisor():
    assert normalize_voice_mode(None) == "advisor"
    assert normalize_voice_mode("invalid_mode") == "advisor"


def test_normalize_voice_mode_passes_valid_modes():
    assert normalize_voice_mode("advisor") == "advisor"
    assert normalize_voice_mode("first_person") == "first_person"
    assert normalize_voice_mode("both") == "both"


def test_project_exists_false_for_nonexistent(tmp_path: Path):
    assert project_exists(tmp_path, "nobody") is False


def test_project_exists_true_for_created(tmp_path: Path):
    create_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
    )
    assert project_exists(tmp_path, "li-ming") is True


def test_project_status_returns_not_found(tmp_path: Path):
    status = project_status(tmp_path / "outputs" / "nobody")
    assert status["exists"] is False


def test_project_status_returns_summary(tmp_path: Path):
    base = create_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        now="2026-05-01T00:00:00+00:00",
    )
    status = project_status(base)
    assert status["exists"] is True
    assert status["version"] == "v1"
    assert status["created_at"] == "2026-05-01T00:00:00+00:00"
    assert status["mental_model_count"] == 0
    assert status["source_count"] == 0
    assert status["version_count"] == 0


def test_create_person_with_minimal_args_defaults_voice_and_populates_timestamps(tmp_path: Path):
    base = create_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type=None,
        relationship_to_user="coworker",
        use_case="work review",
    )

    meta = json.loads((base / "person.meta.json").read_text(encoding="utf-8"))
    assert meta["voice_mode"] == "advisor"
    assert meta["profile_type"] == "relationship"
    assert meta["lifecycle"]["created_at"]
    assert meta["lifecycle"]["updated_at"]
