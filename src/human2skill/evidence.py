SOURCE_WEIGHT = {
    "direct_quote_or_behavior": 3,
    "observer_report": 2,
    "model_inference": 1,
}


def evidence_by_id(pack: dict) -> dict[str, dict]:
    return {item["evidence_id"]: item for item in pack.get("evidence", [])}


def claim_support_level(pack: dict, claim: dict) -> str:
    evidence = evidence_by_id(pack)
    items = [evidence[eid] for eid in claim.get("evidence_ids", []) if eid in evidence]
    if not items:
        return "unsupported"
    direct_count = sum(1 for item in items if item["source_type"] == "direct_quote_or_behavior")
    observer_count = sum(1 for item in items if item["source_type"] == "observer_report")
    if direct_count >= 2 or (direct_count >= 1 and observer_count >= 1):
        return "high"
    if direct_count == 1 or observer_count >= 2:
        return "medium"
    return "low"


def find_overconfident_claims(pack: dict) -> list[dict]:
    result = []
    rank = {"unsupported": 0, "low": 1, "medium": 2, "high": 3}
    for claim in pack.get("claims", []):
        support = claim_support_level(pack, claim)
        if rank[support] < rank[claim["confidence"]]:
            result.append({"claim_id": claim["claim_id"], "claimed": claim["confidence"], "supported": support})
    return result
