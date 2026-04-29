import json
from pathlib import Path

from human2skill.evidence_builder import add_claim, add_evidence, empty_evidence_pack
from human2skill.exporter import export_skill
from human2skill.flow import build_from_distillation, create_project_person
from human2skill.ingest import add_text_source


def test_p0_p2_end_to_end_flow(tmp_path: Path):
    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="both",
        now="2026-04-29T00:00:00+00:00",
    )
    source = add_text_source(
        base,
        title="manual note",
        text="李明在方案评审时先问 impact 和目标。",
        source_kind="manual_text",
        now="2026-04-29T00:00:00+00:00",
    )
    pack = empty_evidence_pack("li-ming")
    evidence = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary=source["summary"],
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    claim = add_claim(
        pack,
        claim="方案评审前先问 impact 和目标。",
        claim_type="decision_heuristic",
        confidence="medium",
        evidence_ids=[evidence["evidence_id"]],
        profile_scope="colleague",
    )
    (base / "private_evidence/evidence_pack.json").write_text(
        json.dumps(pack, ensure_ascii=False), encoding="utf-8"
    )
    distillation = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [],
        "decision_heuristics": [{
            "title": "Impact first",
            "content": "方案评审前先问 impact 和目标。",
            "claim_ids": [claim["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "手动观察摘要支持。",
            "limits": ["只覆盖工作评审。"]
        }],
        "expression_dna": [],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [
            {
                "title": "关系场景不足",
                "content": "关系场景证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "没有关系场景材料。",
                "limits": ["不推断亲密关系。"]
            },
            {
                "title": "技术细节有限",
                "content": "技术实现细节证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "无技术讨论记录。",
                "limits": ["不推断技术偏好。"]
            },
            {
                "title": "时间范围有限",
                "content": "仅覆盖当前工作场景。",
                "claim_ids": [],
                "confidence": "medium",
                "evidence_summary": "仅当前材料。",
                "limits": ["历史变化未追踪。"]
            },
        ],
        "scenario_tests": []
    }

    result = build_from_distillation(
        base, distillation, generated_at="2026-04-29T00:00:00+00:00"
    )
    export_dir = export_skill(
        base, host="codex", variant="advisor",
        created_at="2026-04-29T00:00:00+00:00"
    )

    assert result["review"]["passed"] is True
    assert (base / "public_skill/variants/advisor/SKILL.md").exists()
    assert (base / "public_skill/variants/first_person/SKILL.md").exists()
    assert (export_dir / "SKILL.md").exists()
