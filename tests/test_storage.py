from pathlib import Path

from human2skill.storage import initialize_person_dir, snapshot_version, write_json


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
