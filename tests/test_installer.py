from pathlib import Path

from human2skill.installer import install_export


def test_install_export_copies_to_explicit_target(tmp_path: Path):
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    (export_dir / "SKILL.md").write_text("# skill", encoding="utf-8")
    target = tmp_path / "target"

    installed = install_export(export_dir, target, package_name="li-ming")

    assert installed == target / "li-ming"
    assert (installed / "SKILL.md").exists()


def test_install_export_requires_existing_export(tmp_path: Path):
    try:
        install_export(tmp_path / "missing", tmp_path / "target", package_name="li-ming")
    except FileNotFoundError as error:
        assert "missing" in str(error)
    else:
        raise AssertionError("missing export did not fail")
