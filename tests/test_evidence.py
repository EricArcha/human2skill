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
