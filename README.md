# human2skill

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

如果按他的偏好，他会建议先砍掉两个不必要的抽象层，把风险点写进迁移计划。
但我没有足够证据判断他在安全合规问题上的取舍，所以这里需要你再补充材料。
```

## 它适合什么场景？

**同事和合作者**

想保留一个人的工作方法、评审风格和决策习惯。比如“某位资深同事离职了，但我还想用他的视角检查技术方案”。

**朋友、伴侣和家人**

不是替你操控关系，而是帮你理解对方可能怎么接收一段话、什么地方容易误会、哪些判断证据不足。

**导师、专家和顾问**

把一个人长期给你的建议、反馈和判断方式沉淀下来，让它在新问题里继续提供参考。

**自己和未来的自己**

把你的原则、反模式、长期目标和复盘结论做成 Skill。遇到选择时，请“更清醒的自己”提醒现在的你。

## 它产出什么？

human2skill 最终会生成两类东西：

```text
people/{slug}/
  public_skill/
    SKILL.md                  # 可安装、可分享的公开 Skill
    variants/
      advisor/SKILL.md        # 默认：视角顾问
      first_person/SKILL.md   # 可选：自用第一人称版本
  private_evidence/
    source_index.json         # 私有材料索引
    evidence_pack.json        # 结构化证据包
    distillation.json         # agent 辅助提炼结果
    reviews/                  # 质量和隐私评审
  exports/
    codex/SKILL.md            # 面向不同宿主的导出结果
```

公开 Skill 是轻量的：它只保留摘要化的思维模型、表达 DNA、决策启发式、反模式和诚实边界。

私有材料留在本地 evidence pack 里，不会默认进入可分发的 `SKILL.md`。这是 human2skill 和很多“人格模拟”工具最重要的区别。

## 它蒸馏的不是“像不像”，而是“怎么想”

一个有用的人物 Skill 不应该只会复读口头禅。human2skill 更关注五层内容：

| 层次 | 它会提炼什么 |
| --- | --- |
| 思维模型 | 这个人习惯怎样拆问题、找关键变量、判断优先级 |
| 表达 DNA | 这个人怎样解释、反馈、反驳、安慰或推进讨论 |
| 决策启发式 | 他在信息不完整时通常怎么做取舍 |
| 反模式 | 他容易过度使用、误判或不适用的模式 |
| 诚实边界 | 哪些事情证据不足，不能装作知道 |

所以它默认是“视角顾问”，不是“我就是某某”。它会提醒你：哪些判断来自证据，哪些只是低置信度推断。

## 快速开始

选择你使用的 AI 工具：

**Claude Code**

```bash
cp -r exports/claude-code ~/.claude/skills/human2skill
```

然后在 Claude Code 中输入：

```text
human2skill
```

**OpenClaw**

```bash
cp -r exports/openclaw ~/.openclaw/skills/human2skill
```

然后在 OpenClaw 中输入：

```text
human2skill
```

常用触发词：

- `human2skill`
- `人物蒸馏`
- `创建人物 Skill`
- `更新人物视角`

启动后，meta-skill 会引导你完成：选择人物类型、提供材料、补充访谈、生成证据包、构建 Skill、通过评审并导出。

更详细的 meta-skill 流程见 [human2skill-meta/README.md](human2skill-meta/README.md)。

## 一个完整例子

假设你想创建一位同事“李明”的视角顾问。

你可以提供：

- 他写过的技术方案或评审意见。
- 你整理的会议纪要。
- 你对他工作风格的观察。
- 几轮访谈回答，比如“他遇到 deadline 通常怎么取舍？”

human2skill 会把这些材料变成：

- 核心思维模型：例如“先拆问题，再验证假设”。
- 表达 DNA：例如“先肯定，再指出改进空间”。
- 决策启发式：例如“可逆决策快速推进，不可逆决策拉人评审”。
- 反模式：例如“有时会对简单问题引入过多抽象”。
- 诚实边界：例如“缺少非工作场景证据，不推断他的私人关系处理方式”。

生成后，你可以这样使用：

```text
用李明的视角帮我看这个 PR 说明够不够清楚。
```

```text
如果李明来评审这套技术方案，他最可能挑战哪几个假设？
```

```text
这段反馈发给李明会不会太硬？帮我从他的沟通偏好看一下。
```

仓库里有三个可查看的样例：

- [examples/colleague-li-ming](examples/colleague-li-ming)
- [examples/relationship-chen-yu](examples/relationship-chen-yu)
- [examples/self-future-me](examples/self-future-me)

## 为什么需要 evidence pack？

因为私人/身边人的 Skill 很容易踩三个坑：

1. **过度自信**：材料很少，却写得像完全了解这个人。
2. **隐私泄露**：把聊天记录、朋友圈、工作文档原文塞进公开 Skill。
3. **人格冒充**：让 AI 说“我就是他”，模糊边界。

human2skill 用本地 evidence pack 解决这些问题：

- 每条结论都应该能追溯到证据或访谈。
- 证据不足时，结论必须降置信度或写入诚实边界。
- 公开 Skill 不包含私域原文。
- review/export gate 会阻止明显不安全或质量不足的产物导出。

## 开发者说明

human2skill 也是一个 Python CLI。当前版本面向你身边或你本人熟悉的人：同事、合作者、朋友、亲人、导师、专家、自己或未来的自己。它不是公众人物仿冒工具，也不鼓励生成“我就是某人”的人格冒充。

### 已实现能力

- 在 `people/{slug}` 下创建人物项目。
- 摄入 `.txt`、`.md` 和可提取文本的 `.pdf` 文件。
- 内置四类 profile：`colleague`、`relationship`、`mentor`、`self`。
- 基于信息缺口选择下一轮访谈问题。
- Evidence Pack Builder API：管理 evidence、claims、conflicts。
- 通过 `distillation.json` 接入 agent 辅助提炼，并由 Python 做结构校验。
- 渲染 advisor 和 first-person 两种 Skill 变体。
- 结构化 review：硬失败条件 + 各维度评分阈值。
- 按变体执行 export gate，防止 advisor / first_person review 串用。
- 安装已导出的 Skill 到目标目录。
- 版本快照、changelog 辅助和版本恢复。
- `examples/` 下的完整示例项目。
- 132 个 pytest 测试覆盖当前 P0-P2 主流程。

重要边界：human2skill 目前不会完全自动从原始材料推理出一个人的视角。高判断力的 distillation 仍由宿主 agent 辅助完成；Python 负责校验、渲染、review、export、install 和持久化状态。

### 仓库结构

```text
src/human2skill/           Python 包和 CLI 实现
src/human2skill/schemas/   打包进 wheel 的 JSON Schema
src/human2skill/templates/ 打包进 wheel 的 profile 和 Skill 模板
tests/                     Pytest 测试
examples/                  已生成的人物示例和导出 Skill
exports/                   可直接安装到各宿主的 meta-skill 包
docs/                      产品、架构、质量和计划文档
human2skill-meta/          Meta-skill 文档
zg-strategy-distillation/  仓库内保留的既有参考 Skill
```

### 安装开发环境

需要 Python 3.11 或更新版本。

```bash
python3 -m venv .venv
.venv/bin/pip install ".[dev]"
```

安装后可以直接调用：

```bash
human2skill --help
```

如果在本地持续编辑源码，测试也可以直接从 checkout 运行，因为 `pyproject.toml` 已经为 pytest 配置了 `src` import path。改动 CLI 或包元数据后，重新安装一次 package。

### CLI 调用流程

创建人物项目：

```bash
human2skill create \
  --root workspace \
  --slug li-ming \
  --name "李明" \
  --profile colleague \
  --relationship coworker \
  --use-case "work review and collaboration" \
  --voice-mode both
