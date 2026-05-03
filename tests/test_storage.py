import json
from pathlib import Path

import pytest

from human2skill.storage import (
    backup_before_update,
    initialize_person_dir,
    restore_version,
    snapshot_version,
    write_changelog,
    write_json,
)


def test_initialize_person_dir_creates_expected_layout(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "zhang-san")

    assert (base / "public_skill").is_dir()
    assert (base / "private_evidence/interviews").is_dir()
    assert (base / "private_evidence/reviews").is_dir()
    assert (base / "versions").is_dir()


def test_snapshot_version_copies_core_artifacts(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "zhang-san")
    write_json(base / "person.meta.json", {"slug": "zhang-san"})
    (base / "public_skill/SKILL.md").write_text("# skill", encoding="utf-8")
    write_json(base / "private_evidence/evidence_pack.json", {"schema_version": "1"})

    snapshot = snapshot_version(base, "v1")

    assert (snapshot / "person.meta.json").exists()
    assert (snapshot / "public_skill/SKILL.md").exists()
    assert (snapshot / "private_evidence/evidence_pack.json").exists()


def test_snapshot_version_copies_new_core_artifacts(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_json(base / "person.meta.json", {"slug": "li-ming"})
    write_json(base / "private_evidence/source_index.json", {"sources": []})
    write_json(base / "private_evidence/distillation.json", {"schema_version": "1"})
    write_json(base / "private_evidence/reviews/review-v1.json", {"passed": True})
    (base / "public_skill/SKILL.md").write_text("# skill", encoding="utf-8")

    snapshot = snapshot_version(base, "v1")

    assert (snapshot / "private_evidence/source_index.json").exists()
    assert (snapshot / "private_evidence/distillation.json").exists()
    assert (snapshot / "private_evidence/reviews/review-v1.json").exists()


def test_write_changelog_creates_version_markdown(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")

    path = write_changelog(base, "v2", ["Added src-0002"], ["claim-impact-first"], [])

    assert path.name == "v2.md"
    assert "Added src-0002" in path.read_text(encoding="utf-8")


def test_restore_version_restores_public_skill(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    (base / "public_skill/SKILL.md").write_text("# v1", encoding="utf-8")
    snapshot_version(base, "v1")
    (base / "public_skill/SKILL.md").write_text("# v2", encoding="utf-8")

    restore_version(base, "v1")

    assert (base / "public_skill/SKILL.md").read_text(encoding="utf-8") == "# v1"


def test_backup_before_update_copies_key_files(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "zhang-san")
    write_json(base / "person.meta.json", {"slug": "zhang-san", "lifecycle": {"version": "v1"}})
    write_json(base / "private_evidence/distillation.json", {"mental_models": []})
    write_json(base / "private_evidence/evidence_pack.json", {"evidence": []})

    result = backup_before_update(base, "v1")

    assert result is not None
    assert (result / "person.meta.json").exists()
    assert (result / "private_evidence/distillation.json").exists()
    assert (result / "private_evidence/evidence_pack.json").exists()
    assert json.loads((result / "person.meta.json").read_text(encoding="utf-8"))["slug"] == "zhang-san"


def test_backup_before_update_returns_none_when_nothing_to_backup(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "zhang-san")
    result = backup_before_update(base, "v1")
    assert result is None


def test_restore_version_raises_for_missing_version(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")

    with pytest.raises(FileNotFoundError):
        restore_version(base, "v99")
