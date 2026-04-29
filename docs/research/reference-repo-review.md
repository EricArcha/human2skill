# 参考仓库 Review

## 1. 参考仓库位置

- `references/repos/colleague-skill`
- `references/repos/nuwa-skill`
- `zg-strategy-distillation/`

## 2. colleague-skill

### 定位

`colleague-skill` 已从同事场景演化成 `dot-skill`，目标是把不同类型的人物生成成可运行 Skill。

### 可借鉴点

- 通用 meta-skill 入口。
- character family / preset 抽象。
- `work.md` + `persona.md` + `SKILL.md` 的组合结构。
- `meta.json` 和 `manifest.json`。
- 版本管理和 rollback。
- correction 机制：用户说“这不像他”时转成可合并规则。
- 多宿主兼容意识。
- 私域语料导入思路：飞书、钉钉、Slack、微信、邮件、PDF、截图。

### 局限

- 更偏“生成一个像某人的 skill”，对证据置信度和隐私分发边界不够细。
- 结构支持 `knowledge/` 原始材料归档，但私人场景下如果直接随 skill 分发会有风险。
- 同意策略较轻，适合本地自用，但需要 metadata 记录分发状态。

### human2skill 采用方式

- 采用 preset/schema/version/correction 的工程化方向。
- 不直接采用“原始材料跟 skill 放一起”的默认分发方式。
- 把原始私域材料放入本地私有证据区，public skill 只保留摘要化结论。

## 3. nuwa-skill

### 定位

`nuwa-skill` 用于公众人物思维框架蒸馏，强调不是角色扮演，而是提炼认知操作系统。

### 可借鉴点

- 六维调研结构：
  - 著作与系统思考。
  - 长对话与即兴思考。
  - 表达 DNA。
  - 外部评价。
  - 决策记录。
  - 时间线。
- 心智模型三重验证：
  - 跨域复现。
  - 有生成力。
  - 有排他性。
- 表达 DNA 的量化方向。
- 诚实边界。
- 质量自检清单。
- 公开 examples 中保留研究笔记，而不是全部原始材料。

### 局限

- 更适合公众人物，不完全适合私人语料。
- 对私密聊天、朋友圈、关系互动的隐私和同意策略覆盖不足。
- 角色规则中更偏第一人称模拟，human2skill 默认要改成视角顾问。

### human2skill 采用方式

- 采用心智模型、表达 DNA、诚实边界和质量验证方法。
- 把六维调研改造成私人场景的 coverage map。
- 不默认采用第一人称冒充式角色扮演。

## 4. zg-strategy-distillation

### 定位

`zg-strategy-distillation` 是一个增量知识蒸馏 skill，重点不是人物模拟，而是把新内容准确入库。

### 可借鉴点

- 增量更新流程。
- 矛盾必须停机，不擅自调和。
- 来源和时间标注。
- 治理文件和运行日志。
- 子代理并行 QA 的思路。

### 局限

- 面向投资策略知识库，不是通用人物蒸馏。
- 输出目标是知识库更新，不是可运行人物 Skill。
- 对表达 DNA、关系互动和 persona 输出没有覆盖。

### human2skill 采用方式

- 采用“增量合并 + 矛盾停机 + 运行日志”的治理原则。
- 对每次人物 Skill 更新记录变更摘要、证据变化和置信度变化。

## 5. 组合结论

human2skill 应采用三者组合：

- `colleague-skill` 作为工程底座参考。
- `nuwa-skill` 作为思维和表达提炼参考。
- `zg-strategy-distillation` 作为增量治理和冲突处理参考。

关键创新点是公开 Skill 和私有证据包分离，适合私人/身边人蒸馏。
