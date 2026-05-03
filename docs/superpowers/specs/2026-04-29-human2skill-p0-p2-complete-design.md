# human2skill P0-P2 Complete Design Spec

## 1. Summary

human2skill 是一个面向私人/身边人物的 Meta-skill 系统。它把用户提供的材料、手动整理的语料、访谈回答和 agent 辅助提炼结果，转成一个可运行、可评审、可导出、可更新的人物视角 Skill。

下一轮实现目标是完成 P0、P1 和 P2 的质量与导出层：

- P0：用户能通过最小闭环生成一个可运行的人物 Skill。
- P1：用户能补充语料、增量更新、记录冲突、生成版本 diff。
- P2：用户能得到结构化质量评审、场景回放报告、分享前隐私检查，以及 Codex、Claude Code、OpenClaw、Hermes 的导出包和显式安装能力。

本 spec 不包含 P3：

- 不实现独立 OCR 引擎。
- 不实现 Web UI 或 TUI。
- 不实现本地加密证据区。
- 不实现多观察者证据合并。
- 不实现长期漂移检测。

图片/截图可以作为用户提供材料的来源类型记录，但系统不做图片识别。若用户已通过宿主能力读取图片内容，human2skill 只接收读取后的文本摘要。

## 2. Product Positioning

human2skill 的核心创新是把可分享的 public Skill 与本地 private evidence 分离。它不是简单生成一个“像某人说话”的角色卡，而是生成一个有证据、置信度、边界、评审和版本记录的 perspective skill。

它与两个参考仓库的关系如下：

### 2.1 From colleague-skill

采用：

- skill preset / schema / writer / version / install / correction 的工程化方向。
- 生成物可导出到多个宿主的意识。
- 版本备份、rollback、patch update 的机制。
- 用户说“这不像他”时，把反馈转成可合并 correction 的思路。

不采用：

- 不直接把原始私域材料跟 public skill 放在一起分发。
- 不实现飞书、钉钉、Slack、邮件平台自动采集。
- 不默认执行真实宿主安装，必须显式 install。

### 2.2 From nuwa-skill

采用：

- 心智模型三重验证：跨域复现、生成力、排他性。
- 表达 DNA、价值排序、反模式、诚实边界。
- agent-assisted 的调研、提炼、构建和质量检查流程。
- 用场景回放测试 skill 是否能运行，而不是只检查文本是否完整。

不采用：

- 不默认第一人称冒充。
- 不默认针对公众人物做网络调研。
- 不把公开人物深度研究作为下一轮主路径。

### 2.3 human2skill specific

human2skill 面向私人/身边人，因此必须更重视：

- 同意状态、用途和分发状态记录。
- 原始私域材料不进入 public skill。
- 证据摘要、置信度和冲突记录。
- 默认 `summary_only` 留存策略。
- 分享前隐私检查。

## 3. Scope

### 3.1 In Scope

下一轮必须实现：

- 混合入口：Python core/CLI + Meta-skill 对话入口。
- Intake Router。
- Corpus Ingestor。
- Adaptive Interviewer 升级。
- Evidence Pack Builder。
- Agent-assisted Distillation contract。
- Skill Generator 多 voice mode。
- Structured Reviewer。
- Scenario Replay。
- Evolution / Incremental Update。
- Exporter。
- Explicit Installer。
- Examples。

### 3.2 Out of Scope

下一轮明确不实现：

- 平台自动采集：飞书、钉钉、Slack、微信、邮箱 API。
- 网络自动调研公众人物。
- 独立 OCR。
- 语音、视频、图片直接解析。
- Web dashboard。
- TUI。
- 本地加密。
- 多观察者冲突归因。
- 长期 drift 监控。
- 云同步。
- 远程服务。

## 4. User Experience

用户应有两种入口。

### 4.1 CLI Entry

CLI 是可靠执行入口，负责文件生成、校验、评审、导出和安装。

目标命令形态：

```bash
human2skill create --slug zhang-san --name 张三 --profile colleague
human2skill ingest --slug zhang-san --file notes.md
human2skill question --slug zhang-san
human2skill build --slug zhang-san --distillation distillation.json
human2skill review --slug zhang-san
human2skill update --slug zhang-san --file new-notes.md
human2skill export --slug zhang-san --host codex
human2skill install --slug zhang-san --host codex --target ~/.codex/skills
```

CLI 可以接受显式参数，也可以读取已有 person directory 中的状态。

### 4.2 Meta-skill Entry

Meta-skill 是对话入口，体验接近 `nuwa-skill` 和 `colleague-skill`：

