# human2skill 产品路线图

## 分期原则

先建立可闭环的最小系统，再扩展语料、评审和多宿主适配。每一期都必须能独立使用和测试。

---

## P0：最小闭环 ✅ 已完成

- Profile preset（4 类）+ metadata + evidence pack schema
- 手动语料导入 + 自适应访谈
- Skill 生成模板（advisor + first_person）
- 结构化评审（7 维度评分）
- 版本快照

## P1：语料扩展与增量进化 ✅ 已完成

- Markdown/TXT/PDF 批量导入 + `pypdf` 文本提取
- 增量 evidence 合并 + 冲突检测
- 版本 diff + 置信度变化报告
- `corpus/raw/` 原文归档 + PII 扫描

## P2：多宿主适配与质量增强 ✅ 已完成

- Claude Code / OpenClaw / Codex / Hermes 多宿主导出
- Phase 0-5 工作流 + 3 个强制 Checkpoint
- 4 层验证漏斗（reviewer → scenario → sub-agent → quality_check.py）
- `quality_check.py` 7 项自动化品质检查
- 场景回放测试集（historical/counterfactual/boundary）
- 导出前隐私检查 + 模板溯源签名

---

## P3：规划中

| 方向 | 说明 |
|------|------|
| 多人物交叉视角 | 同时加载多个人物 Skill 做对比分析 |
| 公开人物语料库 | 支持网络调研采集公众人物的公开材料 |
| 长期漂移检测 | 追踪人物视角随时间的演变 |
| 多观察者证据合并 | 融合多个提供者对同一人物的观察 |
| 聊天导出格式适配 | 自动解析微信/飞书/钉钉等导出格式 |
| Web UI | 非 CLI 用户的可视化蒸馏界面 |
| 本地加密证据区 | 对敏感 evidence 做本地加密存储 |

---

## 当前版本：v2.0.0

P0-P2 全部完成并合并。132 个 pytest 覆盖核心管线。详见 [CHANGELOG.md](../CHANGELOG.md)。
