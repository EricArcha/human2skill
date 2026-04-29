from pathlib import Path

from human2skill.generator import render_skill
from human2skill.reviewer import review_public_skill
from human2skill.storage import initialize_person_dir, snapshot_version, write_json


def test_minimal_person_flow(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "zhang-san")
    meta = {
        "schema_version": "1",
        "slug": "zhang-san",
        "display_name": "张三",
        "profile_type": "colleague"
    }
    evidence_pack = {
        "schema_version": "1",
        "person_slug": "zhang-san",
        "evidence": [],
        "claims": []
    }
    distilled = {
        "mental_models": ["讨论方案前先问 impact。"],
        "expression_dna": ["短句，结论先行。"],
        "honest_boundaries": ["关系场景证据不足。"]
    }

    write_json(base / "person.meta.json", meta)
    write_json(base / "private_evidence/evidence_pack.json", evidence_pack)
    skill = render_skill(meta, distilled)
    (base / "public_skill/SKILL.md").write_text(skill, encoding="utf-8")

    review = review_public_skill(skill)
    snapshot = snapshot_version(base, "v1")

    assert review["passed"] is True
    assert (snapshot / "public_skill/SKILL.md").exists()