- 用户说“帮我蒸馏张三”。
- Meta-skill 先确认人物、关系、用途、输出姿态和隐私策略。
- Meta-skill 引导用户提供语料或回答访谈。
- Meta-skill 调用 CLI 初始化目录、写 source index、写 evidence pack。
- Meta-skill 负责 agent-assisted distillation，把高判断力提炼写成 `distillation.json`。
- CLI 负责校验、渲染、评审、导出。

Meta-skill 不绕过 CLI 直接散写产物。所有可测试的结构化产物都应由 core/CLI 写入或校验。

## 5. Directory Layout

每个人物目录：

```text
outputs/{slug}/
  person.meta.json
  public_skill/
    SKILL.md
    variants/
      advisor/SKILL.md
      first_person/SKILL.md
  private_evidence/
    source_index.json
    evidence_pack.json
    distillation.json
    interviews/
      interview-YYYYMMDD-HHMM.md
    reviews/
      review-YYYYMMDD-HHMM.json
      scenario-replay-YYYYMMDD-HHMM.json
    changelog/
      v1.md
      v2.md
  exports/
    codex/
    claude-code/
    openclaw/
    hermes/
  versions/
    v1/
    v2/
```

Examples 目录：

```text
examples/
  colleague-li-ming/
  relationship-chen-yu/
  self-future-me/
```

示例必须使用虚构人物，不得包含真实隐私。

## 6. Data Model

### 6.1 person.meta.json

`person.meta.json` 是人物级 metadata。

Required fields:

- `schema_version`: `"1"`
- `slug`: stable slug
- `display_name`: display name
- `profile_type`: `colleague | relationship | mentor | self`
- `relationship_to_user`
- `use_case`
- `voice_mode`: `advisor | first_person | both`
- `consent_status`
- `privacy_policy`
- `export_policy`
- `lifecycle`

`voice_mode` rules:

- `advisor` 是默认值。
- `first_person` 允许有限第一人称运行风格，但必须声明非本人观点。
- `both` 同时生成 advisor 和 first_person 变体。

`privacy_policy` defaults:

```json
{
  "raw_retention": "summary_only",
  "public_skill_allows_private_quotes": false
}
```

`export_policy` defaults:

```json
{
  "default_visibility": "private",
  "shareable_variants": ["advisor"],
  "requires_privacy_review": true
}
```

If `voice_mode` is `first_person`, sharing is still allowed only if review passes and the generated first-person skill includes mandatory disclaimer and non-impersonation boundaries.

### 6.2 source_index.json

`source_index.json` records what material exists and how it may be used.

Required source fields:

- `source_id`: `src-0001`
- `source_kind`: `manual_text | markdown | txt | pdf_text | chat_excerpt | meeting_note | email_summary | interview_answer | screenshot_text`
- `title`
- `provided_by`: usually `user`
- `retention`: `no_raw_retention | summary_only | local_private_raw`
- `contains_private_data`
- `allowed_in_public_skill`: boolean, default false
- `summary`
- `created_at`

Default behavior:

- System stores summaries and metadata.
- System does not copy raw source files by default.
- Public skill never receives source raw text.

### 6.3 evidence_pack.json

Evidence remains based on the existing schema but must support:

- evidence list
- claims list
- conflicts list
- source references

Evidence types:

- `direct_quote_or_behavior`
- `observer_report`
- `model_inference`

Claim types:

- `mental_model`
- `decision_heuristic`
- `expression_dna`
- `profile_specific`
- `pressure_response`
- `value_order`
- `anti_pattern`
- `boundary`

Conflict fields:

- `conflict_id`: `cf-0001`
- `claim_ids`
- `evidence_ids`
- `conflict_type`: `temporal | contextual | observer_conflict | inherent_tension`
- `resolution`: `halt_for_review | keep_both_with_scope | mark_low_confidence`
- `note`

Conflict policy:

- Never silently reconcile conflicts.
- If an active high-confidence claim conflicts with new evidence, update flow must stop with required changes.
- Low-confidence or contextual conflicts may be preserved with scope notes.

### 6.4 distillation.json

`distillation.json` is the contract between agent-assisted reasoning and deterministic code.

It must include:

- `schema_version`
- `person_slug`
- `generated_at`
- `source_evidence_pack_version`
- `mental_models`
- `decision_heuristics`
- `expression_dna`
- `profile_specific`
- `pressure_response`
- `value_order`
- `anti_patterns`
- `honest_boundaries`
- `scenario_tests`

Each distilled item must include:

- `title`
- `content`
- `claim_ids`
- `confidence`
- `evidence_summary`
- `limits`

