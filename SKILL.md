---
name: human2skill
description: 将有限语料和自适应访谈蒸馏为可复用的人物视角顾问 Skill。触发词：human2skill、人物蒸馏、创建人物 Skill、更新人物视角。
user-invocable: true
license: MIT
compatibility: requires Python 3.11+; pip install git+https://github.com/EricArcha/human2skill.git
---

<!-- ⚠️ CANONICAL — single source of truth. -->

# human2skill 人物视角蒸馏

> 将私人/身边人的有限语料和自适应访谈，蒸馏为可复用的人物视角顾问 Skill。
> 触发词：**human2skill** / **人物蒸馏** / **创建人物 Skill**

---

## 定位

human2skill 是人物视角蒸馏的编排工具。产物是 `public_skill/SKILL.md`（可分发视角顾问）+ `private_evidence/`（私有证据包）+ `corpus/`（原文归档）。

不做角色扮演，不冒充本人，不输出私域原文。

---

## 产物目录结构

```
outputs/{slug}/
├── person.meta.json
├── corpus/                          # 原文归档层
│   ├── raw/                         # 原始语料（脱敏后）
│   └── index.json                   # 原文索引
├── public_skill/
│   ├── SKILL.md                     # {slug}-lens
│   └── SKILL.first_person.md
├── private_evidence/
│   ├── evidence_pack.json
│   ├── source_index.json
│   ├── distillation.json
│   ├── interviews/
│   ├── reviews/
│   └── changelog/
├── exports/
│   ├── claude-code/
│   ├── codex/
│   ├── openclaw/
│   └── hermes/
└── versions/
    ├── v1/
    └── v2/
```

---

## 执行流程（Phase 0 — Phase 5）

流程采用 Phase 化设计，3 个强制检查点需要用户确认才能推进。
**绝对不可跳过任何 Phase 或 Checkpoint。迭代上限 2 轮。**

---

### Phase 0: 入口分流

收集以下信息：

1. **人物称呼/slug**：英文小写，连字符分隔

**收到 slug 后，Agent 首先检查 `outputs/{slug}/` 是否存在**（`human2skill status --root . --slug {slug}`）。

→ **不存在** → 继续以下步骤 2-6 的新建流程。

→ **已存在** → 展示项目概况，让用户选择：

```
检测到已有项目：
- 版本: v{N}
- 创建时间: {created_at}
- 心智模型: N 个
- 语料来源: N 条

你想做什么？
A. 补充新语料 — 有新聊天记录、文档等素材
B. 纠正现有信息 — 某些描述不准，需要修改
C. 两者都有
D. 从头重建（保留旧版本快照）
```

选 A/B/C → 跳转到**增量更新模式**。选 D → Agent 先调 `human2skill build` 备份当前版本（会自动快照），再走新建流程（新版 `create` 支持 `--force` 覆盖）。

2. **与用户的关系**：同事/朋友/导师/自己
3. **用途描述**：这个 Skill 用来做什么决策或分析
4. **Profile 类型**：从四类 Preset 中选择

| Profile | 适用对象 | CLI 参数 |
| --- | --- | --- |
| colleague | 同事、上级、下级、客户 | `--profile colleague` |
| relationship | 朋友、伴侣、父母、子女 | `--profile relationship` |
| mentor | 导师、老师、顾问、专家 | `--profile mentor` |
| self | 自己、过去的自己 | `--profile self` |

若未明确指定，Agent 根据关系描述关键词自动推断。

5. **语气模式**（若不指定则按 profile 自动推断）：

| 模式 | 产物文件 | 用途 |
| --- | --- | --- |
| advisor | `SKILL.md` | 第三人称视角顾问，以观察者身份提供视角分析（同事/导师默认） |
| first_person | `SKILL.first_person.md` | 沉浸式第一人称，首次激活说一次免责声明后全程自然对话（自己/亲友默认） |

自动推断规则：`self` / `relationship` → first_person；`colleague` / `mentor` → advisor。用户可通过 `--voice-mode` 覆盖。

6. **隐私配置确认**：Agent 在创建前向用户确认隐私策略。

