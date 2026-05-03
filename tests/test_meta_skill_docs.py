from pathlib import Path

SKILL_PATH = Path(__file__).resolve().parent.parent / "human2skill-meta" / "SKILL.md"


def test_meta_skill_documents_required_flow():
    content = SKILL_PATH.read_text(encoding="utf-8")

    assert "human2skill create" in content
    assert "human2skill ingest" in content
    assert "distillation.json" in content
    assert "summary_only" in content
    assert "不输出私域原文" in content
    assert "outputs/{slug}" in content
    assert "{slug}-lens" in content
    assert "quality_check.py" in content


def test_meta_skill_mentions_checkpoints():
    content = SKILL_PATH.read_text(encoding="utf-8")

    assert "Checkpoint A" in content
    assert "Checkpoint B" in content
    assert "Checkpoint C" in content
