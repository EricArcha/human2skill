from human2skill.interview import (
    initial_coverage,
    next_question_for_profile,
)


def test_initial_coverage_marks_all_missing():
    coverage = initial_coverage()

    assert coverage["mental_models"] == "missing"
    assert coverage["expression_dna"] == "missing"


def test_initial_coverage_includes_value_order_and_anti_patterns():
    coverage = initial_coverage()

    assert coverage["value_order"] == "missing"
    assert coverage["anti_patterns"] == "missing"


def test_next_question_targets_first_missing_dimension():
    coverage = initial_coverage()

    question = next_question_for_profile(
        coverage,
        profile_type="colleague",
        perspective="observer_answer",
        turn_count=0,
    )
    assert "这个人是谁" in question


def test_turn_twenty_prompts_before_extending():
    coverage = initial_coverage()
    coverage["identity_context"] = "medium"

    question = next_question_for_profile(
        coverage,
        profile_type="colleague",
        perspective="observer_answer",
        turn_count=20,
    )
    assert "访谈预算上限" in question
    assert "mental_models" in question


def test_all_dimensions_medium_or_high_returns_completion():
    coverage = {key: "medium" for key in initial_coverage()}

    result = next_question_for_profile(
        coverage,
        profile_type="colleague",
        perspective="observer_answer",
        turn_count=1,
    )
    assert "信息覆盖已经足够" in result


def test_self_perspective_uses_self_wording():
    coverage = initial_coverage()
    coverage["identity_context"] = "medium"

    question = next_question_for_profile(
        coverage,
        profile_type="self",
        perspective="self_answer",
        turn_count=1,
    )

    assert "你" in question
    assert "自己" in question or "过去" in question or "未来" in question


def test_observer_perspective_uses_profile_specific_question_for_known_dimension():
    coverage = {key: "medium" for key in initial_coverage()}
    coverage["honest_boundaries"] = "missing"

    question = next_question_for_profile(
        coverage,
        profile_type="colleague",
        perspective="observer_answer",
        turn_count=1,
    )

    assert "工作场景" in question
