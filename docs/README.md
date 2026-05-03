# human2skill Documentation

## 目录索引

| 目录 | 内容 | 面向 |
|------|------|------|
| `design/` | 架构决策记录（ADR）：产品规格、系统架构、证据模型、访谈设计、Profile 预设、质量评审 | 开发者 |
| `specs/` | 产品规格演进记录：各阶段正式设计规格 | 开发者 |
| `archive/` | 历史执行计划（已过时，保留备查） | 维护者 |
| `research/` | 参考仓库调研结论 | 开发者 |
| `roadmap.md` | 产品路线图 | 所有人 |

## 核心文档

- `design/human2skill-product-spec.md` — 产品目标、用户流程、范围边界
- `design/human2skill-architecture.md` — 核心架构、数据流、目录结构
- `design/evidence-model.md` — 证据分层、置信度、冲突处理、隐私留存
- `design/adaptive-interview.md` — 信息缺口驱动的自适应访谈设计
- `design/profile-presets.md` — 四类人物 profile 的权重、问题和输出差异
- `design/quality-review.md` — 结构化评审标准和场景回放

## 当前决策

- 第一版聚焦私人/身边人，不以公众人物为主
- 产物是"视角顾问 Skill"，不是冒充本人
- 默认采用"可运行 Skill + 本地私有证据包"
- 原始语料经 PII 扫描后归档至 `corpus/raw/` 用于验证对照，不进入可分发 Skill
- 访谈有 20 轮硬限制，达到上限后必须暂停由用户决定延展或降级
- 内置四类 profile：同事/合作者、朋友/亲人、导师/专家、自己
- 质量评估采用 4 层验证漏斗
- 参考仓库保存在 `references/repos/`
- 治理规则见根目录 `GOVERNANCE.md`
