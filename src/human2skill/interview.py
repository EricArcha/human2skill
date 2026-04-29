CORE_DIMENSIONS = (
    "identity_context",
    "mental_models",
    "expression_dna",
    "decision_heuristics",
    "pressure_response",
    "profile_specific",
    "honest_boundaries",
    "evaluation_scenarios",
)


QUESTION_BANK = {
    "identity_context": "这个人是谁？你和他是什么关系？你最想用这个视角解决什么问题？",
    "mental_models": "他遇到复杂问题时，通常先看什么？能举一个具体场景吗？",
    "expression_dna": "他常说的三句话是什么？请尽量贴近原话。",
    "decision_heuristics": "他在什么情况下会推进、等待、拒绝或改变主意？",
    "pressure_response": "他被催、被质疑或遇到冲突时，通常怎么反应？",
    "profile_specific": "按这个人的身份，最能代表他的专项能力或互动方式是什么？",
    "honest_boundaries": "哪些问题上你不确定他会怎么想？有没有反例？",
    "evaluation_scenarios": "请给一个历史场景和一个新场景，用来测试生成后的 Skill。"
}


def initial_coverage() -> dict[str, str]:
    return {dimension: "missing" for dimension in CORE_DIMENSIONS}


def next_question(coverage: dict[str, str], turn_count: int) -> str:
    for dimension in CORE_DIMENSIONS:
        if coverage.get(dimension) in ("missing", "low"):
            if turn_count >= 20:
                return (
                    "目前已经接近默认访谈预算，但仍缺少关键信息。"
                    f" 下一步建议补充：{QUESTION_BANK[dimension]}"
                )
            return QUESTION_BANK[dimension]
    return "信息覆盖已经足够，可以进入蒸馏。"


def should_continue(coverage: dict[str, str]) -> bool:
    return any(value in ("missing", "low") for value in coverage.values())