```

摄入私有材料：

```bash
human2skill ingest \
  --root workspace \
  --slug li-ming \
  --file notes/li-ming.md
```

获取下一轮访谈问题：

```bash
human2skill question \
  --root workspace \
  --slug li-ming \
  --profile colleague \
  --perspective observer_answer \
  --turn 1
```

让宿主 agent 准备 `workspace/people/li-ming/private_evidence/distillation.json`，然后构建：

```bash
human2skill build --root workspace --slug li-ming
```

查看 review JSON：

```bash
human2skill review --root workspace --slug li-ming --variant advisor
```

导出已通过 review 的 Skill 变体：

```bash
human2skill export \
  --root workspace \
  --slug li-ming \
  --host codex \
  --variant advisor
```

安装导出的 Skill：

```bash
human2skill install \
  --export workspace/people/li-ming/exports/codex \
  --target ~/.codex/skills \
  --name li-ming-perspective
```

支持的 host 定义在 `src/human2skill/constants.py`：`codex`、`claude-code`、`openclaw` 和 `hermes`。

### Python API 调用

```python
from pathlib import Path

from human2skill.flow import create_project_person, build_from_distillation
from human2skill.ingest import ingest_file
from human2skill.exporter import export_skill

root = Path("workspace")

base = create_project_person(
    root=root,
    slug="li-ming",
    display_name="李明",
    profile_type="colleague",
    relationship_to_user="coworker",
    use_case="work review and collaboration",
    voice_mode="advisor",
)

ingest_file(base, Path("notes/li-ming.md"))

# distillation 由 agent 辅助生成并作为 JSON payload 传入。
# result = build_from_distillation(base, distillation)
# export_dir = export_skill(base, host="codex", variant="advisor")
```

### 质量和隐私门禁

以下情况会阻止 review/export：

- Skill 声称自己就是该人物。
- 缺少免责声明或诚实边界。
- 公开内容中出现原始私域材料标记。
- 存在缺少证据支撑的高置信度结论。
- 仍有阻塞性冲突未处理。
- 任一必需评分维度低于通过阈值。

Export 是变体绑定的：导出 `advisor` 必须有 advisor review 通过；导出 `first_person` 必须有 first-person review 通过。

冲突语义：

- `halt_for_review` 会阻塞 build/review。
- `keep_both_with_scope` 和 `mark_low_confidence` 是可接受的冲突处理方式，本身不会导致 review 失败。

### 开发验证

跑完整测试：

```bash
.venv/bin/python -m pytest -q
```

构建 wheel：

```bash
.venv/bin/python -m pip wheel . -w /tmp/human2skill-wheel --no-deps
```

wheel 应包含 `src/human2skill/schemas/` 和 `src/human2skill/templates/` 下的 schema 与模板资源。

### 已知限制

- distillation synthesis 仍由 agent 辅助完成。
- reviewer 是确定性的启发式检查器；它能执行阈值门禁，但不是语义全知审稿人。
- CLI `review` 支持 `--variant`；不传时保留向后兼容的 latest-file 行为。
- 当前没有远程服务、数据库或 UI；状态全部是本地 JSON 和 Markdown 文件。
