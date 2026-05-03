# Changelog

All notable changes to human2skill are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-05-03

### Added
- **增量更新模式**：Phase 0 新增 slug 存在性检测，已有项目自动分流到"增量更新模式"。不重写整个 Skill，只增量更新。含冲突检测、pre-update 备份、版本自动递增。
- **`human2skill status`** CLI 子命令：查看项目概况（版本号、心智模型数、来源数、快照数）。
- **`create --force`** 保护：对已有 slug 直接 `create` 不再静默覆盖，报错引导走增量更新。`--force` 显式覆盖。
- **`backup_before_update()`**：更新前将 `person.meta.json`、`distillation.json`、`evidence_pack.json` 快照到 `versions/v{n}_before_update/`。
- **`project_exists()` / `project_status()`**：程序化 slug 存在性检查和项目状态查询。
- **构建版本自动递增**：`build` 命令自动根据已有 versions 目录数递增 `lifecycle.version`。

### Changed
- **SKILL.md Phase 0**：新增 slug 存在性检查分支，Phase 0.5 标注为"仅新建流程"。增量更新流程从文末 6 行附录升级为完整 Step 0-6 章节。

## [2.1.0] - 2026-05-03

### Added
- **`human2skill interview`** CLI 子命令：交互式 20 问访谈循环，支持 skip/done 随时退出。
- **`human2skill check-coverage`** CLI 子命令：程序化输出 Checkpoint A 覆盖率表格。
- **`/human2skill Q20`** 快捷入口：直接启动 20 问快速蒸馏体验。
- **证据引用系统**：distillation schema 新增 `quote`/`quote_source` 字段（≤280 字符）。生成 SKILL.md 时自动收集签名语录和关键引用段落。
- **nuwa 风格 first_person 模板**：沉浸式第一人称，首次激活说一次免责声明后全程自然对话。含角色扮演规则、身份卡、内部路由、示例对话。
- **advisor 模板增强**：结构化格式、签名语录、关键引用、调研来源附录。

