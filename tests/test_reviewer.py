from human2skill.reviewer import review_public_skill


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
