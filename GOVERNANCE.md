# human2skill Governance

本文档记录 human2skill 的治理规则体系。面向维护者和 Agent，不是用户文档。

每条规则包含**规则内容**和**为什么（rationale）**。

---

## 1. 工作流护栏

### 1.1 Phase 强制顺序

**规则**：蒸馏必须按 Phase 0 → 0.5 → 1 → Checkpoint A → 2 → Checkpoint B → 3 → 4 → Checkpoint C → 5 顺序执行，不可跳过任何 Phase。

**为什么**：Agent 有跳过步骤的自然倾向（尤其倾向于跳过访谈和验证直接生成结果）。Phase 编号 + 明确入口出口条件降低了跳步概率。

### 1.2 强制检查点

**规则**：3 个 Checkpoint（A: 覆盖率审查, B: 蒸馏确认, C: 验证确认）必须暂停，Agent 展示摘要表格，等待用户确认后才能继续。不可自动跳过。

**为什么**：蒸馏中最容易出错的两个环节是调研质量（A）和主观提炼（B）。在错误方向上继续等同于白费功夫。验证（C）是最后防线。参照 nuwa-skill 的 Phase 1.5/2.5/4 检查点设计。

### 1.3 迭代上限

**规则**：Checkpoint 未通过 → 回到 Phase 2 调整，最多 2 轮迭代。超过 2 轮 → 交付当前版本并标注局限性。

**为什么**：防止无限打磨。完美主义是蒸馏的天敌——宁可交付诚实标注了局限的 60 分 Skill，也不要生成看起来完美但实际在编造的 90 分 Skill。

### 1.4 PII 扫描

**规则**：`ingest.py` 在摄入文本时自动扫描 PII（身份证号、手机号、完整聊天记录等）。发现匹配立即抛出 `ValueError`，不继续处理。

**为什么**：这是硬性安全红线。私域原文一旦进入 Agent 上下文就可能被无意中输出到公开 Skill。在入口拦截比在出口拦截可靠得多。检测模式定义在 `constants.py` 的 `PRIVATE_MARKERS` 中。

### 1.5 访谈预算

**规则**：自适应访谈最多 20 轮。达到上限后 Agent 必须暂停并请求用户决定（延展或降级）。常量 `INTERVIEW_BUDGET = 20` 定义在 `constants.py`。

**为什么**：20 轮是经验值——足够覆盖 10 个维度的大部分缺口，同时防止无休止追问导致用户疲劳。

---

## 2. 验证体系

### 2.1 4 层漏斗

**规则**：Skill 构建后依次通过 4 层验证，任何一层未通过都不得导出：

```
Layer 1: structured_review()  — Python 自动化：schema、claim 完整性、7 维度评分
Layer 2: scenario replay       — 3 类型场景测试（historical/counterfactual/boundary）
Layer 3: sub-agent 行为测试    — 已知测试、边缘测试、风格测试（Agent 驱动，Phase 4）
Layer 4: quality_check.py     — 6 项自动化标准检查
```

**为什么**：每层检查不同维度。Layer 1 检查结构正确性，Layer 2 检查推理一致性，Layer 3 检查行为质量，Layer 4 给出量化分数。单靠任何一层都无法全面评估。

### 2.2 Layer 1 评分阈值

| 维度 | 阈值 | 硬失败条件 |
|------|------|-----------|
| evidence_consistency | ≥4 | — |
| confidence_calibration | ≥5 | 任何 overconfident claim |
| honest_boundary | ≥5 | 无诚实边界 section |
| privacy_safety | ≥5 | 含私有标记或冒充声明 |
| expression_similarity | ≥4 | — |
| thinking_utility | ≥4 | — |
| profile_fit | ≥4 | — |

`confidence_calibration = 5` 意味着任何过度自信声明（claim 置信度高于 evidence 支持等级）都是硬失败。

### 2.3 Layer 4 通过标准

| 检查项 | 通过条件 |
|--------|---------|
| 心智模型数量 | 3-7 个 |
| 每个模型局限性 | 所有模型都有非空限制声明 |
| 表达 DNA 辨识度 | ≥3 项特征标记 |
| 诚实边界 | ≥3 条具体局限 |
| 内在张力 | ≥2 处矛盾/冲突 |
| 一手来源占比 | >50%（有 corpus 时） |

---

## 3. 命名与目录约定

### 3.1 Skill 命名

**规则**：生成的 Skill 使用 `{slug}-lens` 格式（如 `brittany-lens`、`zhang-san-lens`）。

**为什么**：`-lens` 强调"视角透镜"的定位——这个 Skill 提供的是一个观察问题的角度，不是角色扮演。替代了之前照搬 nuwa-skill 的 `-perspective` 后缀。

