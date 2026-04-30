# human2skill — 人物视角蒸馏 Meta-Skill

将有限语料和自适应访谈蒸馏为可复用的人物视角顾问 Skill。输出是一个可在 Claude Code / OpenClaw 中安装的 `SKILL.md`，背后有私有证据包支撑。

不做角色扮演，不冒充本人，不输出私域原文。

## 快速安装

### Claude Code

```bash
cp -r exports/claude-code ~/.claude/skills/human2skill
```

### OpenClaw

```bash
cp -r exports/openclaw ~/.openclaw/skills/human2skill
```

## 触发词

在 Claude Code / OpenClaw 中输入以下任一触发词启动：

- `human2skill`
- `人物蒸馏`
- `创建人物 Skill`
- `更新人物视角`

## 它做什么

1. 确认主题人物和关系
2. 选择人物档案（同事/关系/导师/自己）
3. 确认语气模式和隐私配置
4. 摄入来源语料，构建结构化证据包
5. 通过自适应访谈补充信息缺口
6. 编写蒸馏声明，生成公开 Skill
7. 运行结构化评审，导出可安装的 Skill

完整流程详见 [SKILL.md](./SKILL.md)。

## 工程开发

本 meta-skill 编排的是 `human2skill` CLI 工具。如果你想参与 CLI 开发或直接使用 Python API，请参阅项目根目录的 [README.md](../README.md)。