The CLI validates that every non-boundary distilled item links to at least one claim.

### 6.5 review_report.json

Review report contains two reviewer perspectives:

- `evidence_boundary`
- `voice_utility`

Required score dimensions:

- `evidence_consistency`
- `confidence_calibration`
- `honest_boundary`
- `privacy_safety`
- `expression_similarity`
- `thinking_utility`
- `profile_fit`

Pass thresholds:

- evidence consistency >= 4
- confidence calibration >= 4
- honest boundary = 5
- privacy safety = 5
- expression similarity >= 4
- thinking utility >= 4
- profile fit >= 4

Hard failures:

- public skill includes raw private material.
- skill claims to be the real person.
- high-confidence claims are unsupported.
- conflicts are flattened without record.
- honest boundaries are missing.
- first-person variant lacks disclaimer.

### 6.6 export_manifest.json

Each export package must include:

- host name
- slug
- variant
- generated files
- install target recommendation
- review status
- privacy check result
- created_at

Supported hosts:

- `codex`
- `claude-code`
- `openclaw`
- `hermes`

## 7. Core Modules

### 7.1 Intake Router

Responsibilities:

- Normalize slug.
- Infer or accept profile type.
- Create person directory.
- Write initial metadata.
- Set defaults for privacy and export policy.
- Select voice mode.

Rules:

- Unknown profile falls back to `relationship`.
- `self` must be detected when user says “我自己”“过去的我”“未来的我” or equivalent.
- `public_skill_allows_private_quotes` must default false.
- `raw_retention` must default `summary_only`.

### 7.2 Corpus Ingestor

Responsibilities:

- Accept manual text and local files.
- Extract plain text from Markdown/TXT.
- Extract text from PDF using lightweight dependency.
- Convert each input into source summary records.
- Add source records to `source_index.json`.

Supported input kinds:

- pasted/manual text
- `.md`
- `.txt`
- `.pdf`
- manually prepared chat excerpts
- meeting notes
- email summaries
- screenshot text already extracted by host

Non-goals:

- No platform login.
- No automatic browser scraping.
- No OCR.
- No email API.

Failure behavior:

- Unsupported file type returns a structured error.
- PDF extraction failure records no source and reports the file path.
- Empty text is rejected.

### 7.3 Coverage Analyzer and Adaptive Interviewer

Coverage dimensions:

- identity context
- mental models
- expression DNA
- decision heuristics
- pressure response
- profile specific
- value order
- anti patterns
- honest boundaries
- evaluation scenarios

Interview perspectives:

- `self_answer`: target person answers directly, used especially for self profile.
- `observer_answer`: user answers as observer, default for private/known people.

Question selection:

- Prioritize missing high-weight profile dimensions.
- Prefer concrete scene questions over abstract impression questions.
- Ask for behavior, approximate wording, context, and counterexamples.
- At 20 turns, summarize remaining gaps and ask whether to continue.

If user stops:

- Missing dimensions become honest boundaries.
- Related claims must be low confidence.

### 7.4 Evidence Pack Builder

Responsibilities:

- Generate sequential IDs.
- Convert interview answers and source summaries into evidence items.
- Add claims from agent-assisted distillation.
- Compute support level.
- Flag overconfident claims.
- Record conflicts.

Confidence rules:

- High: multiple direct/behavior sources, or direct + observer support, or same pattern across multiple contexts.
- Medium: one direct source, or multiple observer reports, or well-grounded inference.
- Low: single observer report, model inference only, unresolved conflict, or missing interview dimension.

### 7.5 Agent-assisted Distillation

The project must not pretend to distill deep human perspective through local keyword heuristics alone.

Division of responsibility:

- Agent performs high-judgment synthesis.
- Python validates structure, evidence links, privacy rules, and rendering.

Agent must produce `distillation.json` using:

- source index
- evidence pack
- profile preset
- interview summaries
- existing skill if update mode

Agent must apply:

- mental model triple validation
- expression DNA extraction
- value order and anti-pattern extraction
- conflict preservation
- honest boundary writing

The agent must not:

- invent unsupported high-confidence claims.
- paste raw private text into public sections.
- silently resolve conflicts.
- claim the skill is the real person.

### 7.6 Skill Generator

Generator renders public Skill variants.

Supported variants:

- advisor
- first_person

Advisor mode:

- Speaks as a perspective advisor.
- Uses phrasing like “从这个人的视角看”.
- Safe for sharing after privacy review.

First-person mode:

