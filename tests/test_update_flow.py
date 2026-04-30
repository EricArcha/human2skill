from human2skill.flow import detect_update_conflicts, summarize_update


def test_detect_update_conflicts_halts_on_active_conflict():
    pack = {
        "claims": [
            {"claim_id": "claim-a", "status": "active"},
            {"claim_id": "claim-b", "status": "active"},
        ],
        "conflicts": [{
            "conflict_id": "cf-0001",
            "claim_ids": ["claim-a", "claim-b"],
            "evidence_ids": ["ev-0001", "ev-0002"],
            "conflict_type": "contextual",
            "resolution": "halt_for_review",
            "note": "场景冲突"
        }]
    }

    result = detect_update_conflicts(pack)

    assert result["halted"] is True
    assert result["conflicts"][0]["conflict_id"] == "cf-0001"


def test_summarize_update_lists_sources_claims_and_conflicts():
    summary = summarize_update(
        added_sources=["src-0002"],
        changed_claims=["claim-impact-first"],
        conflicts=["cf-0001"],
    )

    assert "src-0002" in summary
    assert "claim-impact-first" in summary
    assert "cf-0001" in summary