### 3.2 输出目录

**规则**：所有人物项目统一放在 `outputs/{slug}/` 下。

```
outputs/{slug}/
├── person.meta.json
├── corpus/raw/                   # 原文归档
├── corpus/index.json              # 原文索引
├── public_skill/                  # 公开产物
│   ├── SKILL.md
│   ├── SKILL.first_person.md
│   └── variants/
├── private_evidence/              # 私有证据
│   ├── evidence_pack.json
│   ├── source_index.json
│   ├── distillation.json
│   ├── interviews/
│   ├── reviews/
│   └── changelog/
├── exports/                       # 宿主导出
└── versions/                      # 版本快照
```

**为什么**：`outputs/` 语义明确——这是产出目录，不应包含源代码或配置。`.gitignore` 中同时覆盖 `outputs/` 和 `people/`（防御性）。

### 3.3 语料归档

**规则**：摄入的原始文本必须保存到 `corpus/raw/{source_id}.txt`，并在 `corpus/index.json` 中记录元数据。

**为什么**：支撑验证阶段的原文对照（已知测试、一手来源占比计算）。corpus 仅在本地保留，不进入可分发的 Skill。

### 3.4 安装与分发约定

**规则**：meta-skill 采用 repo-as-skill 模式。根目录 `SKILL.md` 使整个仓库可以直接 clone 为可用的 skill 目录。

```bash
git clone https://github.com/EricArcha/human2skill.git ~/.claude/skills/human2skill
```

**为什么**：参照 nuwa-skill 和 colleague-skill 的 AgentSkills 标准——用户不需要理解 Python 打包或 CLI 细节，clone 即用。根目录 `SKILL.md` 为 canonical 源，`exports/` 和 `.claude/skills/` 中的副本为同步目标。

**相关文件**：
- `INSTALL.md`：安装说明，区分终端用户（git clone）和开发者（make install）
- `Makefile`：开发者便利，`make install` / `make test` / `make clean`

**规则**：生成的 Skill 模板必须在末尾包含溯源签名：
```
> 本 Skill 由 [human2skill](https://github.com/EricArcha/human2skill) 生成
```

**为什么**：每个蒸馏产物都应该能追溯到生成工具和版本。参照 nuwa-skill 的"女娲造人"署名。签名在 `src/human2skill/templates/skill/advisor.md` 和 `first_person.md` 中硬编码。

---

## 4. 隐私与伦理

### 4.1 留存策略

| 模式 | 行为 |
|------|------|
| `no_raw_retention` | 不保留任何原始材料 |
| `summary_only` | 仅保留摘要（默认） |
| `local_private_raw` | 原文保留在本地，不入公开 Skill |

默认策略在 `intake.py` 中设置。

### 4.2 默认隐私配置

- 公开 Skill 不包含私域原文（`public_skill_allows_private_quotes = false`）
- 默认不要求本人同意（`person_consented = false`）
- 默认不分发（`distribution_allowed = false`）

用户在 Phase 0 可以覆盖这些配置。

### 4.3 强制规则

1. 不输出私域原文
2. 不做角色扮演（不声称"我就是某人"）
3. 区分已证实和推断
4. 诚实标注边界
5. 版本化管理
6. 评审必须通过
7. 隐私停止规则（发现 PII 立即停）
8. 不可跳过 Phase 和 Checkpoint
9. 迭代上限 2 轮
10. 语料必须归档

### 4.4 禁止事项

- 冒充本人的 Skill
- 输出身份证号、手机号、完整私聊记录等
- 替用户操控与目标人物的关系
- 无证据支持的高置信度宣称
- 跳过评审直接交付
- 矛盾未解决时强行合入新版本
- 跳过 Checkpoint 自动推进

---

## 5. 变更流程与同步检查清单

### 5.1 核心原则

**改一查三，清单勾，不靠记忆。**

本仓库的单一事实源分散在多个文件中（Python 代码、模板、meta-skill、README、GOVERNANCE）。每次修改任何源后，必须按矩阵检查所有受影响的下游文件。v2.0.0 审计发现的 12 个问题中有 4 个是"改了代码忘了同步文档"导致的。

### 5.2 变更影响矩阵

按变更类型查表，逐项检查 `→` 右边的文件是否需同步更新。

