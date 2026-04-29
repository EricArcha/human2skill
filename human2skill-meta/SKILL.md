---
name: human2skill
description: 将有限语料和自适应访谈蒸馏为可复用的人物视角顾问 Skill。触发词：human2skill、人物蒸馏、创建人物 Skill、更新人物视角。
---

# human2skill 人物视角蒸馏

> 将私人/身边人的有限语料和自适应访谈，蒸馏为可复用的人物视角顾问 Skill。
> 触发词：**human2skill** / **人物蒸馏** / **创建人物 Skill**

---

## 定位

本 Meta-skill 是人物视角蒸馏的编排工具，负责从主题确认到最终产物交付的完整流程。产物是 `public_skill/SKILL.md`（可分发视角顾问）+ `private_evidence/`（私有证据包）。

不做角色扮演，不冒充本人，不输出私域原文。

---

## 产物目录结构

```
people/{slug}/
  person.meta.json
  public_skill/
    SKILL.md
    SKILL.first_person.md
  private_evidence/
    evidence_pack.json
    source_index.json
    distillation.json
    interviews/
    reviews/
  versions/
    v1/
    v2/
```

---

## 标准流程（共 10 步）

### Step 1 -- 确认主题人物

用户提供：人物称呼或 slug、与用户的关系、用途描述。

Agent 调用 `human2skill create` 初始化人物目录：

```bash
human2skill create --slug zhang-san --display-name "张三" \
  --relationship "coworker" --use-case "work perspective advisor"
```

此步骤创建 `person.meta.json`、人物目录布局、空证据包和空来源索引。

### Step 2 -- 选择人物 Profile

从四类 Preset 中选择：

| Profile | 适用对象 | CLI 参数 |
| --- | --- | --- |
| colleague | 同事、上级、下级、客户 | `--profile-type colleague` |
| relationship | 朋友、伴侣、父母、子女 | `--profile-type relationship` |
| mentor | 导师、老师、顾问、专家 | `--profile-type mentor` |
| self | 自己、过去的自己 | `--profile-type self` |

若未明确指定，Agent 根据关系描述关键词自动推断。

### Step 3 -- 选择语气模式

两种语气变体：

| 模式 | 产物文件 | 用途 |
| --- | --- | --- |
| advisor | `SKILL.md` | 第三人称视角顾问（默认），以观察者身份提供视角分析 |
| first_person | `SKILL.first_person.md` | 第一人称视角自用，用于自我反思和决策镜像 |

`human2skill create` 支持 `--voice-mode` 参数，默认 `advisor`。

### Step 4 -- 确认隐私配置

默认隐私策略（无干预时生效）：

- **留存模式**: `summary_only` -- 保留摘要，不存原文
- **公开 Skill 不包含私域原文**: public_skill_allows_private_quotes 强制为 false
- **默认不要求本人同意**: person_consented 默认 false
- **默认不分发**: distribution_allowed 默认 false

Agent 在创建前向用户确认以上配置，用户可覆盖。

可选留存模式：
- `no_raw_retention` -- 不保留任何原始材料
- `summary_only` -- 仅保留摘要（默认）
- `local_private_raw` -- 原文保留在本地私有证据区，不入可分发 Skill

### Step 5 -- 摄入来源语料

Agent 接收用户提供的语料：

- 直接粘贴的文本
- Markdown/TXT 文件
- 手动整理的聊天摘录
- 会议纪要
- 工作文档摘要

调用 `human2skill ingest` 归档：

```bash
human2skill ingest --slug zhang-san --text "张三在评审会上说..." --source-type direct_quote
human2skill ingest --slug zhang-san --file ./notes/zhangsan-meeting.md
```

每条来源记录 `source_id`、`source_type`、摘要和留存策略。

**停止规则**：若用户提供材料包含身份证、手机号等敏感信息，Agent 必须停止并提示用户脱敏后再摄入。

### Step 6 -- 自适应访谈

Agent 分析当前信息覆盖度（8 个维度），对缺口维度启动追问：

1. 基本身份与关系语境
2. 核心思维模型
3. 表达 DNA
4. 决策启发式
5. 压力和冲突反应
6. Profile 专项维度
7. 已知边界和盲区
8. 可用于评估的历史场景

访谈预算为约 20 轮（非固定）：
- 信息足够时提前结束
- 信息不足时继续追问
- 到约 20 轮仍不足时，提示缺口并请求用户确认是否延展
- 用户不想继续时，相关结论标低置信度并写入诚实边界

Agent 将访谈记录写入 `private_evidence/interviews/`，命名格式 `interview-YYYYMMDD-HHMM.md`。

**Source Coverage Checkpoint** -- 覆盖度是否足以进入蒸馏？
- 至少 4 个维度达到 medium 或 high
- `honest_boundaries` 维度至少有一条低置信度声明
- 若不满足，继续访谈或由用户确认降级进入蒸馏

### Step 7 -- 构建证据包

Agent 将语料和访谈转为结构化证据，写入 `private_evidence/evidence_pack.json`。

证据三层分级：

| 层级 | 来源类型 | 权重 |
| --- | --- | --- |
| L1 | direct_quote_or_behavior（原话/行为记录） | 3 |
| L2 | observer_report（观察者描述） | 2 |
| L3 | model_inference（模型推断） | 1 |

每条 evidence 包含 `evidence_id`、`source_summary`、`retention`、`confidence`、`supports`（声明的 claim_id 列表）和 `conflicts_with`。

每条 claim 包含 `claim_id`、`claim_type`、`confidence`、`evidence_ids` 和 `status`。