默认隐私策略：
- **留存模式**: `summary_only` — 保留摘要，不存原文
- **公开 Skill 可含脱敏引用**: first_person 模式默认启用有限原话引用（≤280 字符，经 PII 扫描）；advisor 模式可选
- **默认不要求本人同意**: person_consented 默认 false
- **默认不分发**: distribution_allowed 默认 false

---

### Phase 0.5: 创建项目目录（仅新建流程）

**增量更新模式不执行此 Phase。以下仅适用于新建项目。**

**收到确认后立即执行**，在调研之前完成。

Agent 调用 `human2skill create` 初始化目录：

```bash
human2skill create --root . --slug zhang-san --name "张三" \
  --profile colleague --relationship "coworker" \
  --use-case "work perspective advisor" --voice-mode advisor
```

此步骤创建 `outputs/{slug}/` 下的完整目录布局、`person.meta.json`、空证据包和空来源索引。

---

### Phase 1: 信息收集

Agent 在开始前向用户展示三个选项：

> **在开始蒸馏之前，我有三种方式收集信息：**
>
> **A. 提供语料** — 你有聊天记录、会议纪要、笔记等材料，我帮你导入分析
> **B. 20 问快答** — 我来问你最多 20 个问题，你逐一回答（适合本人蒸馏，随时可以 `done` 结束）
> **C. 直接描述** — 你直接告诉我这个人的特点、习惯、思维方式，我来帮你整理成结构化描述
>
> 你想选哪个？（也可以组合使用）

快捷入口：用户说 `/human2skill Q20` 直接跳到 B（20 问快答），跳过 A 和 C。

#### 1.1 语料摄入

Agent 接收用户提供的语料：
- 直接粘贴的文本
- Markdown/TXT 文件
- PDF 文件（会议纪要、聊天导出等）

调用 `human2skill ingest` 将文件归档：

```bash
human2skill ingest --root . --slug zhang-san --file ./notes/meeting.pdf
```

**规则**：
- 每条来源记录 `source_id`、摘要和留存策略
- 原始文本自动保存到 `corpus/raw/{source_id}.txt`
- PII 扫描程序化执行：发现身份证、手机号、完整聊天记录等敏感信息立即停止，提示用户脱敏

#### 1.2 自适应访谈（可选，非强制）

Agent 分析当前信息覆盖度（10 个维度），对缺口维度启动追问。也可通过 CLI 直接运行交互式循环：

```bash
human2skill interview --root . --slug zhang-san --profile colleague --perspective observer_answer
```

交互规则：每轮显示问题 → 用户输入回答（多行以空行结束）→ 下一轮。输入 `skip` 跳过、`done` 提前结束。回答自动保存到 `private_evidence/interviews/`。

1. identity_context — 基本身份与关系语境
2. mental_models — 核心思维模型
3. expression_dna — 表达 DNA
4. decision_heuristics — 决策启发式
5. pressure_response — 压力和冲突反应
6. profile_specific — Profile 专项维度
7. honest_boundaries — 已知边界和盲区
8. evaluation_scenarios — 可用于评估的历史场景
9. value_order — 价值排序
10. anti_patterns — 反模式

**访谈预算：20 轮硬限制**。达到上限后必须进入 Checkpoint A，由用户决定是否延展。

Agent 将访谈记录写入 `private_evidence/interviews/interview-YYYYMMDD-HHMM.md`。

---

### ⛔ Checkpoint A — 覆盖率审查

**Agent 必须在此暂停，展示覆盖率摘要，等待用户确认后才能继续。**

> 用户可以输入：y（继续）/ 补充信息 / 降级确认

也可通过 CLI 查看：
```bash
human2skill check-coverage --root . --slug zhang-san
```

展示格式：

```
覆盖率摘要：
┌──────────────────────┬──────────┬──────────┐
│ 维度                 │ 覆盖度   │ 来源数    │
├──────────────────────┼──────────┼──────────┤
│ identity_context     │ high     │ 5        │
│ mental_models        │ medium   │ 3        │
│ expression_dna       │ high     │ 4        │
│ ...                  │ ...      │ ...      │
│ honest_boundaries    │ medium   │ 2        │
└──────────────────────┴──────────┴──────────┘
维度覆盖: 6/10 ≥ medium | 诚实边界: 已标注 | 状态: ✅ 满足进入蒸馏条件
```

