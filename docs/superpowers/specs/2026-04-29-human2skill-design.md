# human2skill Design Spec

## Summary

human2skill 是一个多宿主兼容的 Meta-skill，用于把私人/身边人的有限语料和主动访谈蒸馏成可运行的“视角顾问 Skill”。

第一版重点不是公众人物深度调研，也不是冒充本人，而是帮助用户在本地自用场景中理解某个人稳定的思维方式、表达习惯、关系互动模式、工作方法和边界。

系统默认生成两个产物：

- 可使用、可安装、可分享的 `public_skill/SKILL.md`。
- 本地私有的 `private_evidence/` 证据包，用于追溯、评审和后续进化。

原始私域语料默认不进入可分发 Skill。

## Goals

- 支持通过文章、聊天记录、朋友圈、微博、工作文档、会议记录、访谈回答等材料蒸馏人物视角。
- 支持信息不足时进行信息缺口驱动的自适应访谈。
- 支持本人回答和观察者回答两种访谈视角。
- 支持四类基础人物 profile：同事/合作者、朋友/亲人、导师/专家、自己。
- 对每条核心结论记录证据来源类型和置信度。
- 使用双评审模式检查证据一致性、表达相似度、边界诚实度和隐私安全。
- 支持持续补充语料后的增量合并、冲突停机、版本记录和置信度变化。
- 保持 Codex、Claude Code、OpenClaw、Hermes 等宿主的适配空间。

## Non-Goals

- 不强制要求目标人物本人授权。
- 不做目标人物授权管理平台。
- 不生成用于冒充本人、代发消息或操控关系的能力。
- 第一版不做 Web dashboard。
- 第一版不做复杂自动采集和全格式聊天记录解析。
- 第一版不把公众人物网络调研作为主路径。

## Key Decisions

- **默认形态**：视角顾问 Skill，而非第一人称冒充。
- **访谈方式**：不是固定 20 问；约 20 轮只是默认预算。信息足够可提前结束，信息不足可提示后继续。
- **证据模型**：采用三层证据：原话/行为记录、观察者描述、模型推断。
- **隐私策略**：可分发 Skill 与私有证据包分离。原始私域语料默认不进入 `SKILL.md`。
- **同意策略**：参考 `colleague-skill` 的低摩擦本地自用方式，不强制同意，但 metadata 记录同意状态、用途、分发状态和留存策略。
- **质量策略**：采用双评审模式，而不是只依赖用户主观打分。
- **进化策略**：采用增量合并 + 版本记录，而不是每次全量重蒸馏。

## Architecture

系统由七个核心模块组成：

1. `Intake Router`
   - 确认人物 profile、用途、关系、同意状态、分发状态和原始语料留存策略。

2. `Corpus Ingestor`
   - 接收文本、Markdown、聊天摘录、会议记录、工作文档摘要等材料。
   - P1 再扩展 PDF、聊天导出、邮件、截图等输入。

3. `Coverage Analyzer`
   - 维护 coverage map，判断当前信息是否足够。
   - 覆盖身份语境、思维模型、表达 DNA、决策习惯、压力反应、profile 专项、边界和测试场景。

4. `Adaptive Interviewer`
   - 根据 coverage map 动态追问。
   - 支持本人版和观察者版。
   - 约 20 轮后仍不足时，先说明缺口和继续价值，再由用户决定是否继续。

5. `Evidence Pack Builder`
   - 生成本地私有证据包。
   - 每条 evidence 标注来源类型、摘要、留存策略、置信度、支持结论和冲突关系。

6. `Distillation Engine`
   - 提炼核心思维模型、表达 DNA、决策启发式、profile 专项层、压力反应和诚实边界。
   - 心智模型优先通过跨场景复现、生成力、特异性三重验证。

7. `Skill Generator + Reviewer + Evolution Manager`
   - 生成 `public_skill/SKILL.md`。
   - 双评审检查质量。
   - 新语料进入待合并状态，冲突时停机记录，不强行调和。
   - 合并后保存版本和置信度变化。

## Data Model

每个人物目录：

