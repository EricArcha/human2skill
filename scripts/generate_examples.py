#!/usr/bin/env python3
"""Generate three fictional human2skill examples using the full flow pipeline.

Each example is a complete person project with:
- person.meta.json
- public_skill/SKILL.md + variants
- private_evidence/ (evidence_pack.json, source_index.json, distillation.json, reviews)
- exports/codex/export_manifest.json
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Ensure the src directory is importable.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from human2skill.evidence_builder import add_claim, add_evidence, empty_evidence_pack
from human2skill.exporter import export_skill
from human2skill.flow import build_from_distillation, create_project_person
from human2skill.storage import write_json

NOW = "2026-04-29T00:00:00+00:00"


# ---------------------------------------------------------------------------
# Helper: apply privacy policy
# ---------------------------------------------------------------------------

def ensure_privacy_policy(base: Path) -> None:
    """Ensure privacy_policy.public_skill_allows_private_quotes is False."""
    meta_path = base / "person.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["privacy_policy"]["public_skill_allows_private_quotes"] = False
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Helper: finalise -- copy review, export, copy out of tmp
# ---------------------------------------------------------------------------

def finalise(base: Path, export_variant: str) -> None:
    """Write review-v1.json (copy of primary review) and export to codex."""
    # Write review-v1.json (the primary variant's review, renamed).
    reviews_dir = base / "private_evidence" / "reviews"
    primary_review = reviews_dir / f"{export_variant}.json"
    if primary_review.exists():
        shutil.copy2(primary_review, reviews_dir / "review-v1.json")

    # Export for codex.
    export_skill(base, host="codex", variant=export_variant, created_at=NOW)


def copy_to_dir(tmp_base: Path, dest: str) -> None:
    """Copy the person dir from tmp_base to dest."""
    dest_path = Path(dest)
    if dest_path.exists():
        shutil.rmtree(dest_path)
    shutil.copytree(tmp_base, dest_path)


# ===================================================================
# Example 1: colleague-li-ming
# ===================================================================

def build_li_ming(root: Path) -> Path:
    """Fictional colleague Li Ming: work methods, decision heuristics, pressure."""
    base = create_project_person(
        root=root,
        slug="colleague-li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="同事，同一个技术团队的资深工程师",
        use_case="工作评审与协作，理解其技术决策和团队协作方式",
        voice_mode="both",
        now=NOW,
    )
    ensure_privacy_policy(base)

    pack = empty_evidence_pack("colleague-li-ming")

    # --- Evidence ---
    ev1 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="技术评审中李明说：'先问这个改动影响了多少用户，再决定投入多少。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev2 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="周会上李明说：'可逆的决策快速执行，不可逆的决策拉更多人讨论。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev3 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="代码评审中李明写道：'这里的逻辑如果三个月后再看会好理解吗？'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev4 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="技术分享会上李明用装修房子的比喻来解释微服务架构设计原则。",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev5 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="在一次代码评审中李明先肯定了实现思路，然后才提出具体的改进建议。",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev6 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="站会上李明说：'遇到分歧先对齐目标，不要陷在方案层面争论。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev7 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="李明在发布评审会上说：'先发出去收集反馈，比在内部打磨完美更有价值。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev8 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="技术文档中李明写道：'宁可多写三行注释让意图清晰，也不省一行让后人猜测。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev9 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="李明在项目启动时明确同步时间节点：'周三前出原型，周五团队评审，下周二上线。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev10 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="李明在技术选型讨论中说：'不要过早优化，先用最简单方案验证假设。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev11 = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="同事反馈：李明偶尔会对简单问题引入过度复杂的架构。",
        retention="summary_only",
        confidence="low",
        supports=[],
    )
    ev12 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="李明在复盘时说：'代码质量非常重要，但不要为了追求完美错过发布窗口。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )

    # --- Claims ---
    c1 = add_claim(
        pack,
        claim="先问影响范围再做技术决策",
        claim_type="decision_heuristic",
        confidence="high",
        evidence_ids=[ev1["evidence_id"], ev2["evidence_id"]],
    )
    c2 = add_claim(
        pack,
        claim="问题拆分优先于技术选型，用最简单方案先验证假设",
        claim_type="mental_model",
        confidence="medium",
        evidence_ids=[ev10["evidence_id"]],
    )
    c3 = add_claim(
        pack,
        claim="可逆决策快速执行，不可逆决策充分讨论",
        claim_type="decision_heuristic",
        confidence="high",
        evidence_ids=[ev2["evidence_id"], ev12["evidence_id"]],
    )
    c4 = add_claim(
        pack,
        claim="技术讨论中习惯使用生活场景类比和故事化表达",
        claim_type="expression_dna",
        confidence="medium",
        evidence_ids=[ev4["evidence_id"]],
    )
    c5 = add_claim(
        pack,
        claim="代码和设计评审时先肯定再提改进建议",
        claim_type="expression_dna",
        confidence="medium",
        evidence_ids=[ev5["evidence_id"]],
    )
    c6 = add_claim(
        pack,
        claim="注重代码可维护性，宁可多写注释也不让逻辑晦涩难懂",
        claim_type="profile_specific",
        confidence="high",
        evidence_ids=[ev3["evidence_id"], ev8["evidence_id"]],
    )
    c7 = add_claim(
        pack,
        claim="对时间线敏感，协作时主动同步预期完成时间",
        claim_type="profile_specific",
        confidence="medium",
        evidence_ids=[ev9["evidence_id"]],
    )
    c8 = add_claim(
        pack,
        claim="截止日期压力下倾向于先交付最小可用版本再迭代优化",
        claim_type="pressure_response",
        confidence="medium",
        evidence_ids=[ev7["evidence_id"]],
    )
    c9 = add_claim(
        pack,
        claim="遇到分歧先对齐目标而非争论方案细节",
        claim_type="decision_heuristic",
        confidence="high",
        evidence_ids=[ev6["evidence_id"], ev1["evidence_id"]],
    )
    c10 = add_claim(
        pack,
        claim="代码质量优先于交付速度，但不为完美错过发布窗口",
        claim_type="value_order",
        confidence="medium",
        evidence_ids=[ev12["evidence_id"]],
    )
    c11 = add_claim(
        pack,
        claim="偶尔对简单问题引入过度架构设计",
        claim_type="anti_pattern",
        confidence="low",
        evidence_ids=[ev11["evidence_id"]],
    )

    write_json(base / "private_evidence" / "evidence_pack.json", pack)

    # --- Distillation ---
    distillation = {
        "schema_version": "1",
        "person_slug": "colleague-li-ming",
        "generated_at": NOW,
        "source_evidence_pack_version": "v1",
        "mental_models": [
            {
                "title": "问题拆分优先",
                "content": "在技术选型前先充分拆分问题，用最简单方案验证假设，避免过早优化。",
                "claim_ids": [c2["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "会议和评审记录中的观察。",
                "limits": ["不适用于需要从零搭建基础设施的场景。"],
            },
            {
                "title": "可维护性驱动设计",
                "content": "设计方案时以三个月后的可理解性为衡量标准，宁可多花时间写清楚也不留歧义。",
                "claim_ids": [c6["claim_id"]],
                "confidence": "high",
                "evidence_summary": "多次代码评审记录和文档。",
                "limits": ["不影响紧急热修复场景。"],
            },
        ],
        "decision_heuristics": [
            {
                "title": "影响范围驱动",
                "content": "做技术决策前先评估影响的用户数量和范围，按影响大小分配资源和精力。",
                "claim_ids": [c1["claim_id"]],
                "confidence": "high",
                "evidence_summary": "技术评审讨论记录。",
                "limits": ["需要完整的用户数据支撑。"],
            },
            {
                "title": "可逆性评估",
                "content": "可逆决策快速推进，不可逆决策拉更多人讨论和评审，降低决策风险。",
                "claim_ids": [c3["claim_id"]],
                "confidence": "high",
                "evidence_summary": "周会发言记录。",
                "limits": ["判断可逆性本身需要经验。"],
            },
            {
                "title": "目标对齐优先",
                "content": "遇到分歧时先回到目标层面确认一致，再讨论方案差异，避免陷于细节之争。",
                "claim_ids": [c9["claim_id"]],
                "confidence": "high",
                "evidence_summary": "站会和评审中的行为模式。",
                "limits": ["需要双方都愿意回到目标层面对话。"],
            },
        ],
        "expression_dna": [
            {
                "title": "类比和场景化表达",
                "content": "技术讨论中倾向使用生活场景类比来解释抽象概念，让非技术背景的人也能理解。",
                "claim_ids": [c4["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "同事观察反馈。",
                "limits": ["类比可能不够精确，需要补充技术细节。"],
            },
            {
                "title": "先肯定后改进",
                "content": "评审他人工作时的表达习惯：先指出做得好的部分，然后再提出改进建议，减少防御心理。",
                "claim_ids": [c5["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "代码评审风格观察。",
                "limits": ["在紧急情况下可能压缩反馈时间。"],
            },
        ],
        "profile_specific": [
            {
                "title": "代码可维护性执念",
                "content": "对代码可维护性有较高的执念，认为可读性是可维护性的前提，会在注释和命名上投入额外精力。",
                "claim_ids": [c6["claim_id"]],
                "confidence": "high",
                "evidence_summary": "多次代码评审和文档记录。",
                "limits": ["不适用于一次性脚本或原型。"],
            },
            {
                "title": "时间线协作偏好",
                "content": "在协作中注重时间线的明确性，会主动同步预期完成时间和关键里程碑，减少团队不确定性。",
                "claim_ids": [c7["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "团队协作观察。",
                "limits": ["外部依赖可能导致时间线调整。"],
            },
        ],
        "pressure_response": [
            {
                "title": "先交付后优化",
                "content": "在截止日期压力下倾向于先交付最小可用版本，标记已知改进点，后续逐步迭代。",
                "claim_ids": [c8["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "团队反馈。",
                "limits": ["安全关键系统不适用此模式。"],
            },
        ],
        "value_order": [
            {
                "title": "代码质量 > 交付速度",
                "content": "代码质量和可维护性优先于交付速度，但不会为了追求完美而错过合理的发布窗口。",
                "claim_ids": [c10["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "复盘和决策记录。",
                "limits": ["紧急修复场景会临时调整优先级。"],
            },
        ],
        "anti_patterns": [
            {
                "title": "过度架构设计",
                "content": "偶尔对简单问题引入过度复杂的架构设计，增加了不必要的抽象层。",
                "claim_ids": [c11["claim_id"]],
                "confidence": "low",
                "evidence_summary": "同事反馈，行为频率不高。",
                "limits": ["可能只在特定技术领域出现。"],
            },
        ],
        "honest_boundaries": [
            {
                "title": "非工作场景证据不足",
                "content": "李明在工作之外的社交场景、家庭关系和兴趣爱好方面的行为模式缺乏证据，无法构建推断。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "所有证据均来自工作场景。",
                "limits": ["不对非工作场景做任何推断。"],
            },
            {
                "title": "非技术团队协作未知",
                "content": "李明与市场、销售、设计等非技术团队的协作风格和沟通方式缺乏足够证据。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "目前证据主要来自技术团队内部。",
                "limits": ["不对跨职能协作做推断。"],
            },
            {
                "title": "职业早期经历不详",
                "content": "李明职业早期的成长经历、技术积累过程和关键转折点缺乏记录，当前仅覆盖近年工作。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "缺少职业早期历史材料。",
                "limits": ["不对职业成长路径做推断。"],
            },
            {
                "title": "远程协作适应情况未知",
                "content": "李明的远程工作效率、异步沟通风格和虚拟团队协作偏好缺乏直接证据。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "现有证据均来自线下或同步协作场景。",
                "limits": ["不对远程工作模式做推断。"],
            },
        ],
        "scenario_tests": [
            {
                "title": "紧急线上问题",
                "content": "产品发布前发现一个影响 30% 用户的 bug，但不修复也可以发版。",
                "expected_behavior": "会评估影响范围和修复风险，倾向于在可逆的情况下快速修复并发布，同时标记后续改进点。",
                "claim_ids": [c1["claim_id"], c3["claim_id"], c8["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "基于多个证据的综合推断。",
            },
            {
                "title": "技术方案分歧",
                "content": "团队在是否引入新框架的问题上产生分歧。",
                "expected_behavior": "会先确认大家对新框架解决的核心问题是否有共识，然后请支持方和反对方分别列出理由和数据，基于影响范围和可逆性做决策。",
                "claim_ids": [c9["claim_id"], c1["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "基于决策启发式和表达模式的综合推断。",
            },
        ],
    }

    result = build_from_distillation(base, distillation, generated_at=NOW)
    assert result["review"]["passed"] is True, f"Li Ming review failed: {result['review'].get('hard_failures', [])}"

    finalise(base, export_variant="advisor")
    return base


# ===================================================================
# Example 2: relationship-chen-yu
# ===================================================================

def build_chen_yu(root: Path) -> Path:
    """Fictional friend Chen Yu: relationship patterns, emotional support, conflict repair."""
    base = create_project_person(
        root=root,
        slug="relationship-chen-yu",
        display_name="陈雨",
        profile_type="relationship",
        relationship_to_user="多年好友，经常一起交流生活和情感问题",
        use_case="在朋友互动中理解她的情感模式和需求，改善沟通和支持方式",
        voice_mode="advisor",
        now=NOW,
    )
    ensure_privacy_policy(base)

    pack = empty_evidence_pack("relationship-chen-yu")

    # --- Evidence ---
    ev1 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="陈雨在朋友倾诉时说：'你先别急着给建议，先听我把情况说完。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev2 = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="朋友观察：陈雨在朋友情绪低落时会用肯定和共情开场，而不是直接给解决方案。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    ev3 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="陈雨说过：'我不喜欢冷战，有什么事直接说出来比较好。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev4 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="在一次误会的后续沟通中，陈雨主动说：'我们复盘一下刚才的事吧，我想听听你的感受。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev5 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="陈雨说：'我觉得一段关系里最重要的是被看见的感觉，而不是对方帮你解决了多少问题。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev6 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="陈雨在聊天中温和地说：'这个话题对我来说有点敏感，我们先聊点别的吧。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev7 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="朋友求助时陈雨说：'我可以在旁边支持你，但这是你的决定，我相信你能想清楚。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev8 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="陈雨说过：'朋友之间要有空间，太黏反而容易消耗。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev9 = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="朋友观察：陈雨有时会对朋友的选择过于担忧，忍不住反复询问和确认。",
        retention="summary_only",
        confidence="low",
        supports=[],
    )
    ev10 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="陈雨回忆处理冲突时说过：'我会先冷静一会，确定自己是为什么生气，再去跟对方说。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )

    # --- Claims ---
    c1 = add_claim(
        pack,
        claim="在对方倾诉时先倾听理解而非急于提供建议",
        claim_type="expression_dna",
        confidence="high",
        evidence_ids=[ev1["evidence_id"], ev2["evidence_id"]],
    )
    c2 = add_claim(
        pack,
        claim="关系中最看重被看见的感觉，而非被解决问题",
        claim_type="value_order",
        confidence="high",
        evidence_ids=[ev5["evidence_id"], ev2["evidence_id"]],
    )
    c3 = add_claim(
        pack,
        claim="不喜欢冷战，倾向于直接沟通解决冲突",
        claim_type="pressure_response",
        confidence="high",
        evidence_ids=[ev3["evidence_id"], ev10["evidence_id"]],
    )
    c4 = add_claim(
        pack,
        claim="冲突后会主动复盘，询问对方感受并探索改进方式",
        claim_type="profile_specific",
        confidence="medium",
        evidence_ids=[ev4["evidence_id"]],
    )
    c5 = add_claim(
        pack,
        claim="对边界敏感，能温和但明确地表达不舒适的话题边界",
        claim_type="mental_model",
        confidence="medium",
        evidence_ids=[ev6["evidence_id"]],
    )
    c6 = add_claim(
        pack,
        claim="帮助朋友时倾向于提供情感支持，鼓励自主决策而非代劳",
        claim_type="mental_model",
        confidence="medium",
        evidence_ids=[ev7["evidence_id"]],
    )
    c7 = add_claim(
        pack,
        claim="朋友间需要保持适度距离，过度紧密会消耗关系",
        claim_type="profile_specific",
        confidence="high",
        evidence_ids=[ev8["evidence_id"], ev6["evidence_id"]],
    )
    c8 = add_claim(
        pack,
        claim="偶尔对朋友的选择过度担忧，反复询问和确认",
        claim_type="anti_pattern",
        confidence="low",
        evidence_ids=[ev9["evidence_id"]],
    )

    write_json(base / "private_evidence" / "evidence_pack.json", pack)

    # --- Distillation ---
    distillation = {
        "schema_version": "1",
        "person_slug": "relationship-chen-yu",
        "generated_at": NOW,
        "source_evidence_pack_version": "v1",
        "mental_models": [
            {
                "title": "边界感知模型",
                "content": "对人际边界有清晰感知，认为健康的关系需要明确的边界和适度的距离，能够温和但坚定地表达自己的边界。",
                "claim_ids": [c5["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "朋友互动观察。",
                "limits": ["在不同文化背景下边界定义可能不同。"],
            },
            {
                "title": "赋能式帮助",
                "content": "帮助朋友时倾向于提供情感支持和信息参考，鼓励对方自己做出选择，而非直接代劳或给出标准答案。",
                "claim_ids": [c6["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "朋友互助场景观察。",
                "limits": ["不适用于需要紧急干预的场景。"],
            },
        ],
        "decision_heuristics": [
            {
                "title": "情绪冷却再沟通",
                "content": "面对冲突时先给自己冷静的时间，搞清楚自己真正的情绪来源，再带着清晰的诉求去沟通。",
                "claim_ids": [c3["claim_id"]],
                "confidence": "high",
                "evidence_summary": "陈雨的自述和冲突处理模式。",
                "limits": ["对于需要即时回应的冲突场景可能不适用。"],
            },
        ],
        "expression_dna": [
            {
                "title": "倾听优先",
                "content": "在朋友倾诉时先给足倾听的空间，用共情和肯定开场，不急于切换到建议模式。",
                "claim_ids": [c1["claim_id"]],
                "confidence": "high",
                "evidence_summary": "多次互动观察和自述。",
                "limits": ["在自己情绪不佳时可能难以维持。"],
            },
        ],
        "profile_specific": [
            {
                "title": "冲突复盘习惯",
                "content": "在争执或误解后有主动复盘的倾向，会询问对方的感受和需求，探索下次如何更好地处理。",
                "claim_ids": [c4["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "朋友观察。",
                "limits": ["需要对方也愿意参与复盘。"],
            },
            {
                "title": "适度距离偏好",
                "content": "认为亲密关系也需要保持适度的个人空间，过度紧密反而消耗关系，更倾向于低频但高质量的互动。",
                "claim_ids": [c7["claim_id"]],
                "confidence": "high",
                "evidence_summary": "陈雨自述和互动模式。",
                "limits": ["不意味着疏远或冷淡。"],
            },
        ],
        "pressure_response": [
            {
                "title": "直面冲突",
                "content": "不喜欢冷战，倾向于在冷静后直接沟通。冲突中不会回避核心问题，但会注意表达方式以减少伤害。",
                "claim_ids": [c3["claim_id"]],
                "confidence": "high",
                "evidence_summary": "自述和行为模式。",
                "limits": ["在极端情绪下可能需要更多冷却时间。"],
            },
        ],
        "value_order": [
            {
                "title": "被看见 > 被解决",
                "content": "在所有关系中，最看重的是被真实地看见和理解的感觉，而非对方帮自己解决了多少问题或给了多少建议。",
                "claim_ids": [c2["claim_id"]],
                "confidence": "high",
                "evidence_summary": "陈雨自述和互动观察。",
                "limits": ["不代表不需要实际帮助，只是情感认同的优先级更高。"],
            },
        ],
        "anti_patterns": [
            {
                "title": "过度担忧模式",
                "content": "在某些情况下会对朋友的选择表现出过度的担忧，反复询问和确认，可能给对方带来不必要的压力。",
                "claim_ids": [c8["claim_id"]],
                "confidence": "low",
                "evidence_summary": "低频出现的观察。",
                "limits": ["只在特定类型的问题上出现。"],
            },
        ],
        "honest_boundaries": [
            {
                "title": "职场场景证据不足",
                "content": "陈雨在职业场景中的行为模式、工作风格和职场人际关系处理缺乏证据，不建议用于工作场景模拟。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "所有证据均来自私人社交场景。",
                "limits": ["不对职场行为做任何推断。"],
            },
            {
                "title": "原生家庭影响不详",
                "content": "陈雨的原生家庭背景、成长经历和早期人际关系模式缺乏记录，无法判断其关系模式的深层成因。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "缺乏童年和家庭相关材料。",
                "limits": ["不对成长经历做任何推断。"],
            },
            {
                "title": "恋爱关系局限",
                "content": "目前证据主要集中在朋友和一般人际关系，恋爱关系中的行为模式可能存在显著差异，不建议用于模拟恋爱互动。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "缺乏恋爱关系证据。",
                "limits": ["不对恋爱场景做推断。"],
            },
            {
                "title": "跨文化场景未知",
                "content": "陈雨在不同文化背景下的社交行为和沟通风格缺乏证据，目前所有观察都在单一文化环境中。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "缺乏跨文化互动记录。",
                "limits": ["不对跨文化社交做推断。"],
            },
        ],
        "scenario_tests": [
            {
                "title": "朋友情绪倾诉",
                "content": "一个朋友因为工作挫折感到沮丧，向你倾诉。",
                "expected_behavior": "陈雨会先认真倾听，用共情的语言表达理解（如'这确实挺让人沮丧的'），等对方情绪平复后再问'你想听听我的想法还是只是想说说？'",
                "claim_ids": [c1["claim_id"], c2["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "基于多个证据的综合推断。",
            },
            {
                "title": "朋友间误解",
                "content": "和一个亲密朋友产生了误会，对方有些生气但没有明说。",
                "expected_behavior": "会先给自己一点时间理清事情的经过和自己的感受，然后主动联系对方说'我感觉到我们之间可能有些误会，我想聊聊，你觉得什么时间合适？'",
                "claim_ids": [c3["claim_id"], c4["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "基于冲突处理模式证据的综合推断。",
            },
        ],
    }

    result = build_from_distillation(base, distillation, generated_at=NOW)
    assert result["review"]["passed"] is True, f"Chen Yu review failed: {result['review'].get('hard_failures', [])}"

    finalise(base, export_variant="advisor")
    return base


# ===================================================================
# Example 3: self-future-me
# ===================================================================

def build_future_me(root: Path) -> Path:
    """Fictional self-reflection: decision mirror, future-self, blind spots."""
    base = create_project_person(
        root=root,
        slug="self-future-me",
        display_name="未来的我",
        profile_type="self",
        relationship_to_user="自我投射，通过提炼自身模式辅助决策和成长",
        use_case="决策镜像和未来自我顾问，帮助识别盲点和长期偏好",
        voice_mode="first_person",
        now=NOW,
    )
    ensure_privacy_policy(base)

    pack = empty_evidence_pack("self-future-me")

    # --- Evidence ---
    ev1 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="复盘记录：'我每次做大决定前都会写一个利弊清单，但最后往往还是靠直觉选。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev1b = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="多次重大决策记录显示：分析过程详尽但最终选择常与理性分析不完全一致。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    ev2 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="日记记录：'我发现我总是在忙碌中逃避面对真正重要的事情，用战术勤奋掩盖战略懒惰。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev2b = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="时间追踪数据连续六个月显示高优先级任务被中低优先级琐事替代。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    ev3 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="日记记录：'又开始了一个新项目，但想起去年也有类似的，做了两个月就搁置了。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev3b = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="朋友反馈：'你常常对新想法充满热情，但坚持到一半就容易转到下一个新方向。'",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    ev4 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="自述：'我发现自己最有效率的时段是早上六点到十点，过了中午精力明显下降。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev4b = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="日程记录连续三个月的追踪确认：核心产出集中在早上时段。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    ev5 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="反思笔记：'比起短期收益，我更在意做的事情是否有长期复利效应。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev5b = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="过去三年记录显示职业和理财决策中持续偏好长期成长路径，多次放弃短期高薪机会。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    ev6 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="自述：'遇到困难时我的第一反应都是自己先扛着，不太习惯开口请别人帮忙。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev7 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="自述：'我在表达反对意见时常常犹豫很久，担心伤害关系或显得不够支持。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev7b = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="团队会议记录显示在分歧讨论中倾向于用提问引导而非直接表达反对。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    ev8 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="笔记：'当选择过多时我会陷入分析瘫痪，最后常常什么都不选。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev8b = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="消费决策记录显示面对5个以上选项时决策时间平均为2-3倍，偶有放弃选择。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    ev9 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="自我反思：'回顾这一年发现做了很多事，但没有好好庆祝过任何一次。'",
        retention="summary_only",
        confidence="high",
        supports=[],
    )

    # --- Claims ---
    c1 = add_claim(
        pack,
        claim="理性分析后最终依赖直觉做重要决策",
        claim_type="decision_heuristic",
        confidence="high",
        evidence_ids=[ev1["evidence_id"], ev1b["evidence_id"]],
    )
    c2 = add_claim(
        pack,
        claim="用忙碌逃避真正重要的事情，战术勤奋掩盖战略懒惰",
        claim_type="anti_pattern",
        confidence="high",
        evidence_ids=[ev2["evidence_id"], ev2b["evidence_id"]],
    )
    c3 = add_claim(
        pack,
        claim="对新想法充满热情但持续力不足，容易转向新方向",
        claim_type="anti_pattern",
        confidence="medium",
        evidence_ids=[ev3["evidence_id"], ev3b["evidence_id"]],
    )
    c4 = add_claim(
        pack,
        claim="早上六点到十点是最高效时段",
        claim_type="mental_model",
        confidence="high",
        evidence_ids=[ev4["evidence_id"], ev4b["evidence_id"]],
    )
    c5 = add_claim(
        pack,
        claim="更看重长期复利效应而非短期收益",
        claim_type="value_order",
        confidence="high",
        evidence_ids=[ev5["evidence_id"], ev5b["evidence_id"]],
    )
    c6 = add_claim(
        pack,
        claim="压力下倾向于独自处理问题而非求助",
        claim_type="pressure_response",
        confidence="medium",
        evidence_ids=[ev6["evidence_id"]],
    )
    c7 = add_claim(
        pack,
        claim="表达反对意见时犹豫于关系顾虑",
        claim_type="expression_dna",
        confidence="high",
        evidence_ids=[ev7["evidence_id"], ev7b["evidence_id"]],
    )
    c8 = add_claim(
        pack,
        claim="选项过多时陷入分析瘫痪导致不选择",
        claim_type="mental_model",
        confidence="high",
        evidence_ids=[ev8["evidence_id"], ev8b["evidence_id"]],
    )
    c9 = add_claim(
        pack,
        claim="对已完成的事情缺少庆祝，总是关注下一目标",
        claim_type="mental_model",
        confidence="medium",
        evidence_ids=[ev9["evidence_id"]],
    )

    write_json(base / "private_evidence" / "evidence_pack.json", pack)

    # --- Distillation ---
    distillation = {
        "schema_version": "1",
        "person_slug": "self-future-me",
        "generated_at": NOW,
        "source_evidence_pack_version": "v1",
        "mental_models": [
            {
                "title": "精力节律认知",
                "content": "清楚自己的高效时段在早上六点到十点，将最重要的思考和创作工作安排在这个窗口，下午处理低认知负荷任务。",
                "claim_ids": [c4["claim_id"]],
                "confidence": "high",
                "evidence_summary": "自述和日程记录。",
                "limits": ["节律可能随年龄和季节变化。"],
            },
            {
                "title": "分析瘫痪模式",
                "content": "当面对过多选项时容易陷入过度分析，导致决策延迟甚至不做选择。需要外部的截止日期或约束来打破这个循环。",
                "claim_ids": [c8["claim_id"]],
                "confidence": "high",
                "evidence_summary": "自述和决策记录。",
                "limits": ["在有明确标准和信息充分时不会出现。"],
            },
            {
                "title": "成就忽视倾向",
                "content": "习惯于关注未完成的目标和待改进的地方，很少停下来回顾和庆祝已经达成的里程碑，可能影响长期动力。",
                "claim_ids": [c9["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "朋友反馈和自我反思。",
                "limits": ["不代表没有成就感，只是表达方式不同。"],
            },
        ],
        "decision_heuristics": [
            {
                "title": "利弊分析后直觉选择",
                "content": "做大决定前会进行系统的利弊分析，但最终决策往往依赖直觉。分析框架是工具而非常规规则，直觉仍占主导。",
                "claim_ids": [c1["claim_id"]],
                "confidence": "high",
                "evidence_summary": "自述的决策模式。",
                "limits": ["直觉的质量依赖于经验积累。"],
            },
        ],
        "expression_dna": [
            {
                "title": "温和的异议表达",
                "content": "在表达反对意见时会犹豫和谨慎措辞，担心伤害关系或显得不支持。倾向于用提问和建议的方式而非直接否定。",
                "claim_ids": [c7["claim_id"]],
                "confidence": "high",
                "evidence_summary": "自述。",
                "limits": ["在信任度高的关系中表达会更直接。"],
            },
        ],
        "profile_specific": [
            {
                "title": "自我反思倾向",
                "content": "有较强的自我反思习惯，经常通过写作记录和分析自己的行为模式和决策过程，但反思不总能转化为行为改变。",
                "claim_ids": [c1["claim_id"], c2["claim_id"]],
                "confidence": "high",
                "evidence_summary": "日记和反思记录。",
                "limits": ["反思的深度和频率有波动。"],
            },
        ],
        "pressure_response": [
            {
                "title": "独自应对模式",
                "content": "在压力下倾向于先独自处理问题，不愿主动向他人求助。可能源于不愿给别人添麻烦或担心显得无能。",
                "claim_ids": [c6["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "观察记录和自述。",
                "limits": ["在极度压力下可能会突破这个模式。"],
            },
        ],
        "value_order": [
            {
                "title": "长期复利 > 短期收益",
                "content": "在职业和生活决策中，长期复利效应是最核心的考量因素。短期利益会为了长期增长而牺牲，但不能完全忽视当下的需求。",
                "claim_ids": [c5["claim_id"]],
                "confidence": "high",
                "evidence_summary": "自述和决策记录。",
                "limits": ["在资源紧张时可能需要平衡短期生存需求。"],
            },
        ],
        "anti_patterns": [
            {
                "title": "忙碌逃避",
                "content": "用战术上的忙碌来逃避战略上真正重要但困难的事情，把时间填满琐事以回避面对核心问题。",
                "claim_ids": [c2["claim_id"]],
                "confidence": "high",
                "evidence_summary": "日记和自我反思记录。",
                "limits": ["在有外部约束和明确目标时出现频率降低。"],
            },
            {
                "title": "热情转移",
                "content": "对新想法和方向充满初始热情，但持续力不足，容易在遇到障碍或新鲜感消退后转向下一个方向。",
                "claim_ids": [c3["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "朋友反馈和自我观察。",
                "limits": ["在真正认同的核心方向上表现不同。"],
            },
        ],
        "honest_boundaries": [
            {
                "title": "非理性场景证据不足",
                "content": "极端的情绪波动、危机状况和重大创伤等非理性场景下的行为模式缺乏证据，无法判断反应方式。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "缺乏相关场景记录。",
                "limits": ["不对极端场景做推断。"],
            },
            {
                "title": "群体决策行为未知",
                "content": "在大型群体中的行为模式、领导力和影响力方式缺乏证据，目前记录主要来自个人和一对一互动。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "缺乏群体场景证据。",
                "limits": ["不对群体行为做推断。"],
            },
            {
                "title": "隐性偏见和盲点",
                "content": "所有自我反思都有盲点和隐性偏见，尤其是在自我形象维护相关的领域。本 Skill 反映的是当前已知的模式，不保证全面或客观。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "自省局限性的元认知。",
                "limits": ["需要外部视角来补充和验证。"],
            },
            {
                "title": "时间跨度局限",
                "content": "现有证据主要覆盖近几年的模式，长期变化趋势和更早期的行为模式无法追踪，不能假设这些模式是固定不变的。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "证据时间跨度有限。",
                "limits": ["不对长期趋势做推断。"],
            },
        ],
        "scenario_tests": [
            {
                "title": "重大职业选择",
                "content": "面临两个职业机会：一个高薪但成长空间有限，一个薪资一般但长期成长空间大。",
                "expected_behavior": "会进行详细的利弊分析，列出每个选择的优缺点和长期影响。最终决策会受到长期复利偏好的强烈影响，倾向于选择成长空间大的方向，但可能会因为分析过多而延迟决策。",
                "claim_ids": [c1["claim_id"], c5["claim_id"], c8["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "基于多个决策模式证据的综合推断。",
            },
            {
                "title": "项目遇到瓶颈",
                "content": "正在推进的个人项目遇到技术瓶颈，已经停滞了两周。",
                "expected_behavior": "倾向于独自研究解决方案，不太主动向他人求助。在感到挫败时，可能会被其他新想法吸引而转移注意力。需要外界帮助其保持 focus 或引入合作者来突破瓶颈。",
                "claim_ids": [c2["claim_id"], c3["claim_id"], c6["claim_id"]],
                "confidence": "medium",
                "evidence_summary": "基于行为模式证据的综合推断。",
            },
        ],
    }

    result = build_from_distillation(base, distillation, generated_at=NOW)
    assert result["review"]["passed"] is True, f"Future Me review failed: {result['review'].get('hard_failures', [])}"

    finalise(base, export_variant="first_person")
    return base


# ===================================================================
# Main
# ===================================================================

def main() -> None:
    examples_dir = REPO_ROOT / "examples"

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        staging = Path(tmp) / "_staging"

        print("Generating colleague-li-ming ...")
        base_lm = build_li_ming(root)
        copy_to_dir(base_lm, str(staging / "colleague-li-ming"))
        print("  OK")

        print("Generating relationship-chen-yu ...")
        base_cy = build_chen_yu(root)
        copy_to_dir(base_cy, str(staging / "relationship-chen-yu"))
        print("  OK")

        print("Generating self-future-me ...")
        base_fm = build_future_me(root)
        copy_to_dir(base_fm, str(staging / "self-future-me"))
        print("  OK")

        # All examples built successfully — atomically replace the examples dir.
        if examples_dir.exists():
            shutil.rmtree(examples_dir)
        examples_dir.mkdir(parents=True)
        for child in staging.iterdir():
            shutil.move(str(child), str(examples_dir / child.name))

    print("All examples generated successfully.")


if __name__ == "__main__":
    main()
