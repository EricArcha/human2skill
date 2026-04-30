# human2skill

[English README](README.md)

## 普通用户：我只想使用它

human2skill 是一个 meta-skill，用有限的私有材料和自适应访谈，把一个真实人物提炼成可复用的"视角顾问" Skill。最终的公开产物是可安装的 `SKILL.md`，背后有本地私有 evidence pack 支撑；原始私域材料不会进入可分发 Skill。

### 快速开始

选择你用的 AI 工具：

**Claude Code：**
```bash
cp -r exports/claude-code ~/.claude/skills/human2skill
```
然后在 Claude Code 中输入 **human2skill** 即可启动。

**OpenClaw：**
```bash
cp -r exports/openclaw ~/.openclaw/skills/human2skill
```
然后在 OpenClaw 中输入 **human2skill** 即可启动。

**触发词**（Claude Code 和 OpenClaw 通用）：
- `human2skill`
- `人物蒸馏`
- `创建人物 Skill`
- `更新人物视角`

Meta-skill 会引导你走完完整流程：选择人物档案（同事/关系/导师/自己）、摄入来源语料、自适应访谈、构建结构化证据、生成通过评审的可导出 Skill。

详见 [human2skill-meta/README.md](human2skill-meta/README.md)。

---

## 开发者：我想用 CLI 或参与开发

human2skill 也是一个 Python CLI，是 meta-skill 工作流的底层工具。当前版本面向你身边或你本人熟悉的人：同事、合作者、朋友、亲人、导师、专家、自己或未来的自己。它不是公众人物仿冒工具，也不鼓励生成"我就是某人"的人格冒充。

### 当前已经实现了什么

合并后的 P0-P2 系统已经包含：

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

本地开发产物已经忽略：`.venv/`、`.pytest_cache/`、`.worktrees/`、`build/`、`dist/`、`.claude/`、`references/repos/` 等。

### 安装

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

支持的 host 定义在 `src/human2skill/constants.py`：`codex`、`claude-code`、`openclaw`、`hermes`。

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

生成的 Skill 是"视角顾问"，不是人格冒充。公开 Skill 必须包含免责声明和诚实边界。

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

### 示例

仓库包含三个示例人物：

- `examples/colleague-li-ming`
- `examples/relationship-chen-yu`
- `examples/self-future-me`

每个示例都包含私有证据、公开 Skill、review 报告、导出结果和版本快照。它们既是文件布局参考，也是回归测试 fixture。

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
