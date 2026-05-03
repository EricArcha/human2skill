# human2skill — 把一个人变成可复用的视角顾问

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-132%20passed-brightgreen)](https://github.com/EricArcha/human2skill/actions)
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/EricArcha/human2skill/blob/main/CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![AgentSkills](https://img.shields.io/badge/standard-AgentSkills-orange)](https://agentskills.io)

[English](README.en.md)

把你熟悉的一个人，提炼成一个可复用的**视角顾问 Skill**。

它不是让 AI 冒充某个人，而是把有限材料、你的观察和一轮轮追问，整理成一份可安装的 `SKILL.md`：当你遇到问题时，可以请它从那个人的思维方式、表达习惯、判断偏好和已知边界出发，帮你换一个角度看。

比如：

```text
你：用李明的视角帮我看这份技术方案。
李明视角顾问：他大概率会先问三个问题：
1. 这个方案解决的是不是当前最痛的问题？
2. 有没有更小的验证路径？
3. 三个月后别人接手时，能不能看懂这里为什么这样设计？

如果按他的偏好，他会建议先砍掉两个不必要的抽象层，
把风险点写进迁移计划。
但我没有足够证据判断他在安全合规问题上的取舍，这里需要你再补充材料。
```

## 它适合什么场景？

**同事和合作者**

想保留一个人的工作方法、评审风格和决策习惯。比如"某位资深同事离职了，但我还想用他的视角检查技术方案"。

**朋友、伴侣和家人**

不是替你操控关系，而是帮你理解对方可能怎么接收一段话、什么地方容易误会、哪些判断证据不足。

**导师、专家和顾问**

把一个人长期给你的建议、反馈和判断方式沉淀下来，让它在新问题里继续提供参考。

**自己和未来的自己**

把你的原则、反模式、长期目标和复盘结论做成 Skill。遇到选择时，请"更清醒的自己"提醒现在的你。

## 它产出什么？

human2skill 最终会生成两类东西：

```text
outputs/{slug}/
  public_skill/
    SKILL.md                  # 可安装、可分享的公开 Skill
    SKILL.first_person.md      # 可选：自用第一人称版本
  private_evidence/
    source_index.json          # 私有材料索引
    evidence_pack.json         # 结构化证据包
    distillation.json          # agent 辅助提炼结果
    reviews/                   # 质量和隐私评审
  corpus/                      # 原文归档（本地保留，用于验证）
  exports/                     # 面向不同宿主的导出结果
```

公开 Skill 是轻量的：它只保留摘要化的思维模型、表达 DNA、决策启发式、反模式和诚实边界。

**私有材料留在本地 evidence pack 里，不会默认进入可分发的 `SKILL.md`。** 这是 human2skill 和其他"人格模拟"工具最重要的区别。

## 它蒸馏的不是"像不像"，而是"怎么想"

一个有用的人物 Skill 不应该只会复读口头禅。human2skill 更关注五层内容：

| 层次 | 它会提炼什么 |
| --- | --- |
| 思维模型 | 这个人习惯怎样拆问题、找关键变量、判断优先级 |
| 表达 DNA | 这个人怎样解释、反馈、反驳、安慰或推进讨论 |
| 决策启发式 | 他在信息不完整时通常怎么做取舍 |
| 反模式 | 他容易过度使用、误判或不适用的模式 |
| 诚实边界 | 哪些事情证据不足，不能装作知道 |

所以它默认是"视角顾问"，不是"我就是某某"。它会提醒你：哪些判断来自证据，哪些只是低置信度推断。

## 快速开始

选择你使用的 AI 工具：

**Claude Code**

```bash
git clone https://github.com/EricArcha/human2skill.git ~/.claude/skills/human2skill
```

**OpenClaw**

```bash
git clone https://github.com/EricArcha/human2skill.git ~/.openclaw/skills/human2skill
```

然后输入 **human2skill** 即可启动。首次使用需 Python 3.11+，Agent 会自动检测并提示。

触发词（Claude Code 和 OpenClaw 通用）：

- `human2skill`
- `人物蒸馏`
- `创建人物 Skill`
- `更新人物视角`

启动后，meta-skill 会引导你走完完整流程：确认人物 → 摄入语料 → 自适应访谈 → 构建证据 → 蒸馏 → 构建 Skill → 验证 → 导出。

## 路线图

| 阶段 | 状态 |
|------|------|
| P0-P2 核心管线（摄入、访谈、证据、蒸馏、构建、评审、导出） | ✅ 已完成 |
| Phase 化工作流 + 3 个强制检查点 + 人类在回路 | ✅ 已完成 |
| 4 层验证漏斗 + 自动化品质检查 | ✅ 已完成 |
| P3 多人物交叉视角、公开人物语料库、Web UI | 🔜 规划中 |

---

## 开发者入口

human2skill 也是一个 Python CLI，是 meta-skill 工作流底层工具。

```bash
# 安装开发环境
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# 运行测试
.venv/bin/python -m pytest
```

开发细节见 [CLAUDE.md](CLAUDE.md)，规则体系见 [docs/GOVERNANCE.md](docs/GOVERNANCE.md)，版本变更见 [CHANGELOG.md](CHANGELOG.md)。

仓库包含三个示例人物（`examples/` 目录），每个都包含完整的私有证据、公开 Skill、评审报告和版本快照。


---

> Created by [Eric](https://github.com/EricArcha) · [human2skill](https://github.com/EricArcha/human2skill)