- Uses limited first person for immersion.
- First activation includes disclaimer.
- Must include explicit non-impersonation boundary.
- Must not claim to be the real person.
- Must not send messages on behalf of the target.
- Must not help manipulate the target or third parties.

Shared sections:

- activation protocol
- use boundaries
- core mental models
- decision heuristics
- expression DNA
- profile-specific layer
- pressure and conflict response
- value order
- anti-patterns
- honest boundaries
- evidence and confidence summary

### 7.7 Structured Reviewer

Reviewer upgrades current binary checks to structured quality reports.

Reviewer A: evidence and boundary.

Checks:

- every core model links to claims.
- high-confidence claims are sufficiently supported.
- conflicts remain visible.
- low-coverage areas are in honest boundaries.
- no raw private material in public skill.

Reviewer B: voice and utility.

Checks:

- output is not generic AI.
- expression features are evidence-backed.
- first-person mode is not impersonation.
- generated skill can answer new questions using extracted models.
- profile-specific layer serves use case.

### 7.8 Scenario Replay

Each person should have at least three scenario tests:

- historical scenario
- counterfactual scenario
- boundary scenario

Replay report records:

- input
- expected behavior
- actual generated answer or structured judgment
- pass/fail
- notes

For implementation safety, actual answer generation may remain agent-assisted. Python stores and validates report structure.

### 7.9 Evolution Manager

Update flow:

1. Add new source.
2. Create new evidence.
3. Compare with active claims.
4. If conflict appears, stop and write review requirement.
5. If new source strengthens existing claim, update confidence or evidence links.
6. If new pattern appears, require distillation update.
7. Render new skill version.
8. Review and snapshot.

Versioning:

- Every successful build increments version.
- Previous public skill, evidence pack, distillation, review report, and export manifests are snapshotted.
- Changelog records added sources, changed claims, changed confidence, conflicts, and generated variants.

Rollback:

- Restore previous version files from `versions/{version}/`.
- Record rollback metadata.

### 7.10 Exporter and Installer

Export behavior:

- Default command writes to project-local `exports/{host}/{slug}/`.
- Export must run privacy review first.
- Export must include host-specific frontmatter or README instructions.

Install behavior:

- Install is explicit.
- Install accepts host and target directory.
- Tests must install only into temporary directories.
- No command should write into home directory by default.

Host requirements:

- Codex: skill directory with `SKILL.md`.
- Claude Code: `.claude/skills/{name}/SKILL.md` style package.
- OpenClaw: workspace skill directory package.
- Hermes: slash-command compatible markdown instructions.

## 8. CLI Design

### 8.1 create

Creates metadata and directory layout.

Inputs:

- slug
- display name
- profile type
- relationship
- use case
- voice mode

Outputs:

- person directory
- initial `person.meta.json`

### 8.2 ingest

Adds source records.

Inputs:

- slug
- text or file
- source kind
- title
- retention override

Outputs:

- updated `source_index.json`

### 8.3 question

Returns next interview question based on coverage.

Inputs:

- slug
- perspective
- turn count

Outputs:

- question text
- missing dimension
- continuation warning when needed

### 8.4 evidence

Builds or updates evidence records from structured agent/user input.

Inputs:

- slug
- source id
- evidence payload or claim payload

Outputs:

- updated evidence pack
- validation warnings

### 8.5 build

Validates `distillation.json` and renders skill variants.

Inputs:

- slug
- distillation path
- variant override

Outputs:

- public skill variant files
- updated lifecycle version

### 8.6 review

Runs structured review and scenario replay validation.

Inputs:

- slug
- variant

Outputs:

- review report JSON
- scenario replay JSON if provided

### 8.7 update

Runs incremental update flow.

Inputs:

- slug
- new source or evidence

Outputs:

- updated evidence pack
- conflict report or new version

### 8.8 export

Creates host package.

Inputs:

- slug
- host
- variant

Outputs:

- `outputs/{slug}/exports/{host}/`
- root-level optional `exports/{host}/{slug}/`
- export manifest

### 8.9 install

Copies export package into a user-provided target.

Inputs:

- slug
- host
- target directory
- variant

Outputs:

- copied package
- install summary

## 9. Meta-skill Design

The Meta-skill must guide the user through:

1. Confirm subject and purpose.
2. Choose profile type.
3. Choose voice mode.
4. Confirm privacy defaults.
5. Ask for source material.
6. Call CLI to create and ingest.
7. Ask adaptive interview questions until coverage is enough or user stops.
8. Build evidence pack.
9. Perform agent-assisted distillation into `distillation.json`.
10. Call CLI to build skill.
11. Call CLI to review.
12. Show review summary.
13. Export if review passes.