```text
outputs/{slug}/
  person.meta.json
  public_skill/
    SKILL.md
  private_evidence/
    evidence_pack.json
    source_index.json
    interviews/
    reviews/
  versions/
```

`person.meta.json` 必须记录：

- `slug`
- `display_name`
- `profile_type`
- `relationship_to_user`
- `use_case`
- `consent_status`
- `privacy_policy`
- `lifecycle`

`evidence_pack.json` 必须记录：

- evidence 列表
- claim 列表
- evidence 到 claim 的支持关系
- claim 的置信度
- 冲突关系

默认留存策略：

- `summary_only`

可选策略：

- `no_raw_retention`
- `local_private_raw`

## Profile Presets

所有 profile 共享：

- 思维模型
- 表达 DNA
- 决策启发式
- 压力/冲突反应
- 价值排序
- 反模式
- 诚实边界

profile 差异：

- `colleague`：加重工作方法、职责边界、协作风格、输出习惯。
- `relationship`：加重关系互动、情绪反应、支持方式、冲突修复和边界。
- `mentor`：加重观点体系、判断框架、教学反馈和专业盲区。
- `self`：加重自我反思、决策镜像、长期偏好和反复盲区。

## Public Skill Requirements

生成的 `SKILL.md` 必须：

- 明确这是基于材料生成的视角顾问，不代表本人观点。
- 不声称自己就是目标人物本人。
- 不输出私域原文。
- 遇到证据不足时说明不确定。
- 包含核心思维模型、表达 DNA、决策启发式、profile 专项层、压力反应和诚实边界。
- 可根据宿主适配不同 frontmatter，但主体内容保持一致。

## Review Requirements

双评审：

- 评审 A：证据与边界。
- 评审 B：表达与使用价值。

硬性失败条件：

- public skill 含敏感原文。
- 声称自己就是目标人物。
- 核心结论大量没有证据。
- 冲突证据被强行揉平。
- 缺少诚实边界。

通过线：

- 证据一致性 >= 4/5。
- 置信度校准 >= 4/5。
- 表达相似度 >= 4/5。
- 思维可用性 >= 4/5。
- profile 适配 >= 4/5。
- 诚实边界 = 5/5。
- 隐私安全 = 5/5。

## Phased Scope

### P0

- 参考仓库进入 `references/repos/`。
- 建立 profile presets。
- 建立 metadata 和 evidence schema。
- 支持手动语料和自适应访谈。
- 生成 `public_skill/SKILL.md`。
- 生成私有证据包。
- 提供双评审最小流程。

### P1

- 扩展语料导入：Markdown/TXT 批量、PDF 文本、手动聊天记录、邮件摘要。
- 增量合并新证据。
- 冲突检测和停机提示。
- 版本 diff 和置信度变化报告。

### P2

- Codex、Claude Code、OpenClaw、Hermes 适配。
- 结构化评审 JSON。
- 场景回放测试集。
- 导出/分享前隐私检查。

### P3

- 聊天导出格式适配器。
- 图片/截图 OCR。
- 本地加密证据区。
- 多观察者证据合并。
- 长期漂移检测。
- 可选公众人物 profile。

## Test Scenarios

- 同事/合作者：少量工作文档 + 观察者访谈。
- 朋友/亲人：聊天摘录 + 关系互动访谈。
- 自己：无语料，仅本人自适应访谈。
- 语料充足：应提前结束访谈。
- 语料不足：应提示缺口并继续追问。
- 用户停止访谈：低覆盖维度进入诚实边界。
- 新语料冲突：系统记录冲突，不强行调和。
- 导出 public skill：不得包含敏感原文。

## Reference Materials

- `references/repos/colleague-skill`
- `references/repos/nuwa-skill`
- `zg-strategy-distillation/`
- `docs/research/reference-repo-review.md`

## Acceptance Criteria

- 设计文档完整覆盖产品、架构、证据、访谈、profile、评审和分期。
- 实施计划能从零开始指导 agentic worker 实现 P0。
- 参考仓库已移入项目 `references/repos/`。
- 文档中不含未决标记。
- 访谈规则明确为信息缺口驱动，而不是强制 20 问。