通过标准：≥4 维度达到 medium/high，且 honest_boundaries 至少有一条低置信度声明。

不满足 → 继续访谈或用户签署降级确认。

---

### Phase 2: 证据构建 + 蒸馏

#### 2.1 构建证据包

Agent 将语料和访谈转为结构化证据，写入 `private_evidence/evidence_pack.json`。

证据三层分级：

| 层级 | 来源类型 | 权重 |
| --- | --- | --- |
| L1 | direct_quote_or_behavior（原话/行为记录） | 3 |
| L2 | observer_report（观察者描述） | 2 |
| L3 | model_inference（模型推断） | 1 |

每条 evidence 包含 `evidence_id`、`source_summary`、`retention`、`confidence`、`supports` 和 `conflicts_with`。

**规则**：若一条 claim 的置信度高于其 evidence 的组合支持等级，标记为 overconfident。

#### 2.2 编写蒸馏声明

Agent 编写 `private_evidence/distillation.json`，包含 9 个章节：mental_models、expression_dna、decision_heuristics、profile_specific、pressure_response、value_order、anti_patterns、honest_boundaries、scenario_tests。

**蒸馏质量要求**：
- 心智模型优先使用三重验证：跨场景复现、能推断新问题立场、有此人特异性
- 未通过三重验证的观点降级为启发式或低置信度观察
- `honest_boundaries` 至少 3 条
- 所有 `scenario_tests` 必须包含 `expected_behavior` 字段
- 每个非 `honest_boundaries` 项必须有至少一个 `claim_id`
- 可选 `quote` 字段（≤280 字符）：收录此人原话，用于增强真实感和可验证性。first_person 模式建议每个心智模型至少附一条 quote

---

### ⛔ Checkpoint B — 蒸馏确认

**Agent 必须在此暂停，展示蒸馏摘要，等待用户确认后才能继续。**

> 用户可以输入：y（继续）/ 修改具体条目 / 回到 Phase 1 补充信息

展示格式：

```
蒸馏结果摘要：
- 心智模型: 5个（增量优化、数据锚定、信号驱动、跨文化协作、技术思维）
- 决策启发式: 5条
- 表达DNA: 4项（高频共情、问题引导、认可同事、数据锚定）
- 诚实边界: 5条
- 场景测试: 3个（历史/反事实/边界各1）
- 内在张力: 需要≥2处（当前可能不足）
```

提炼是主观判断最重的环节，确认后再构建，避免写完才发现方向不对。

---

### Phase 3: 构建 Skill

Agent 调用 `human2skill build` 从蒸馏声明生成 Skill：

```bash
human2skill build --root . --slug zhang-san
```

此命令执行：
1. 校验 `distillation.json` schema 和 claim-id 完整性（Layer 1）
2. 检测 overconfident claims
3. 运行场景测试回放（Layer 2）
4. 收集签名语录 + 关键引用（从含 `quote` 字段的条目中提取）
5. 渲染 Skill 变体（advisor 第三人称观察 / first_person 沉浸式第一人称）并写入 `public_skill/`
6. 运行结构化评审（7 维度评分，confidence_calibration ≥5 为必须）
7. 写入评审报告和场景报告到 `private_evidence/reviews/`
8. 快照版本到 `versions/v{n}/`（仅当全部通过）

Skill 命名格式：`{slug}-lens`

---

### Phase 4: 独立验证

#### 4.1 自动化品质检查

运行 `scripts/quality_check.py` 对生成的 SKILL.md 执行 7 项检查：

| 检查项 | 通过标准 |
|--------|---------|
| 心智模型数量 | 3-7 个，每个有 claim_id 来源 |
| 每个模型的局限 | 明确写出失效条件（限制: 非空） |
| 表达 DNA 辨识度 | ≥3 项特征标记 |
| 诚实边界 | ≥3 条具体局限 |
| 内在张力 | ≥2 处矛盾/冲突 |
| 一手来源占比 | >50%。优先读取 `corpus/index.json` 中的真实来源类型统计；无 corpus 时回退到 SKILL.md 关键词匹配 |
| 原文归档 | `corpus/index.json` 存在且每个来源有对应原文文件 |

```bash
.venv/bin/python scripts/quality_check.py outputs/zhang-san/public_skill/SKILL.md
```

