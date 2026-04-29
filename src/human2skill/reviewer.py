PRIVATE_MARKERS = ("完整聊天记录", "身份证", "手机号", "原始私聊", "朋友圈原文")


def review_public_skill(content: str) -> dict:
    failures = []
    if "我就是" in content:
        failures.append("claims_to_be_person")
    if "诚实边界" not in content:
        failures.append("missing_honest_boundaries")
    if any(marker in content for marker in PRIVATE_MARKERS):
        failures.append("contains_private_raw_material")
    if "不代表本人观点" not in content:
        failures.append("missing_disclaimer")
    return {"passed": not failures, "failures": failures}
