# 证据模型设计

## 1. 目标

证据模型用于解决三个问题：

- 这个人物结论从哪里来。
- 这个结论有多可信。
- 新语料与旧结论冲突时如何处理。

第一版采用三层证据，不做完整证据图谱，以降低实现和使用成本。

## 2. 三层证据

| 层级 | 类型 | 权重 | 示例 |
| --- | --- | --- | --- |
| L1 | 原话/行为记录 | 最高 | 聊天原话、会议发言、文档作者内容、可验证行为 |
| L2 | 观察者描述 | 中 | 用户说“他被质疑时通常反问依据” |
| L3 | 模型推断 | 最低 | 系统从多条证据推断“他偏好数据驱动判断” |

L1 不代表一定正确，但代表来源最接近目标人物。L2 必须标注观察者偏差。L3 必须能回链到 L1 或 L2。

## 3. evidence_pack.json

```json
{
  "person_slug": "example-person",
  "schema_version": "1",
  "created_at": "2026-04-29T00:00:00+08:00",
  "updated_at": "2026-04-29T00:00:00+08:00",
  "evidence": [
    {
      "evidence_id": "ev-0001",
      "source_type": "direct_quote_or_behavior",
      "source_ref": "src-0001",
      "source_summary": "一次需求评审中，目标人物要求先解释 impact 再讨论方案。",
      "retention": "summary_only",
      "confidence": "high",
      "observed_at": "2026-03",
      "supports": ["claim-decision-impact-first"],
      "conflicts_with": [],
      "notes": "原始会议记录不进入 public_skill。"
    }
  ],
  "claims": [
    {
      "claim_id": "claim-decision-impact-first",
      "claim": "讨论方案前会先追问目标和 impact。",
      "claim_type": "decision_heuristic",
      "profile_scope": "colleague",
      "confidence": "high",
      "evidence_ids": ["ev-0001"],
      "status": "active"
    }
  ]
}
```

## 4. source_index.json

```json
{
  "sources": [
    {
      "source_id": "src-0001",
      "source_kind": "meeting_note",
      "title": "用户提供的需求评审摘录",
      "provided_by": "user",
      "retention": "summary_only",
      "contains_private_data": true,
      "allowed_in_public_skill": false,
      "summary": "讨论接口方案时，目标人物先问 impact 和背景。"
    }
  ]
}
```

## 5. 置信度规则

### High

满足任一条件：

- 多条 L1 证据支持。
- L1 和 L2 互相印证。
- 同一模式跨多个场景复现。

### Medium

满足任一条件：

- 单条强 L1 证据。
- 多条 L2 观察者描述一致。
- L3 推断有足够 L1/L2 支撑，但场景覆盖有限。

### Low

满足任一条件：

- 只有单条 L2 证据。
- 只有模型推断。
- 证据存在明显冲突。
- 用户停止访谈导致关键缺口未补齐。

## 6. 冲突处理

冲突不直接修复，也不强行调和。系统必须分类：

- 时间性冲突：早期和近期不同。
- 场景性冲突：工作、家庭、亲密关系中不同。
- 观察者冲突：不同观察者给出不同描述。
- 本质张力：同一人长期同时存在的矛盾。

冲突处理输出：

```json
{
  "conflict_id": "cf-0001",
  "claims": ["claim-a", "claim-b"],
  "conflict_type": "contextual",
  "resolution": "keep_both_with_scope",
  "note": "工作场景中直接，亲密关系中回避冲突。"
}
```

## 7. 隐私留存

每条 source 和 evidence 必须标注留存策略：

- `no_raw_retention`：不保留原文，只保留摘要。
- `summary_only`：保留结构化摘要，不保留完整原文。
- `local_private_raw`：原文仅保存在本地私有证据区。

默认策略是 `summary_only`。可分发 Skill 只能引用摘要化结论，不包含敏感原文。

## 8. 写入 Skill 的规则

允许写入：

- 高层结论。
- 非敏感的抽象表达习惯。
- 来源类型和置信度摘要。
- 诚实边界。

禁止默认写入：

- 完整聊天记录。
- 私人朋友圈原文。
- 工作文档全文。
- 他人隐私信息。
- 能识别第三方身份的敏感片段。
