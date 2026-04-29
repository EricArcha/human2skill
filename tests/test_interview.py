from human2skill.interview import initial_coverage, next_question, should_continue


def test_initial_coverage_marks_all_missing():
    coverage = initial_coverage()

    assert coverage["mental_models"] == "missing"
    assert coverage["expression_dna"] == "missing"


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
