---
name: human2skill
description: 将有限语料和自适应访谈蒸馏为可复用的人物视角顾问 Skill。触发词：human2skill、人物蒸馏、创建人物 Skill、更新人物视角。
user-invocable: true
---

<!-- ⚠️ CANONICAL: This is the canonical meta-skill source. Distribution copies in exports/. -->

# human2skill 人物视角蒸馏

> 将私人/身边人的有限语料和自适应访谈，蒸馏为可复用的人物视角顾问 Skill。
> 触发词：**human2skill** / **人物蒸馏** / **创建人物 Skill**

---

## 定位

本 Meta-skill 是人物视角蒸馏的编排工具。产物是 `public_skill/SKILL.md`（可分发视角顾问）+ `private_evidence/`（私有证据包）+ `corpus/`（原文归档）。

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

5. **语气模式**：

| 模式 | 产物文件 | 用途 |
| --- | --- | --- |
| advisor | `SKILL.md` | 第三人称视角顾问（默认），以观察者身份提供视角分析 |
| first_person | `SKILL.first_person.md` | 第一人称视角自用，用于自我反思和决策镜像 |

6. **隐私配置确认**：Agent 在创建前向用户确认隐私策略。

默认隐私策略：
- **留存模式**: `summary_only` — 保留摘要，不存原文
- **公开 Skill 不包含私域原文**: public_skill_allows_private_quotes 强制为 false
- **默认不要求本人同意**: person_consented 默认 false
- **默认不分发**: distribution_allowed 默认 false

---

### Phase 0.5: 创建项目目录

**收到确认后立即执行**，在调研之前完成。

Agent 调用 `human2skill create` 初始化目录：

```bash
human2skill create --root . --slug zhang-san --name "张三" \
  --profile colleague --relationship "coworker" \
  --use-case "work perspective advisor" --voice-mode advisor
```

此步骤创建 `outputs/{slug}/` 下的完整目录布局、`person.meta.json`、空证据包和空来源索引。

---

### Phase 1: 语料摄入 + 自适应访谈

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

#### 1.2 自适应访谈

Agent 分析当前信息覆盖度（10 个维度），对缺口维度启动追问：

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

**Agent 必须在此暂停，展示覆盖率摘要，等待用户确认。**

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

---

### ⛔ Checkpoint B — 蒸馏确认

**Agent 必须在此暂停，展示蒸馏摘要，等待用户确认。**

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
4. 渲染 Skill 变体（advisor + first_person）并写入 `public_skill/`
5. 运行结构化评审（7 维度评分，confidence_calibration ≥5 为必须）
6. 写入评审报告和场景报告到 `private_evidence/reviews/`
7. 快照版本到 `versions/v{n}/`（仅当全部通过）

Skill 命名格式：`{slug}-lens`

---

### Phase 4: 独立验证

#### 4.1 自动化品质检查

运行 `scripts/quality_check.py` 对生成的 SKILL.md 执行 6 项检查：

| 检查项 | 通过标准 |
|--------|---------|
| 心智模型数量 | 3-7 个，每个有 claim_id 来源 |
| 每个模型的局限 | 明确写出失效条件（限制: 非空） |
| 表达 DNA 辨识度 | ≥3 项特征标记 |
| 诚实边界 | ≥3 条具体局限 |
| 内在张力 | ≥2 处矛盾/冲突 |
| 一手来源占比 | >50%（当有 corpus 时） |

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

## 增量更新流程

1. 提供新语料，调用 `human2skill ingest` 追加
2. Agent 分析新证据对现有 claims 的影响（强化、矛盾、无关）
3. 若发现矛盾，记录到 `evidence_pack.json` 的 `conflicts` 数组中
4. 更新 `distillation.json` 中受影响的条目
5. 重新调用 `human2skill build`，生成新版本
6. 版本快照保存到 `versions/v{n}/`

**冲突停止规则**：若检测到矛盾且 `resolution` 设为 `halt_for_review`，构建中止，Agent 必须向用户报告冲突并等待人工裁决。

---

## 强制规则

1. **不输出私域原文** — 默认为 `summary_only`，原始语料不进入可分发 Skill
2. **不做角色扮演** — 生成 Skill 以"视角顾问"方式回答，不声称是本人
3. **区分已证实和推断** — 每项结论标注 confidence 和 evidence_summary
4. **诚实标注边界** — 证据不足时不强行推断，写入 honest_boundaries
5. **版本化管理** — 每次构建生成版本快照，允许回滚
6. **评审必须通过** — Phase 4 全部通过不得交付 Skill
7. **隐私停止规则** — 发现敏感个人信息立即停止，不继续处理
8. **不可跳过 Phase** — 每个 Phase 必须完成，3 个 Checkpoint 必须用户确认
9. **迭代上限 2 轮** — Phase 2-4 循环最多 2 次，之后交付当前最佳版本
10. **语料必须归档** — 所有原始语料存入 corpus/raw/，脱敏后保留用于验证

## 禁止事项

- 不生成冒充本人的 Skill
- 不输出身份证号、手机号、完整私聊记录等私域原文
- 不替用户操控与目标人物的关系
- 不在无证据支持下宣称高置信度
- 不跳过评审直接交付
- 不在矛盾未解决时强行合入新版本
- 不跳过任何 Checkpoint 自动推进

---

## 相关文件

- `pyproject.toml` — Python 包配置与 CLI 入口
- `src/human2skill/` — 核心 Python 模块
- `scripts/quality_check.py` — 自动化品质检查
- `schemas/` — 数据 schema（person.meta、evidence_pack、distillation）
- `templates/profiles/` — 四类 Profile Preset
- `templates/skill/` — Skill 渲染模板


---

> Created by [Eric](https://github.com/EricArcha) · [human2skill](https://github.com/EricArcha/human2skill)