#### 4.2 独立 sub-agent 验证

启动独立 sub-agent 执行 3 项行为测试：
1. **已知测试**：选 3 个用户确认过的问题，对比 Skill 回答与实际立场
2. **边缘测试**：选 1 个未知问题，验证 Skill 表现出不确定性而非斩钉截铁
3. **风格测试**：撰写 100 字分析，验证表达 DNA 是否可识别、不像通用 AI

---

### ⛔ Checkpoint C — 验证确认

**Agent 展示验证结果表格，等待用户确认后才算完成。**

> 用户可以输入：y（完成）/ 回到 Phase 2 调整（最多 2 轮迭代）/ 降级交付当前版本

展示格式：

```
验证结果：
┌──────────────────────┬──────────┬──────────────────────────┐
│ 检查项               │ 结果     │ 备注                     │
├──────────────────────┼──────────┼──────────────────────────┤
│ quality_check.py     │ 5/6 PASS │ 内在张力不足             │
│ 已知测试 #1          │ PASS     │ 方向一致                 │
│ 已知测试 #2          │ PASS     │ 方向一致                 │
│ 已知测试 #3          │ PASS     │ 细节略有偏差             │
│ 边缘测试             │ PASS     │ 正确表达不确定性         │
│ 风格测试             │ PASS     │ DNA辨识度高              │
└──────────────────────┴──────────┴──────────────────────────┘
```

不通过 → 回到 Phase 2 调整，最多 2 轮迭代。超过 2 轮 → 交付当前版本并标注局限性。

---

### Phase 5: 导出 + 交付

导出可分发 Skill：

```bash
human2skill export --root . --slug zhang-san --host claude-code --variant advisor
```

安装：

```bash
human2skill install --export outputs/zhang-san/exports/claude-code --target ~/.claude/skills --name zhang-san-lens
```

产物交付清单：
- `public_skill/SKILL.md` — 可分发、可安装的视角顾问 Skill
- `public_skill/SKILL.first_person.md` — 自用第一人称版本（若启用）
- `private_evidence/` — 私有证据包（本地保留，不分发）
- `corpus/` — 原文归档（本地保留，用于验证对照）

---

## 增量更新模式

当 Phase 0 检测到 slug 已存在且用户选择 A/B/C 时，进入此模式。

**核心原则**：不重写整个 Skill，只增量更新。每次更新生成新版本快照，旧版本可回溯。

---

### Step 0: 确认更新范围

读取 `person.meta.json` 和 `distillation.json`，展示当前项目概况：

```
项目概况：
- 版本: v{N}
- 心智模型: {名称列表}
- 决策启发式: N 条
- 表达DNA: {特征列表}
- 诚实边界: N 条
- 场景测试: N 个

更新范围：
A. 全部章节 — 新语料可能影响多个维度
B. 特定心智模型 — 只更新选定的模型
C. 特定章节 — 如只补充场景测试或诚实边界
```

---

### Step 1: 备份当前版本

Agent 在更新任何内容前先备份：

```bash
# 查询当前版本号
human2skill status --root . --slug {slug}
```

备份机制：后续 `build` 会自动将当前版本快照到 `versions/v{n}_before_update/`，保护更新前的关键文件（`person.meta.json`、`distillation.json`、`evidence_pack.json`）。

---

### Step 2: 收集新信息

同 Phase 1 的三个入口，但语境变为"增量补充"：

> **有新材料了？告诉我你想怎么补充：**
>
> **A. 提供新语料** — 有新聊天记录、会议纪要、笔记等，我帮你追加到现有证据包
> **B. 直接纠正** — 告诉我现有描述哪里不对，我来修改
> **C. 新维度问答** — 针对某个缺口维度，我追问几个问题

选 A → 调用 `human2skill ingest` 追加：
```bash
human2skill ingest --root . --slug {slug} --file ./new-material.pdf
```

选 B → Agent 记录纠正内容，对应更新 distillation 条目。

选 C → 同自适应访谈，只针对指定维度追问。

---

### Step 3: 冲突检测

Agent 分析新证据/纠正 vs 现有 claims：

| 情况 | 处理方式 |
|------|---------|
| **强化** | 补充案例，标注 confidence 提升 |
| **矛盾** | 标记 conflict，展示给用户决策（保留旧版本 / 更新为新 / 两者共存标注时间） |
| **新维度** | 新增 claim 和对应的 evidence |
| **无关** | 忽略 |

