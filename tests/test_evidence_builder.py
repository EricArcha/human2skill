from human2skill.evidence_builder import (
    add_claim,
    add_conflict,
    add_evidence,
    empty_evidence_pack,
)
from human2skill.evidence import find_overconfident_claims


def test_add_evidence_and_claim_links_ids():
    pack = empty_evidence_pack("li-ming")
    evidence = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="用户观察到李明先问 impact。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    claim = add_claim(
        pack,
        claim="讨论方案前先问 impact。",
        claim_type="decision_heuristic",
        confidence="medium",
        evidence_ids=[evidence["evidence_id"]],
        profile_scope="colleague",
    )

    assert evidence["evidence_id"] == "ev-0001"
    assert claim["claim_id"].startswith("claim-")
    assert claim["evidence_ids"] == ["ev-0001"]


def test_add_conflict_records_halt_resolution():
    pack = empty_evidence_pack("li-ming")
    conflict = add_conflict(
        pack,
        claim_ids=["claim-a", "claim-b"],
        evidence_ids=["ev-0001", "ev-0002"],
        conflict_type="contextual",
        resolution="halt_for_review",
        note="工作场景直接，关系场景回避。",
    )

    assert conflict["conflict_id"] == "cf-0001"
    assert pack["conflicts"][0]["resolution"] == "halt_for_review"


def test_overconfident_value_order_claim_is_flagged():
    pack = empty_evidence_pack("li-ming")
    evidence = add_evidence(
        pack,
        source_type="model_inference",
        source_summary="模型推断其重视效率。",
        retention="summary_only",
        confidence="low",
        supports=[],
    )
    claim = add_claim(
        pack,
        claim="效率高于关系维护。",
        claim_type="value_order",
        confidence="high",
        evidence_ids=[evidence["evidence_id"]],
    )

    assert find_overconfident_claims(pack) == [{
        "claim_id": claim["claim_id"],
        "claimed": "high",
        "supported": "low",
    }]
