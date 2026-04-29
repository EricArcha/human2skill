CORE_DIMENSIONS = (
    "identity_context",
    "mental_models",
    "expression_dna",
    "decision_heuristics",
    "pressure_response",
    "profile_specific",
    "honest_boundaries",
    "evaluation_scenarios",
    "value_order",
    "anti_patterns",
)

QUESTION_BANK = {
    "identity_context": "这个人是谁？你和他是什么关系？你最想用这个视角解决什么问题？",
    "mental_models": "他遇到复杂问题时，通常先看什么？能举一个具体场景吗？",
    "expression_dna": "他常说的三句话是什么？请尽量贴近原话。",
    "decision_heuristics": "他在什么情况下会推进、等待、拒绝或改变主意？",
    "pressure_response": "他被催、被质疑或遇到冲突时，通常怎么反应？",
    "profile_specific": "按这个人的身份，最能代表他的专项能力或互动方式是什么？",
    "honest_boundaries": "哪些问题上你不确定他会怎么想？有没有反例？",
    "evaluation_scenarios": "请给一个历史场景和一个新场景，用来测试生成后的 Skill。",
    "value_order": "他在做取舍时，最看重什么？有没有他明确说过'这个比那个重要'的例子？",
    "anti_patterns": "他最反感或坚决避免的做法、习惯或思维方式是什么？能举反例吗？",
}

SELF_QUESTIONS = {
    "identity_context": "请描述你自己的角色和身份背景。你希望这个 Skill 在什么场景下帮到你？",
    "mental_models": "你过去遇到复杂问题时，通常先从哪里入手？有没有自己反复出现的分析模式？",
    "expression_dna": "你常说的话或口头禅是什么？请尽量贴近原话。",
    "decision_heuristics": "回顾自己过去的决定，你在什么条件下会果断推进、什么条件下会犹豫？",
    "pressure_response": "你在被催、被质疑或在冲突情境中，通常的第一反应是什么？之后会怎么调整？",
    "profile_specific": "就你的身份和经历而言，最能代表你的专项能力或互动风格是什么？",
    "honest_boundaries": "在哪些问题上你觉得自己可能有不自知的一面？或者你已知的盲点是什么？",
    "evaluation_scenarios": "请提供两个场景：一个你过去处理过的，一个你未来可能面对的，用来验证这个 Skill。",
    "value_order": "长期来看，你自己做选择时最在意的价值排序是什么？有没有你曾经为某个价值牺牲另一个的经历？",
    "anti_patterns": "你自认为最想避免的思维定式或行为模式是什么？有什么你刻意不去做的事？",
}

PROFILE_QUESTIONS = {
    "colleague": {
        "identity_context": "这个人是谁？你们在什么项目或团队中共事？你最希望借助他解决什么工作问题？",
        "profile_specific": "在协作中，他在哪方面的判断或能力让你觉得'这点他最靠谱'？能举具体事例吗？",
        "honest_boundaries": "在工作场景里，有哪些问题你觉得他的做法可能和你不一样？有没有你不太确定他会怎么选的情况？",
        "value_order": "在工作取舍上，他最看重什么？比如速度 vs 质量、影响 vs 优雅、稳定 vs 创新，他通常怎么排序？",
        "anti_patterns": "在工作中他最反感或坚决避免的做法是什么？比如无目标的会议、不写测试、或过度设计？",
    },
    "relationship": {
        "identity_context": "这个人是谁？你和他是什么关系？认识多久了？你最想用这个视角帮你理解什么？",
        "profile_specific": "在你们的关系中，他/她最让你印象深刻的一个特质或处理方式是什么？",
        "honest_boundaries": "哪些话题或情境下，你感觉不太了解他的真实想法？有没有你觉得'可能不是这样'的猜测？",
        "value_order": "在你观察中，他在人际关系中最看重什么？比如真诚、忠诚、自由、稳定，他一般怎么排序？",
        "anti_patterns": "在关系中他最不能容忍或最回避的行为是什么？比如冷战、过度控制、不守承诺？",
    },
    "mentor": {
        "identity_context": "这个人是谁？他是你哪个方面的导师或引路人？你希望用他的视角指导你的哪些决策？",
        "profile_specific": "他传授给你的最有价值的框架或原则是什么？是在什么情境下对你产生影响的？",
        "honest_boundaries": "在他的建议中，有没有你不太认同或者觉得不太适用于你当前处境的部分？",
        "value_order": "他指导你时最常强调的价值是什么？比如深度 > 广度、长期 > 短期、原则 > 灵活？",
        "anti_patterns": "他警告过你最要避免的思维陷阱或行为模式是什么？比如过早优化、盲目跟风？",
    },
    "self": {
        "identity_context": "请描述你希望这个 Skill 展示的自我面向。你想让它在什么情境下提供你自己的视角？",
        "profile_specific": "回顾过去一段时间的成长，你在哪个方面的变化最显著？你希望 Skill 能体现这种动态变化吗？",
        "honest_boundaries": "你觉得自我认知中最大的盲区是什么？有没有别人对你的反馈让你意外、但后来发现确实如此的？",
        "value_order": "回顾你自己的重大决定，你发现哪些价值一直在优先级最前面？有没有你为了某个价值而放弃另一个的经历？",
        "anti_patterns": "你自己最警惕的思维惯性或行为模式是什么？有没有你刻意训练自己避免的旧习惯？",
    },
}


def initial_coverage() -> dict[str, str]:
    return {dimension: "missing" for dimension in CORE_DIMENSIONS}


def _get_question(dimension: str, profile_type: str, perspective: str) -> str:
    """Select the most specific question for a dimension.

    Priority: profile-specific > perspective-specific > general bank.
    """
    profile_qs = PROFILE_QUESTIONS.get(profile_type, {})
    if dimension in profile_qs:
        return profile_qs[dimension]

    if perspective == "self_answer" and dimension in SELF_QUESTIONS:
        return SELF_QUESTIONS[dimension]

    return QUESTION_BANK[dimension]


def next_question_for_profile(
    coverage: dict[str, str],
    *,
    profile_type: str,
    perspective: str,
    turn_count: int,
) -> str:
    """Select next interview question based on coverage gaps and perspective.

    Args:
        coverage: Dimension coverage map (key: dimension name, value: missing/low/medium/high).
        profile_type: One of 'colleague', 'relationship', 'mentor', 'self'.
        perspective: 'self_answer' or 'observer_answer'.
        turn_count: Current turn number (used for budget warning at 20+).

    Returns:
        The selected question string, or a completion message if all dimensions are
        medium/high.
    """
    for dimension in CORE_DIMENSIONS:
        if coverage.get(dimension) in ("missing", "low"):
            question = _get_question(dimension, profile_type, perspective)

            if turn_count >= 20:
                return (
                    "目前已经接近默认访谈预算，但仍缺少关键信息。"
                    f" 下一步建议补充：{question}"
                )
            return question

    return "信息覆盖已经足够，可以进入蒸馏。"


def next_question(coverage: dict[str, str], turn_count: int) -> str:
    """Backward-compatible question selector.

    Delegates to next_question_for_profile with default observer perspective.
    """
    return next_question_for_profile(
        coverage,
        profile_type="relationship",
        perspective="observer_answer",
        turn_count=turn_count,
    )


def should_continue(coverage: dict[str, str]) -> bool:
    return any(value in ("missing", "low") for value in coverage.values())
