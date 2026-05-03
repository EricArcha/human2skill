# human2skill Documentation

本目录保存 human2skill 的完整设计与实施规划。

## 文档索引

- `design/human2skill-product-spec.md`：产品目标、用户流程、范围边界。
- `design/human2skill-architecture.md`：核心架构、数据流、目录结构、多宿主适配。
- `design/evidence-model.md`：证据分层、置信度、冲突处理、隐私留存。
- `design/adaptive-interview.md`：信息缺口驱动的自适应访谈设计。
- `design/profile-presets.md`：四类人物 profile 的权重、问题和输出差异。
- `design/quality-review.md`：双评审质量标准、场景回放和失败处理。
- `plans/README.md`：产品路线图目录说明。
- `plans/product-roadmap.md`：完整分期实现路线。
- `research/reference-repo-review.md`：参考仓库研究结论。
- `superpowers/specs/2026-04-29-human2skill-design.md`：Superpowers 流程的正式 design spec。
- `superpowers/plans/README.md`：执行计划目录说明。
- `superpowers/plans/2026-04-29-human2skill-execution-plan.md`：面向 agentic worker 的详细执行计划。

## 目录约定

- `design/`：稳定设计文档，回答“系统应该长什么样”。
- `plans/`：项目和产品层路线图，回答“我们按什么阶段推进”。
- `superpowers/specs/`：正式设计规格，回答“这件事的最终规格是什么”。
- `superpowers/plans/`：给 agentic worker 的执行手册，回答“下一步具体怎么做”。
- `research/`：参考资料和外部仓库研究结论。

## P0-P2 Flow

Use `human2skill create`, `ingest`, `build`, `review`, `export`, and `install` for the local flow. Distillation remains agent-assisted through `distillation.json`; Python validates and renders the durable artifacts.

## 当前决策

- 第一版聚焦私人/身边人，不以公众人物为主。
- 产物是“视角顾问 Skill”，不是冒充本人。
- 默认采用“可运行 Skill + 本地私有证据包”。
- 原始私域语料默认不进入可分发 Skill。
- 访谈有 20 轮硬限制，达到上限后必须暂停由用户决定延展或降级。
- 内置四类 profile：同事/合作者、朋友/亲人、导师/专家、自己。
- 质量评估采用双评审模式。
- 参考仓库保存在 `references/repos/`。
