import json
import shutil
from pathlib import Path


def person_dir(root: Path, slug: str) -> Path:
    return root / "outputs" / slug


def initialize_person_dir(root: Path, slug: str) -> Path:
    base = person_dir(root, slug)
    for relative in (
        "corpus/raw",
        "public_skill",
        "public_skill/variants/advisor",
        "public_skill/variants/first_person",
        "private_evidence/interviews",
        "private_evidence/reviews",
        "private_evidence/changelog",
        "exports/codex",
        "exports/claude-code",
        "exports/openclaw",
        "exports/hermes",
        "versions",
    ):
        (base / relative).mkdir(parents=True, exist_ok=True)
    return base


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def backup_before_update(base: Path, current_version: str) -> Path | None:
    """Archive current key artifacts before an incremental update.

    Copies ``person.meta.json``, ``distillation.json``, and
    ``evidence_pack.json`` into ``versions/{version}_before_update/``.
    Returns the backup directory path, or ``None`` if none of the source
    files exist.
    """
    target = base / "versions" / f"{current_version}_before_update"
    sources = (
        "person.meta.json",
        "private_evidence/distillation.json",
        "private_evidence/evidence_pack.json",
    )
    wrote = False
    for relative in sources:
        src = base / relative
        if src.exists():
            dest = target / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            wrote = True
    return target if wrote else None


def snapshot_version(base: Path, version: str) -> Path:
    target = base / "versions" / version
    target.mkdir(parents=True, exist_ok=True)

    # Individual files to copy
    files = (
        "person.meta.json",
        "public_skill/SKILL.md",
        "private_evidence/evidence_pack.json",
        "private_evidence/source_index.json",
        "private_evidence/distillation.json",
    )
    for relative in files:
        source = base / relative
        if source.exists():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    # Directories to copy (entire contents)
    dirs = (
        "public_skill/variants",
        "private_evidence/reviews",
        "private_evidence/changelog",
    )
    for relative in dirs:
        source = base / relative
        if source.is_dir() and any(source.iterdir()):
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)

    return target


def write_changelog(
    base: Path,
    version: str,
    added_sources: list[str],
    changed_claims: list[str],
    conflicts: list[str],
) -> Path:
    changelog_dir = base / "private_evidence" / "changelog"
    changelog_dir.mkdir(parents=True, exist_ok=True)

    lines = [f"# Changelog {version}", ""]

    if added_sources:
        lines.append("## Added sources")
        for item in added_sources:
            lines.append(f"- {item}")
        lines.append("")

    if changed_claims:
        lines.append("## Changed claims")
        for item in changed_claims:
            lines.append(f"- {item}")
        lines.append("")

    if conflicts:
        lines.append("## Conflicts")
        for item in conflicts:
            lines.append(f"- {item}")
        lines.append("")

    path = changelog_dir / f"{version}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def restore_version(base: Path, version: str) -> Path:
    source = base / "versions" / version
    if not source.is_dir():
        raise FileNotFoundError(f"Version not found: {version}")

    # Clear fully-restored directories first to prevent stale files from
    # surviving the restore (e.g. a variant that existed after the snapshot).
    fully_restored_dirs = (
        "public_skill/variants",
        "private_evidence/reviews",
        "private_evidence/changelog",
    )
    for relative in fully_restored_dirs:
        dest = base / relative
        if dest.is_dir():
            shutil.rmtree(dest)

    for item in source.rglob("*"):
        if not item.is_file():
            continue
        relative = item.relative_to(source)
        destination = base / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_dir():
            shutil.rmtree(destination)
        shutil.copy2(item, destination)

    return source
