import json
from pathlib import Path

from human2skill.evidence_builder import add_claim, add_conflict, add_evidence, empty_evidence_pack
from human2skill.flow import build_from_distillation, create_project_person
from human2skill.storage import write_json


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
        "mental_models": [{
            "title": "Impact first",
            "content": "先问 impact，再讨论方案。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"]
        }],
        "decision_heuristics": [{
            "title": "Impact first",
            "content": "先问 impact。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"]
        }],
        "expression_dna": [{
            "title": "直接表达",
            "content": "结论先行。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作场景。"]
        }],
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


def test_build_increments_version_in_meta(tmp_path: Path):
    """Each build call updates the version in person.meta.json even if review fails."""
    from human2skill.evidence_builder import add_claim, add_evidence

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

    pack = empty_evidence_pack("li-ming")
    ev = add_evidence(pack, source_type="direct_quote_or_behavior",
                      source_summary="先问 impact。", retention="summary_only",
                      confidence="medium", supports=[])
    add_claim(pack, claim="先问 impact。", claim_type="decision_heuristic",
              confidence="medium", evidence_ids=[ev["evidence_id"]])
    write_json(base / "private_evidence/evidence_pack.json", pack)
    claim_id = pack["claims"][0]["claim_id"]

    def load_version() -> str:
        meta = json.loads((base / "person.meta.json").read_text(encoding="utf-8"))
        return meta["lifecycle"]["version"]

    dist = {
        "schema_version": "1", "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [], "decision_heuristics": [], "expression_dna": [],
        "profile_specific": [], "pressure_response": [], "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [
            {"title": "A", "content": "X", "claim_ids": [], "confidence": "low",
             "evidence_summary": "无", "limits": ["不推断。"]},
        ],
        "scenario_tests": [],
    }

    assert load_version() == "v1"  # initial version from create

    # Simulate one prior successful build by creating a version dir.
    (base / "versions" / "v1").mkdir(parents=True, exist_ok=True)

    # Build → should now compute v2 (1 existing dir → v2)
    build_from_distillation(base, dist, generated_at="2026-05-01T00:00:00+00:00")
    assert load_version() == "v2"


# ---------------------------------------------------------------------------
# Conflict resolution regression tests
# ---------------------------------------------------------------------------


def build_base_with_conflict(tmp_path: Path, resolution: str) -> tuple[Path, dict]:
    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-30T00:00:00+00:00",
    )
    pack = empty_evidence_pack("li-ming")
    ev1 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="工作场景直接指出问题。",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev2 = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="关系场景会放缓语气。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    claim1 = add_claim(
        pack,
        claim="工作场景直接指出问题。",
        claim_type="pressure_response",
        confidence="medium",
        evidence_ids=[ev1["evidence_id"]],
    )
    claim2 = add_claim(
        pack,
        claim="关系场景会放缓语气。",
        claim_type="pressure_response",
        confidence="medium",
        evidence_ids=[ev2["evidence_id"]],
    )
    add_conflict(
        pack,
        claim_ids=[claim1["claim_id"], claim2["claim_id"]],
        evidence_ids=[ev1["evidence_id"], ev2["evidence_id"]],
        conflict_type="contextual",
        resolution=resolution,
        note="不同场景保留不同规则。",
    )
    (base / "private_evidence/evidence_pack.json").write_text(
        json.dumps(pack, ensure_ascii=False),
        encoding="utf-8",
    )
    return base, claim1


def conflict_distillation(claim_id: str) -> dict:
    return {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-30T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [],
        "decision_heuristics": [],
        "expression_dna": [{
            "title": "直接但会分场景",
            "content": "工作场景直接，关系场景放缓。",
            "claim_ids": [claim_id],
            "confidence": "medium",
            "evidence_summary": "冲突按场景保留。",
            "limits": ["只覆盖已观察场景。"],
        }],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [
            {
                "title": "关系边界",
                "content": "亲密关系细节证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "仅有观察者描述。",
                "limits": ["不推断深层动机。"],
            },
            {
                "title": "时间边界",
                "content": "只覆盖当前阶段。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "没有长期材料。",
                "limits": ["不推断长期变化。"],
            },
            {
                "title": "领域边界",
                "content": "非工作领域证据较弱。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "工作材料更多。",
                "limits": ["不泛化到所有关系。"],
            },
        ],
        "scenario_tests": [],
    }


def test_build_allows_keep_both_with_scope_conflict(tmp_path: Path):
    base, claim = build_base_with_conflict(tmp_path, "keep_both_with_scope")

    result = build_from_distillation(
        base,
        conflict_distillation(claim["claim_id"]),
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert "unresolved_conflicts" not in result["review"]["hard_failures"]


def test_build_allows_mark_low_confidence_conflict(tmp_path: Path):
    base, claim = build_base_with_conflict(tmp_path, "mark_low_confidence")

    result = build_from_distillation(
        base,
        conflict_distillation(claim["claim_id"]),
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert "unresolved_conflicts" not in result["review"]["hard_failures"]


def test_build_blocks_halt_for_review_conflict(tmp_path: Path):
    base, claim = build_base_with_conflict(tmp_path, "halt_for_review")

    result = build_from_distillation(
        base,
        conflict_distillation(claim["claim_id"]),
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert "unresolved_conflicts" in result["review"]["hard_failures"]
