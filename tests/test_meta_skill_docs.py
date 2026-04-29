from pathlib import Path


def test_meta_skill_documents_required_flow():
    content = Path("human2skill-meta/SKILL.md").read_text(encoding="utf-8")

    assert "human2skill create" in content
    assert "human2skill ingest" in content
    assert "distillation.json" in content
    assert "summary_only" in content
    assert "不输出私域原文" in content
    assert "advisor" in content
    assert "first_person" in content


def test_meta_skill_mentions_checkpoints():
    content = Path("human2skill-meta/SKILL.md").read_text(encoding="utf-8")

    assert "Source Coverage Checkpoint" in content
    assert "Distillation Checkpoint" in content
    assert "Review Checkpoint" in content
