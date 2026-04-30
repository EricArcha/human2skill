from human2skill.evidence import claim_support_level, find_overconfident_claims


def test_claim_with_direct_and_observer_support_is_high():
    pack = {
        "evidence": [
            {"evidence_id": "ev-0001", "source_type": "direct_quote_or_behavior"},
            {"evidence_id": "ev-0002", "source_type": "observer_report"}
        ]
    }
    claim = {"evidence_ids": ["ev-0001", "ev-0002"], "confidence": "high"}

    assert claim_support_level(pack, claim) == "high"


def test_flags_overconfident_claim():
    pack = {
        "evidence": [
            {"evidence_id": "ev-0001", "source_type": "model_inference"}
        ],
        "claims": [
            {
                "claim_id": "claim-too-strong",
                "confidence": "high",
                "evidence_ids": ["ev-0001"]
            }
        ]
    }

    assert find_overconfident_claims(pack) == [
        {"claim_id": "claim-too-strong", "claimed": "high", "supported": "low"}
    ]


def test_value_order_claim_flagged_when_overconfident():
    pack = {
        "evidence": [
            {"evidence_id": "ev-0001", "source_type": "model_inference"}
        ],
        "claims": [
            {
                "claim_id": "claim-vo-1",
                "claim": "效率高于关系维护。",
                "claim_type": "value_order",
                "confidence": "high",
                "evidence_ids": ["ev-0001"],
                "status": "active",
            }
        ],
    }

    assert find_overconfident_claims(pack) == [
        {"claim_id": "claim-vo-1", "claimed": "high", "supported": "low"}
    ]


def test_anti_pattern_claim_not_flagged_when_supported():
    pack = {
        "evidence": [
            {"evidence_id": "ev-0001", "source_type": "direct_quote_or_behavior"},
            {"evidence_id": "ev-0002", "source_type": "observer_report"},
        ],
        "claims": [
            {
                "claim_id": "claim-ap-1",
                "claim": "过度微观管理导致团队流失。",
                "claim_type": "anti_pattern",
                "confidence": "high",
                "evidence_ids": ["ev-0001", "ev-0002"],
                "status": "active",
            }
        ],
    }

    assert find_overconfident_claims(pack) == []


def test_pressure_response_claim_handled():
    pack = {
        "evidence": [
            {"evidence_id": "ev-0001", "source_type": "direct_quote_or_behavior"},
            {"evidence_id": "ev-0002", "source_type": "observer_report"},
        ],
        "claims": [
            {
                "claim_id": "claim-pr-1",
                "claim": "压力下更倾向于独自决策。",
                "claim_type": "pressure_response",
                "confidence": "high",
                "evidence_ids": ["ev-0001", "ev-0002"],
                "status": "active",
            }
        ],
    }

    assert find_overconfident_claims(pack) == []


def test_claim_without_profile_scope_is_evaluated():
    pack = {
        "evidence": [
            {"evidence_id": "ev-0001", "source_type": "direct_quote_or_behavior"},
            {"evidence_id": "ev-0002", "source_type": "direct_quote_or_behavior"},
        ],
        "claims": [
            {
                "claim_id": "claim-noscope",
                "claim": "Always asks about impact first.",
                "claim_type": "decision_heuristic",
                "confidence": "high",
                "evidence_ids": ["ev-0001", "ev-0002"],
                "status": "active",
            }
        ],
    }

    assert find_overconfident_claims(pack) == []
