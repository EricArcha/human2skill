# human2skill 架构设计

## 1. 总体架构

human2skill 是一个 profile 化 Meta-skill。它把人物蒸馏拆成七个模块，每个模块通过明确文件和数据结构交接。

```text
Intake Router
  -> Corpus Ingestor
  -> Coverage Analyzer
  -> Adaptive Interviewer
  -> Evidence Pack Builder
  -> Distillation Engine
  -> Skill Generator
  -> Reviewer + Evolution Manager
```

## 2. 模块职责

### Intake Router

负责确认创建任务的基本边界。

输入：
- 人物称呼或 slug。
- profile 类型。
- 用户与目标人物关系。
- 用途。
- 同意状态。
- 分发状态。
- 原始语料留存偏好。

输出：
- `person.meta.json` 初始版本。
- profile preset。
- 后续访谈和输出章节的权重配置。

### Corpus Ingestor

负责接收和归档语料。第一版支持：

- 直接粘贴文本。
- Markdown/TXT 文件。
- 手动整理的聊天摘录。
- 会议纪要。
- 工作文档摘要。

P1 扩展：

- PDF 提取。
- 聊天记录导出。
- 邮件和文档批量导入。
- 图片截图 OCR 或视觉读取。

Corpus Ingestor 不直接把原始材料写进 `SKILL.md`。它只生成 `source_index.json` 和可供 Evidence Pack Builder 使用的材料摘要。

### Coverage Analyzer

负责判断当前信息是否足够，输出信息缺口。

覆盖维度：

- 基本身份与关系语境。
- 核心思维模型。
- 表达 DNA。
- 决策习惯。
- 压力和冲突反应。
- profile 专项维度。
- 已知边界和盲区。
- 可用于评估的历史场景。

### Adaptive Interviewer

负责信息缺口驱动的追问。它不是固定 20 问。约 20 轮是默认预算：

- 信息足够时提前结束。
- 信息不足时继续追问。
- 到约 20 轮仍不足时，先提示缺口和继续价值，用户确认后延展。
- 用户不想继续时，相关结论标低置信度并写入诚实边界。

### Evidence Pack Builder

负责把语料和访谈转成结构化证据。证据分三层：

1. 原话/行为记录。
2. 观察者描述。
3. 模型推断。

每条 evidence 必须有 ID、来源摘要、置信度、支持的结论和冲突关系。

### Distillation Engine

负责从证据中提炼人物视角。

输出结构：

- 核心思维模型。
- 表达 DNA。
- 决策启发式。
- profile 专项层。
- 压力/冲突反应。
- 价值排序和反模式。
- 诚实边界。

心智模型优先使用三重验证：

- 跨场景复现。
- 能推断新问题立场。
- 有此人特异性。

未通过三重验证的观点降级为启发式或低置信度观察。

### Skill Generator

负责生成 `public_skill/SKILL.md`。

生成规则：

- 默认是视角顾问，不冒充本人。
- 可以使用此人的表达特征，但避免声称“我就是某某本人”。
- 首次激活说明这是基于材料生成的视角。
- 不输出敏感原文。
- 不提供操控目标人物的建议。

### Reviewer + Evolution Manager

负责质量评审和后续进化。

- 双评审检查生成物。
- 新语料先进入待合并状态。
- 发现冲突时记录冲突，不强行调和。
- 合并后保存版本和更新摘要。
- 记录置信度变化。

## 3. 目录结构

```text
human2skill/
  docs/
  references/
    repos/
      colleague-skill/
      nuwa-skill/
  outputs/
    {slug}/
      person.meta.json
      public_skill/
        SKILL.md
      private_evidence/
        evidence_pack.json
        source_index.json
        interviews/
          interview-YYYYMMDD-HHMM.md
        reviews/
          review-YYYYMMDD-HHMM.md
      versions/
        v1/
        v2/
  templates/
    skill/
    profiles/
    review/
  tools/
```

## 4. 多宿主适配

核心数据结构保持宿主无关。不同宿主只影响：

- skill frontmatter。
- 安装路径。
- 触发方式。
- 可用工具说明。

目标宿主：

| 宿主 | 适配策略 |
| --- | --- |
| Codex | 使用本地 skills 目录和 Markdown skill 入口 |
| Claude Code | 使用 `.claude/skills/{name}/SKILL.md` |
| OpenClaw | 使用 OpenClaw workspace skill 目录 |
| Hermes | 保留 slash command 兼容说明 |

## 5. 与参考仓库的关系

- `colleague-skill` 提供工程化底座参考：schema、preset、writer、version manager、correction。
- `nuwa-skill` 提供提炼方法参考：六维调研、心智模型验证、表达 DNA、诚实边界。
- `zg-strategy-distillation` 提供治理参考：增量更新、矛盾停机、来源和运行日志。

human2skill 的关键改进是公开 Skill 与私有证据包分离，适合私人/身边人场景。