发现矛盾时展示冲突表格：

```
冲突检测：
┌──────────┬──────────┬──────────────────────────────┐
│ 现有声明 │ 新证据   │ 处理方式                     │
├──────────┼──────────┼──────────────────────────────┤
│ 模型X    │ 材料A    │ ✅ 强化 — 补充案例            │
│ 模型Y    │ 材料B    │ ⚠️ 矛盾 — 需要你决定          │
│ —        │ 材料C    │ 🆕 新维度 — 新增 claim        │
└──────────┴──────────┴──────────────────────────────┘
```

**冲突停止规则**：若检测到 `halt_for_review` 级矛盾，Agent 必须向用户报告并等待人工裁决。

---

### Step 4: 更新蒸馏声明

在现有 `distillation.json` 基础上增量修改：

- 强化 → 在现有心智模型条目追加新案例
- 矛盾 → 修改条目并在描述末尾标注 `[已更新: YYYY-MM-DD]`
- 新维度 → 新增节和 claim
- 诚实边界 → 有新局限发现则补充

更新后展示变更摘要让用户确认，再进入下一步。

---

### Step 5: 重建 + 版本快照

```bash
human2skill build --root . --slug {slug}
```

`build` 命令自动：
- 校验 schema 和 claim-id 完整性
- 检测 overconfident claims
- 运行场景测试回放
- 渲染 Skill 变体并写入 `public_skill/`
- 运行结构化评审
- **版本号递增**（v1 → v2 → v3...）
- **快照版本到 `versions/v{n}/`**（仅当全部通过）

---

### Step 6: 评审 + 交付

同标准 Phase 4/5 评审流程。特别关注：
- 更新是否引入了新的 overconfident claims
- 更新前后的表达风格是否一致
- 新版本的诚实边界是否覆盖了新增局限

迭代上限同标准流程：最多 2 轮调整，之后交付当前最佳版本。

---

## 强制规则

1. **不输出未经脱敏的完整私域原文** — 默认 `summary_only`，但 first_person 模式允许 ≤280 字符的脱敏原话引用
2. **沉浸式第一人称（first_person）** — 首次激活说一次免责声明，之后全程自然对话；advisor 模式保持第三人称观察
3. **区分已证实和推断** — 每项结论标注 confidence 和 evidence_summary
4. **诚实标注边界** — 证据不足时不强行推断，写入 honest_boundaries
5. **版本化管理** — 每次构建生成版本快照，允许回滚
6. **评审必须通过** — Phase 4 全部通过不得交付 Skill
7. **隐私停止规则** — 发现敏感个人信息立即停止，不继续处理
8. **不可跳过 Phase** — 每个 Phase 必须完成，3 个 Checkpoint 必须用户确认
9. **迭代上限 2 轮** — Phase 2-4 循环最多 2 次，之后交付当前最佳版本
10. **语料必须归档** — 所有原始语料存入 corpus/raw/，脱敏后保留用于验证

## 禁止事项

- 不生成冒充本人的 Skill（first_person 模式首次激活说免责声明，之后沉浸但不冒充）
- 不输出身份证号、手机号、完整私聊记录等未经脱敏的私域原文
- 不替用户操控与目标人物的关系
- 不在无证据支持下宣称高置信度
- 不跳过评审直接交付
- 不在矛盾未解决时强行合入新版本
- 不跳过任何 Checkpoint 自动推进
- 不为通过质量检查而编造 quote、引用或来源

---

## 相关文件

- `pyproject.toml` — Python 包配置与 CLI 入口
- `src/human2skill/` — 核心 Python 模块
- `scripts/quality_check.py` — 自动化品质检查
- `schemas/` — 数据 schema（person.meta、evidence_pack、distillation），位于 `src/human2skill/schemas/`
- `templates/profiles/` — 四类 Profile Preset，位于 `src/human2skill/templates/profiles/`
- `templates/skill/` — Skill 渲染模板，位于 `src/human2skill/templates/skill/`


---

> Created by [Eric](https://github.com/EricArcha) · [human2skill](https://github.com/EricArcha/human2skill)

