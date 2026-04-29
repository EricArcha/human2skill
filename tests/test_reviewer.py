from human2skill.reviewer import review_public_skill, structured_review


def safe_content():
    return "\n".join([
        "不代表本人观点",
        "不声称自己就是 李明 本人",
        "## 核心思维模型",
        "- Impact first",
        "## 表达 DNA",
        "- 短句",
        "## 诚实边界",
        "- 关系场景证据不足。",
        "- 投资建议证据不足。",
        "- 医疗法律问题不适用。",
    ])


def test_review_passes_safe_skill():
    content = "不代表本人观点\n## 诚实边界\n- 证据不足时会说明不确定。"

    assert review_public_skill(content) == {"passed": True, "failures": []}


def test_review_fails_impersonation():
    content = "我就是张三\n## 诚实边界\n不代表本人观点"

    result = review_public_skill(content)

    assert result["passed"] is False
    assert "claims_to_be_person" in result["failures"]


def test_review_fails_private_raw_material():
    content = "不代表本人观点\n## 诚实边界\n这里包含完整聊天记录。"

    result = review_public_skill(content)

    assert result["passed"] is False
    assert "contains_private_raw_material" in result["failures"]


def test_structured_review_passes_safe_advisor():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=safe_content(),
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-29T00:00:00+00:00",
    )

    assert report["passed"] is True
    assert report["scores"]["privacy_safety"] == 5
    assert report["scores"]["honest_boundary"] == 5


def test_structured_review_fails_first_person_without_disclaimer():
    report = structured_review(
        person_slug="li-ming",
        variant="first_person",
        content="## 诚实边界\n- 不确定。\n我就是李明",
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-29T00:00:00+00:00",
    )

    assert report["passed"] is False
    assert "claims_to_be_person" in report["hard_failures"]


def test_structured_review_fails_overconfident_claims():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=safe_content(),
        overconfident_claims=[{"claim_id": "claim-a", "claimed": "high", "supported": "low"}],
        unresolved_conflicts=[],
        generated_at="2026-04-29T00:00:00+00:00",
    )

    assert report["passed"] is False
    assert "unsupported_high_confidence_claims" in report["hard_failures"]


def review_content_without_expression_or_models() -> str:
    return "\n".join([
        "不代表本人观点",
        "不声称自己就是 李明 本人",
        "## 诚实边界",
        "- 关系场景证据不足。",
        "- 投资建议证据不足。",
        "- 医疗法律问题不适用。",
    ])


def review_content_meeting_all_thresholds() -> str:
    return "\n".join([
        "不代表本人观点",
        "不声称自己就是 李明 本人",
        "## 核心思维模型",
        "- 先确认影响范围，再讨论方案。",
        "## 表达 DNA",
        "- 短句，结论先行。",
        "## Profile 专项层",
        "- 适合工作评审和协作场景。",
        "## 诚实边界",
        "- 关系场景证据不足。",
        "- 投资建议证据不足。",
        "- 医疗法律问题不适用。",
    ])


def test_structured_review_fails_when_expression_score_below_threshold():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=review_content_without_expression_or_models(),
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert report["passed"] is False
    assert report["scores"]["expression_similarity"] < 4
    assert not report["hard_failures"]
    assert any("expression" in change.lower() or "表达" in change for change in report["required_changes"])


def test_structured_review_fails_when_thinking_score_below_threshold():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=review_content_without_expression_or_models(),
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert report["passed"] is False
    assert report["scores"]["thinking_utility"] < 4
    assert not report["hard_failures"]
    assert any("thinking" in change.lower() or "思维" in change for change in report["required_changes"])


def test_structured_review_passes_only_when_all_thresholds_met():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=review_content_meeting_all_thresholds(),
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert report["passed"] is True
    assert report["scores"]["evidence_consistency"] >= 4
    assert report["scores"]["confidence_calibration"] >= 4
    assert report["scores"]["honest_boundary"] == 5
    assert report["scores"]["privacy_safety"] == 5
    assert report["scores"]["expression_similarity"] >= 4
    assert report["scores"]["thinking_utility"] >= 4
    assert report["scores"]["profile_fit"] >= 4
