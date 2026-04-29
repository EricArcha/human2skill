from human2skill.interview import (
    initial_coverage,
    next_question,
    next_question_for_profile,
    should_continue,
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

    assert "这个人是谁" in next_question(coverage, turn_count=0)


def test_turn_twenty_prompts_before_extending():
    coverage = initial_coverage()
    coverage["identity_context"] = "medium"

    question = next_question(coverage, turn_count=20)

    assert "接近默认访谈预算" in question
    assert "复杂问题" in question


def test_should_stop_when_all_dimensions_medium_or_high():
    coverage = {key: "medium" for key in initial_coverage()}

    assert should_continue(coverage) is False


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


def test_observer_perspective_asks_for_observable_behavior():
    coverage = initial_coverage()
    coverage["identity_context"] = "medium"

    question = next_question_for_profile(
        coverage,
        profile_type="colleague",
        perspective="observer_answer",
        turn_count=1,
    )

    assert "具体" in question or "观察" in question or "场景" in question