### Changed
- **voice_mode 默认值**：改为按 profile 自动推断 — `self`/`relationship` → `first_person`，`colleague`/`mentor` → `advisor`。
- **隐私条款**：从"不输出私域原文"改为"可引用脱敏后的有限原话"（first_person 默认启用，advisor 可选）。
- **`format_distilled_item()`** 改为按 section 类型输出结构化 Markdown。
- **reviewer** 兼容新旧两种模板格式（bullet 和 block 格式均能正确计分）。
- **docs/** 重组：恢复 `docs/superpowers/specs/` 和 `docs/superpowers/plans/`，移除 `docs/archive/`。

### Fixed
- `self` profile 不再错误默认 `advisor` 而应使用 `first_person`。
- reviewer `_count_section_items` 对诚实边界的计数不再误过滤"证据不足"内容。
- first_person 模板 disclaimer 同时支持"不代表本人观点"和"非本人观点"两种表述。

## [2.0.0] - 2026-05-03

### Added
- **Phase 化工作流**：将原有 10 步流程重构为 Phase 0-5，每个 Phase 有明确的入口和出口条件。
- **3 个强制 Checkpoint**（⛔ 标记）：覆盖率审查（Checkpoint A）、蒸馏确认（Checkpoint B）、验证确认（Checkpoint C），每个检查点需用户确认才能推进。迭代上限 2 轮。
- **4 层验证漏斗**：Layer 1 (structured_review) → Layer 2 (scenario replay) → Layer 3 (sub-agent behavioral tests) → Layer 4 (quality_check.py)。
- `scripts/quality_check.py`：6 项自动化品质检查（心智模型数量、局限性、表达 DNA、诚实边界、内在张力、一手来源占比），对标 nuwa-skill。
- `corpus/` 原文归档层：ingest 时自动将原始文本保存到 `corpus/raw/`，支撑验证阶段的原文对照。
- PII 扫描：`ingest.py` 新增 `_scan_for_pii()`，检测到身份证、手机号等敏感信息立即停止摄入。
- 访谈预算硬限制：`INTERVIEW_BUDGET = 20`，达到上限后必须进入 Checkpoint A。
- `assess_coverage()`：10 维度覆盖率量化评估。
- CLI choices 验证：`--profile`、`--voice-mode`、`--perspective`、`--host`、`--variant` 增加 argparse choices。
- CLI 集中错误处理：`_handle_error()` 统一错误输出。
- `GOVERNANCE.md`：治理文档，记录护栏规则、验证标准、命名约定和变更影响矩阵。
- **Repo-as-skill 安装**：根目录 `SKILL.md` + `INSTALL.md` + `Makefile`，`git clone` 即用。
- **README 徽章**：Python、版本、License、AgentSkills 四个 shields.io 徽章。
- **文档签名**：所有主要文档末尾添加 `Created by Eric · human2skill` 签名。
- **模板溯源签名**：生成的 Skill 模板末尾携带 `本 Skill 由 human2skill 生成` 签名。
- **quality_check.py 原文归档检查**：第 7 项检查读取 `corpus/index.json` 验证原文归档完整性，一手来源占比优先使用 corpus 数据而非关键词匹配。

### Changed
- **Skill 命名**：`{slug}-perspective` → `{slug}-lens`（`generator.py`）。
- **输出目录**：`people/` → `outputs/`（`storage.py`、`cli.py`、`flow.py`）。
- **验证阈值**：`confidence_calibration` 从 ≥4 收紧到 ≥5（`reviewer.py`）。
- **Meta-skill**：10 步流程 → Phase 0-5 阶段化，3 个 Checkpoint 标记。
- **Reviewer**：删除 `review_public_skill()`，统一为 `structured_review()`。
- **Scenario 模块**：接入 `build_from_distillation` flow，不再孤立。
- **常量去重**：`PRIVATE_MARKERS` 和 `PROFILE_TYPES` 统一在 `constants.py` 定义。
- **Importlib 模式**：三处重复实现合并为 `schemas.resource_path()`。
- **Interview 预算**：`INTERVIEW_BUDGET` 常量化，取代魔法数字 20。

### Removed
- `base-perspective-advisor.md` 模板（被 `advisor.md` 替代）。
- `render_skill()`（被 `render_skill_variant()` 替代）。
- `next_question()` 向后兼容包装（直接使用 `next_question_for_profile()`）。
- `should_continue()`（逻辑已内联到 `next_question_for_profile()` 和 `assess_coverage()`）。
- `review_public_skill()`（被 `structured_review()` 替代）。
- `README.zh-CN.md`（冗余，`README.md` 已是中文）。

### Fixed
- Python 包版本号从 `0.1.0` 更新为 `2.0.0`（`pyproject.toml`、`__init__.py`）
- CLAUDE.md 中 `confidence_calibration` 阈值从 `≥4` 更新为 `≥5`
- SKILL.md 中 `schemas/`、`templates/` 路径加注完整 `src/human2skill/` 前缀
- 设计文档中"约 20 轮软限制"措辞更新为"20 轮硬限制"
- 移除 Actions 徽章（无 CI workflow）
- 新增 MIT LICENSE
- 删除 `exports/*/README.md`（统一为 `INSTALL.md`）
- 删除残留空目录 `people/`、`.claude/skills/human2skill/`、`.claude/skills/brittany/`
- GOVERNANCE.md §5 新增变更影响矩阵（13 种变更类型 × 下游文件）
- GOVERNANCE.md 从 `docs/` 移至根目录，与 README/CHANGELOG/CLAUDE/LICENSE 同级
- docs/ 目录重组：`superpowers/` 彻底拆分 → `archive/`（历史计划）+ `specs/`（产品规格），与 `design/` 平级

## [1.0.0] - 2026-04-29

### Added
- P0-P2 初始版本。
- 7 模块管线：Intake Router → Corpus Ingestor → Coverage Analyzer → Adaptive Interviewer → Evidence Pack Builder → Distillation Engine → Skill Generator + Reviewer。
- 4 种 Profile 预设：colleague, relationship, mentor, self。
- 3 层证据体系：L1 (direct quote/behavior), L2 (observer report), L3 (model inference)。
- Variant 技能生成：advisor + first_person。
- CLI 命令：create, ingest, question, build, review, export, install。
- 132 个 pytest 测试。


---

> Created by [Eric](https://github.com/EricArcha) · [human2skill](https://github.com/EricArcha/human2skill)

