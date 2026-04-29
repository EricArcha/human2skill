import json
from pathlib import Path

from human2skill.evidence_builder import add_claim, add_evidence
from human2skill.flow import build_from_distillation, create_project_person


def test_create_project_person_initializes_person(tmp_path: Path):
    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-29T00:00:00+00:00",
    )

    assert (base / "person.meta.json").exists()
    assert (base / "private_evidence/source_index.json").exists()


def test_build_from_distillation_renders_and_reviews(tmp_path: Path):
    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-29T00:00:00+00:00",
    )
    pack = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "evidence": [],
        "claims": [],
        "conflicts": [],
    }
    ev = add_evidence(pack, source_type="direct_quote_or_behavior", source_summary="先问 impact。", retention="summary_only", confidence="medium", supports=[])
    add_claim(pack, claim="先问 impact。", claim_type="decision_heuristic", confidence="medium", evidence_ids=[ev["evidence_id"]])
    (base / "private_evidence/evidence_pack.json").write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    distillation = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [],
        "decision_heuristics": [{
            "title": "Impact first",
            "content": "先问 impact。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"]
        }],
        "expression_dna": [],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [{
            "title": "关系不足",
            "content": "关系场景证据不足。",
            "claim_ids": [],
            "confidence": "low",
            "evidence_summary": "无证据。",
            "limits": ["不推断关系。"]
        }, {
            "title": "技术细节有限",
            "content": "技术实现细节证据不足。",
            "claim_ids": [],
            "confidence": "low",
            "evidence_summary": "无技术讨论记录。",
            "limits": ["不推断技术偏好。"]
        }, {
            "title": "时间范围有限",
            "content": "仅覆盖当年工作场景。",
            "claim_ids": [],
            "confidence": "medium",
            "evidence_summary": "仅当年材料。",
            "limits": ["历史变化未追踪。"]
        }],
        "scenario_tests": []
    }

    result = build_from_distillation(base, distillation, generated_at="2026-04-29T00:00:00+00:00")

    assert result["review"]["passed"] is True
    assert (base / "public_skill/SKILL.md").exists()