置信度分为 `high`/`medium`/`low`。

**规则**：若一条 claim 的置信度高于其 evidence 的组合支持等级，标记为 overconfident。Review 阶段会报告所有 overconfident claims。

### Step 8 -- 编写蒸馏声明

Agent 编写 `private_evidence/distillation.json`，包含以下章节：

- `mental_models` -- 核心思维模型
- `expression_dna` -- 表达 DNA（口头禅、句式、语气特征）
- `decision_heuristics` -- 决策启发式
- `profile_specific` -- Profile 专项层（如工作方法、关系模式、教学风格）
- `pressure_response` -- 压力和冲突反应
- `value_order` -- 价值排序
- `anti_patterns` -- 反模式（已知不会做的事）
- `honest_boundaries` -- 诚实边界（证据不足无法推断的区域）
- `scenario_tests` -- 可用于评估的历史场景和新场景

每项结构：`title`、`content`、`claim_ids`（关联的证据声明 ID）、`confidence`、`evidence_summary`、`limits`（已知限制）。

**Agent 辅助蒸馏要求**：
- 心智模型优先使用三重验证：跨场景复现、能推断新问题立场、有此人特异性
- 未通过三重验证的观点降级为启发式或低置信度观察
- `honest_boundaries` 至少包含 3 条：关系场景不足、技术细节有限、时间范围有限
- 所有 `scenario_tests` 必须包含 `expected_behavior` 字段
- 每个非 `honest_boundaries` 项必须有至少一个 `claim_id`

**Distillation Checkpoint** -- 蒸馏是否满足完整性要求？
- 所有必填章节存在且非空（或明确标注证据不足）
- `honest_boundaries` 至少 3 条
- 至少 1 个 `scenario_tests` 条目
- 所有 `claim_id` 在 `evidence_pack.json` 中存在
- 不存在 overconfident claims

### Step 9 -- 构建、评审与导出

Agent 调用 `human2skill build` 从蒸馏声明生成 Skill：

```bash
human2skill build --slug zhang-san --distillation distillation.json
```

此命令执行：
1. 校验 `distillation.json` schema 和 claim-id 完整性
2. 检测 overconfident claims
3. 渲染 Skill 变体（advisor + first_person）并写入 `public_skill/`
4. 运行结构化评审（证据一致性、边界诚实度、隐私安全）
5. 写入评审报告到 `private_evidence/reviews/`
6. 快照版本到 `versions/v{n}/`

**Review Checkpoint** -- 评审是否通过？

结构化评审检查项：
- **隐私安全**：无 `完整聊天记录`、`身份证`、`手机号`、`原始私聊`、`朋友圈原文` 等私域原文标记
- **冒充检测**：无 `我就是` 等冒充声明
- **免责声明**：包含 `不代表本人观点`
- **诚实边界**：包含 `诚实边界` 章节
- **置信度一致性**：无 claim 置信度高于 evidence 支持等级

若评审未通过，Agent 报告具体失败项和修复建议，不生成新版本。

导出可分发 Skill：

```bash
human2skill export --slug zhang-san --output ./dist/
```

### Step 10 -- 交付与使用

产物交付清单：
- `public_skill/SKILL.md` -- 可分发、可安装的视角顾问 Skill
- `public_skill/SKILL.first_person.md` -- 自用第一人称版本（若启用）
- `private_evidence/` -- 私有证据包（本地保留，不分发）

用户在目标宿主（Claude Code/Codex/OpenClaw）中安装 `SKILL.md` 后即可调用。

---

## 增量更新流程

人物视角不是一次性产物，可持续补充语料。

增量更新步骤：
1. 提供新语料，调用 `human2skill ingest` 追加
2. Agent 分析新证据对现有 claims 的影响（强化、矛盾、无关）
3. 若发现矛盾，记录到 `evidence_pack.json` 的 `conflicts` 数组中
4. 更新 `distillation.json` 中受影响的条目
5. 重新调用 `human2skill build`，生成新版本
6. 版本快照保存到 `versions/v{n}/`

**冲突停止规则**：若检测到矛盾且 `resolution` 设为 `halt_for_review`，构建中止，Agent 必须向用户报告冲突并等待人工裁决。

---

## 强制规则

1. **不输出私域原文** -- 默认为 `summary_only`，原始语料不进入可分发 Skill
2. **不做角色扮演** -- 生成 Skill 以"视角顾问"方式回答，不声称是本人
3. **区分已证实和推断** -- 每项结论标注 confidence 和 evidence_summary
4. **诚实标注边界** -- 证据不足时不强行推断，写入 honest_boundaries
5. **版本化管理** -- 每次构建生成版本快照，允许回滚
6. **评审必须通过** -- Review Checkpoint 未通过不得交付 Skill
7. **隐私停止规则** -- 发现敏感个人信息（身份证号、手机号等）立即停止，不继续处理

---

## 禁止事项

- 不生成冒充本人的 Skill
- 不输出身份证号、手机号、完整私聊记录等私域原文
- 不替用户操控与目标人物的关系
- 不在无证据支持下宣称高置信度
- 不跳过评审直接交付
- 不在矛盾未解决时强行合入新版本

---

## 相关文件

- `pyproject.toml` -- Python 包配置与 CLI 入口
- `schemas/` -- 数据 schema（person.meta、evidence_pack、distillation）
- `templates/profiles/` -- 四类 Profile Preset
- `templates/skill/` -- Skill 渲染模板
- `docs/design/human2skill-architecture.md` -- 架构设计
- `docs/design/human2skill-product-spec.md` -- 产品规格
