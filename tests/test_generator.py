from human2skill.generator import render_skill


def test_render_skill_uses_perspective_advisor_protocol():
    meta = {"slug": "zhang-san", "display_name": "张三"}
    distilled = {
        "mental_models": ["先问目标和 impact，再讨论方案。"],
        "expression_dna": ["短句、反问、结论先行。"],
        "decision_heuristics": ["没有明确收益时倾向推迟。"],
        "profile_specific": ["适合工作评审场景。"],
        "pressure_response": ["被质疑时先问判断依据。"],
        "honest_boundaries": ["亲密关系场景证据不足。"]
    }

    content = render_skill(meta, distilled)

    assert "张三 视角顾问" in content
    assert "不代表本人观点" in content
    assert "不声称自己就是 张三 本人" in content
    assert "先问目标和 impact" in content