Meta-skill must include checkpoint behavior:

- After source ingestion, show coverage summary.
- After distillation, show extracted models and boundaries.
- After review, show pass/fail and required changes.

Meta-skill must not:

- Continue after hard review failure without user confirmation.
- Put raw private material in public skill.
- Skip evidence links for strong claims.
- Start writing implementation plan.

## 10. Privacy and Safety

Privacy defaults:

- `raw_retention = summary_only`
- `public_skill_allows_private_quotes = false`
- `allowed_in_public_skill = false` for sources unless explicitly safe

Public skill may include:

- abstracted conclusions
- non-sensitive behavior patterns
- confidence summaries
- honest boundaries

Public skill must not include:

- full chat logs
- private social posts
- IDs, phone numbers, addresses
- third-party private details
- sensitive work document text
- raw quotes from private contexts unless explicitly sanitized and allowed

First-person mode safety:

- Must disclose non-person status.
- Must not claim “我就是某某本人”.
- Must not provide manipulation scripts.
- Must not impersonate for communication.

## 11. Examples

Three examples must be included:

### 11.1 colleague-li-ming

Profile:

- colleague
- work review and collaboration use case
- advisor + first-person variant allowed

Expected skill strengths:

- work method
- decision heuristics
- pressure response

### 11.2 relationship-chen-yu

Profile:

- relationship
- friendship/family interaction use case
- advisor default

Expected skill strengths:

- relationship patterns
- emotional triggers
- support style
- conflict repair

### 11.3 self-future-me

Profile:

- self
- decision mirror and future-self use case
- first-person or both allowed

Expected skill strengths:

- self-reflection
- long-term preference
- recurring blind spots

## 12. Acceptance Criteria

Functional acceptance:

- User can create a person directory.
- User can ingest at least Markdown, TXT, PDF text, manual text, and interview answers.
- User can produce evidence pack with claims and confidence.
- User can provide agent-written distillation and have it validated.
- User can render advisor and first-person variants.
- User can run structured review.
- User can export to four hosts.
- User can explicitly install into a provided target directory.
- User can update with new evidence and trigger conflict stop.
- User can rollback to a previous version.

Quality acceptance:

- All public skill variants include non-impersonation boundaries.
- First-person variants include mandatory disclaimer.
- Public skills contain no private raw material.
- High-confidence claims are not unsupported.
- Conflicts are visible and classified.
- Review reports identify low-confidence regions.
- Scenario replay includes historical, counterfactual, and boundary scenarios.

Test acceptance:

- All existing tests continue passing.
- New schema tests include valid and invalid examples.
- CLI integration tests run in temporary directories.
- Export/install tests never write to actual home directories.
- Example fixtures pass privacy review.

Documentation acceptance:

- Meta-skill entry document explains complete user flow.
- README or docs explain CLI usage.
- Spec and implementation plan remain separate.
- No implementation plan is written until user approves this spec.

## 13. Risks and Tradeoffs

### 13.1 Large Scope

P0-P2 is larger than the current codebase. The implementation plan should split work into small, independently testable tasks.

### 13.2 Agent-assisted Distillation

The project will not be fully deterministic because synthesis quality depends on the host agent. This is intentional. Deterministic code owns structure, validation, privacy, review, export, and versioning.

### 13.3 First-person Mode

First-person mode improves immersion but raises impersonation risk. The system mitigates this by making voice mode explicit, adding mandatory disclaimers, preserving non-impersonation rules, and requiring privacy review.

### 13.4 PDF Extraction

Lightweight PDF extraction may fail on scanned PDFs. Scanned image PDFs are out of scope unless the host extracts text first.

### 13.5 Multi-host Install

Host install paths vary by environment. Therefore export is default and install requires explicit target.

## 14. Defaults Chosen

- Scope: P0 + P1 + P2 quality/export.
- P3 excluded.
- Entry: Python core/CLI + Meta-skill.
- Distillation: agent-assisted.
- Ingest: manual + file.
- Platform collection: excluded.
- Privacy: `summary_only` default.
- Voice mode: configurable, default `advisor`.
- Export: project-local by default.
- Install: explicit command only.
- Examples: committed under `examples/` with fictional subjects.
- Dependencies: light Python dependencies only.

## 15. Confirmation Gate

This spec is the source of truth for the next implementation plan.

Do not write the implementation plan until the user explicitly approves this spec.

After approval, the next step is to use the Superpowers writing-plans workflow and create a detailed plan under:

```text
docs/superpowers/plans/2026-04-29-human2skill-p0-p2-complete-implementation-plan.md
```