| 变更类型 | 单一事实源 | 需同步/检查的下游文件 |
|---------|-----------|---------------------|
| **版本号** | `pyproject.toml` | `src/human2skill/__init__.py`（`__version__`）、`CHANGELOG.md`（新增版本条目）、`tests/test_import.py`（断言值） |
| **常量/阈值** | `constants.py` | `reviewer.py`（`REVIEW_PASS_THRESHOLDS`）、`quality_check.py`（对应检查项）、`GOVERNANCE.md §2`（阈值描述）、`CLAUDE.md`（如有提及） |
| **数据模型/路径** | `storage.py` | `flow.py`、`cli.py`、`exporter.py`、`ingest.py`（所有引用 `person_dir` 或 `outputs/` 的文件）；`README.md`（目录结构图） |
| **命名规则** | `generator.py`（`{slug}-lens`） | `templates/skill/*.md`（`{skill_name}` 占位符）、`README.md`（示例）、`GOVERNANCE.md §3.1`、所有 `examples/` 中的 SKILL.md |
| **访谈规则** | `interview.py` | `GOVERNANCE.md §1.5`、`docs/design/adaptive-interview.md`、`docs/README.md`、`SKILL.md`（Phase 1 描述） |
| **验证逻辑** | `reviewer.py` | `flow.py`（`build_from_distillation` 调用）、`quality_check.py`（6 项检查）、`GOVERNANCE.md §2`、`SKILL.md`（Phase 4 描述） |
| **Meta-skill 流程** | `SKILL.md` | `exports/claude-code/SKILL.md`、`exports/openclaw/SKILL.md`（全部同步副本） |
| **CLI 参数** | `cli.py` | `INSTALL.md`（示例命令）、`README.md`（快速开始节）、`SKILL.md`（Phase 中的命令示例） |
| **模板内容** | `templates/skill/*.md` | `generator.py`（`render_skill_variant` 中的格式化字段）、`templates/skill/` 中另一个变体（advisor ↔ first_person 同步）、已生成的示例人物 SKILL.md（`examples/` 和 `outputs/`） |
| **新增/删除文件** | 文件系统 | `pyproject.toml`（`packages` 配置如需要）、`.gitignore`（防止误提交）、`README.md`（如影响目录结构）、`GOVERNANCE.md §3`（如影响约定）、`SKILL.md`（相关文件节） |
| **安装方式** | `INSTALL.md` | `README.md`（快速开始）、`Makefile`（如有命令变更）、任何引用旧安装方式的文档 |
| **隐私/安全规则** | `constants.py`（`PRIVATE_MARKERS`） | `ingest.py`（`_scan_for_pii`）、`reviewer.py`（`structured_review`）、`exporter.py`（`_privacy_check_passed`）、`GOVERNANCE.md §4` |
| **Skill 安装目录** | `~/.claude/skills/human2skill/` | `exports/`（分发副本与安装目录内容一致）、`INSTALL.md`（安装命令指向正确源） |

### 5.3 使用方式

1. 确定变更属于上述哪种类型。
2. 逐行检查 `→` 右侧的每个文件，打开确认是否需要同步。
3. 修改后运行 `make test`（或 `python -m pytest`），确保 132 tests 通过。
4. `git diff --stat` 确认变更范围与预期一致。
5. 在 commit message 中注明跨文件同步（例：`fix: bump threshold, sync GOVERNANCE and CLAUDE.md`）。

### 5.4 修改护栏规则（详细流程）

1. 在 `constants.py` 中修改常量（如有）
2. 在 `GOVERNANCE.md` 中描述变更和理由
3. 查 §5.2 矩阵中"常量/阈值"和"验证逻辑"两行，同步所有下游文件
4. 更新 `CHANGELOG.md`
5. 运行 `make test` 确认无回归

### 5.5 新增 Profile 类型（详细流程）

1. 在 `constants.py` 的 `PROFILE_TYPES` 中新增
2. 在 `templates/profiles/` 中新增对应的 JSON 文件
3. 在 `interview.py` 的 `PROFILE_QUESTIONS` 中新增该类型的面试问题
4. 在 `profiles.py` 的 `infer_profile_type()` 中新增推断关键词
5. 查 §5.2 矩阵中"Meta-skill 流程"行，同步所有 SKILL.md 副本中的 Profile 表格
6. 新增测试

### 5.6 修改验证标准（详细流程）

1. 在 `reviewer.py` 的 `REVIEW_PASS_THRESHOLDS` 中修改阈值
2. 在 `scripts/quality_check.py` 中同步更新对应的检查逻辑
3. 查 §5.2 矩阵中"验证逻辑"行，同步 `GOVERNANCE.md §2` 和 meta-skill Phase 4 描述
4. 用实际的 SKILL.md 测试新旧阈值效果


---

> Created by [Eric](https://github.com/EricArcha) · [human2skill](https://github.com/EricArcha/human2skill)

