from pathlib import Path

from human2skill.generator import render_skill_variant, write_skill_variants
from human2skill.reviewer import structured_review
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
    sections = {
        "mental_models": ["讨论方案前先问 impact。"],
        "expression_dna": ["短句，结论先行。"],
        "honest_boundaries": ["关系场景证据不足。", "技术细节了解有限。", "非工作场景沟通风格未知。"],
    }

    write_json(base / "person.meta.json", meta)
    write_json(base / "private_evidence" / "evidence_pack.json", evidence_pack)

    variants = write_skill_variants(base, meta, sections)
    skill = variants.get("advisor", list(variants.values())[0])

    review = structured_review(
        person_slug="zhang-san",
        variant="advisor",
        content=skill,
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-05-01T00:00:00+00:00",
    )
    snapshot = snapshot_version(base, "v1")

    assert review["passed"] is True
    assert (snapshot / "public_skill/SKILL.md").exists()
