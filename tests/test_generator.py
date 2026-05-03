from human2skill.generator import render_skill_variant, render_skill_variants


def full_distilled_sections():
    return {
        "mental_models": ["Impact first: 先问 impact。"],
        "expression_dna": ["短句，结论先行。"],
        "decision_heuristics": ["没有收益则推迟。"],
        "profile_specific": ["适合工作评审。"],
        "pressure_response": ["被质疑时问依据。"],
        "value_order": ["效果高于优雅。"],
        "anti_patterns": ["不接受无目标讨论。"],
        "honest_boundaries": ["关系场景证据不足。"],
    }


def test_render_advisor_variant_uses_lens_naming():
    meta = {"slug": "zhang-san", "display_name": "张三", "voice_mode": "advisor"}
    sections = {
        "mental_models": ["先问目标和 impact，再讨论方案。"],
        "expression_dna": ["短句、反问、结论先行。"],
        "decision_heuristics": ["没有明确收益时倾向推迟。"],
        "profile_specific": ["适合工作评审场景。"],
        "pressure_response": ["被质疑时先问判断依据。"],
        "honest_boundaries": ["亲密关系场景证据不足。"]
    }

    content = render_skill_variant(meta, sections, variant="advisor")

    assert "zhang-san-lens" in content
    assert "张三 视角顾问" in content
    assert "不代表本人观点" in content
    assert "先问目标和 impact" in content


def test_render_advisor_variant_keeps_non_impersonation():
    meta = {"slug": "li-ming", "display_name": "李明", "voice_mode": "advisor"}

    content = render_skill_variant(meta, full_distilled_sections(), variant="advisor")

    assert "视角顾问" in content
    assert "不代表本人观点" in content
    assert "不声称自己就是 李明 本人" in content
    assert "价值排序" in content
    assert "反模式" in content


def test_render_first_person_variant_has_mandatory_disclaimer():
    meta = {"slug": "li-ming", "display_name": "李明", "voice_mode": "first_person"}

    content = render_skill_variant(meta, full_distilled_sections(), variant="first_person")

    assert "有限第一人称" in content
    assert "不代表本人观点" in content
    assert "不得声称自己就是李明本人" in content
    assert "我" in content


def test_render_both_variants_returns_two_entries():
    meta = {"slug": "li-ming", "display_name": "李明", "voice_mode": "both"}

    variants = render_skill_variants(meta, full_distilled_sections())

    assert set(variants) == {"advisor", "first_person"}


def test_missing_voice_mode_defaults_to_advisor_only():
    meta = {"slug": "li-ming", "display_name": "李明"}

    variants = render_skill_variants(meta, full_distilled_sections())

    assert set(variants) == {"advisor"}
