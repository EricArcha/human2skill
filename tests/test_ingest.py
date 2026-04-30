from pathlib import Path

from human2skill.ingest import add_text_source, ingest_file, load_source_index
from human2skill.storage import initialize_person_dir


def test_add_text_source_creates_source_index(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")

    source = add_text_source(
        base,
        title="manual note",
        text="李明在评审时先问 impact，再看方案。",
        source_kind="manual_text",
        now="2026-04-29T00:00:00+00:00",
    )

    index = load_source_index(base)
    assert source["source_id"] == "src-0001"
    assert index["person_slug"] == "li-ming"
    assert index["sources"][0]["allowed_in_public_skill"] is False
    assert "impact" in index["sources"][0]["summary"]


def test_ingest_markdown_file_records_markdown_kind(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    file_path = tmp_path / "notes.md"
    file_path.write_text("# Notes\n\n李明喜欢先确认目标。", encoding="utf-8")

    source = ingest_file(base, file_path, now="2026-04-29T00:00:00+00:00")

    assert source["source_kind"] == "markdown"
    assert source["title"] == "notes.md"


def test_ingest_unsupported_file_type_rejects(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    file_path = tmp_path / "notes.bin"
    file_path.write_bytes(b"\x00\x01")

    try:
        ingest_file(base, file_path)
    except ValueError as error:
        assert "Unsupported file type" in str(error)
    else:
        raise AssertionError("unsupported file did not fail")


def test_add_text_source_rejects_invalid_source_kind(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")

    try:
        add_text_source(
            base,
            title="test",
            text="test",
            source_kind="invalid_kind",
        )
    except ValueError as error:
        assert "Unknown source kind" in str(error)
    else:
        raise AssertionError("invalid source kind did not fail")
