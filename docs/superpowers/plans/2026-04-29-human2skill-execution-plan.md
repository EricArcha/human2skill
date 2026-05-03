# human2skill Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a profile-based meta-skill that distills private/personally known humans into reusable perspective-advisor Skills using source material, adaptive interviews, private evidence packs, review, and versioned evolution.

**Architecture:** The system is a host-neutral core with thin adapters for Codex, Claude Code, OpenClaw, and Hermes. A person directory stores public skill output separately from private evidence. The core flow is intake -> ingest -> coverage -> interview -> evidence -> distill -> generate -> review -> evolve.

**Tech Stack:** Markdown skills, JSON schemas, Python 3 CLI utilities, local filesystem storage, pytest for schema and flow tests.

---

## File Structure

- Create `templates/skill/base-perspective-advisor.md`: public skill rendering template.
- Create `templates/profiles/*.json`: four profile preset files.
- Create `schemas/person.meta.schema.json`: metadata schema.
- Create `schemas/evidence_pack.schema.json`: evidence schema.
- Create `src/human2skill/profiles.py`: profile loading and selection.
- Create `src/human2skill/evidence.py`: evidence and claim validation.
- Create `src/human2skill/interview.py`: coverage map and next-question selection.
- Create `src/human2skill/generator.py`: render `SKILL.md`.
- Create `src/human2skill/reviewer.py`: review checks.
- Create `src/human2skill/storage.py`: person directory and version management.
- Create `tests/`: unit tests for each module.

## Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/human2skill/__init__.py`
- Create: `tests/test_import.py`

- [ ] **Step 1: Create package config**

Create `pyproject.toml`:

```toml
[project]
name = "human2skill"
version = "0.1.0"
description = "Distill private human perspectives into reusable skills"
requires-python = ">=3.11"
dependencies = [
  "jsonschema>=4.22.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0.0"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Create package marker**

Create `src/human2skill/__init__.py`:

```python
"""human2skill core package."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Add import test**

Create `tests/test_import.py`:

```python
def test_package_imports():
    import human2skill

    assert human2skill.__version__ == "0.1.0"
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/test_import.py -q`

Expected: `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/human2skill/__init__.py tests/test_import.py
git commit -m "chore: initialize human2skill package"
```

## Task 2: Schemas

**Files:**
- Create: `schemas/person.meta.schema.json`
- Create: `schemas/evidence_pack.schema.json`
- Create: `tests/test_schemas.py`

- [ ] **Step 1: Create person metadata schema**

Create `schemas/person.meta.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["schema_version", "slug", "display_name", "profile_type", "privacy_policy", "lifecycle"],
  "properties": {
    "schema_version": {"const": "1"},
    "slug": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
    "display_name": {"type": "string", "minLength": 1},
    "profile_type": {"enum": ["colleague", "relationship", "mentor", "self"]},
    "relationship_to_user": {"type": "string"},
    "use_case": {"type": "string"},
    "consent_status": {
      "type": "object",
      "required": ["person_consented", "distribution_allowed"],
      "properties": {
        "person_consented": {"type": "boolean"},
        "distribution_allowed": {"type": "boolean"},
        "notes": {"type": "string"}
      },
      "additionalProperties": false
    },
    "privacy_policy": {
      "type": "object",
      "required": ["raw_retention", "public_skill_allows_private_quotes"],
      "properties": {
        "raw_retention": {"enum": ["no_raw_retention", "summary_only", "local_private_raw"]},
        "public_skill_allows_private_quotes": {"const": false}
      },
      "additionalProperties": false
    },
    "lifecycle": {
      "type": "object",
      "required": ["version", "created_at", "updated_at"],
      "properties": {
        "version": {"type": "string", "pattern": "^v[0-9]+$"},
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"}
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

- [ ] **Step 2: Create evidence pack schema**

Create `schemas/evidence_pack.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["schema_version", "person_slug", "evidence", "claims"],
  "properties": {
    "schema_version": {"const": "1"},
    "person_slug": {"type": "string"},
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["evidence_id", "source_type", "source_summary", "retention", "confidence", "supports"],
        "properties": {
          "evidence_id": {"type": "string", "pattern": "^ev-[0-9]{4}$"},
          "source_type": {"enum": ["direct_quote_or_behavior", "observer_report", "model_inference"]},
          "source_ref": {"type": "string"},
          "source_summary": {"type": "string", "minLength": 1},
          "retention": {"enum": ["no_raw_retention", "summary_only", "local_private_raw"]},
          "confidence": {"enum": ["high", "medium", "low"]},
          "observed_at": {"type": "string"},
          "supports": {"type": "array", "items": {"type": "string"}},
          "conflicts_with": {"type": "array", "items": {"type": "string"}},
          "notes": {"type": "string"}
        },
        "additionalProperties": false
      }
    },
    "claims": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["claim_id", "claim", "claim_type", "confidence", "evidence_ids", "status"],
        "properties": {
          "claim_id": {"type": "string", "pattern": "^claim-[a-z0-9-]+$"},
          "claim": {"type": "string", "minLength": 1},
          "claim_type": {"enum": ["mental_model", "decision_heuristic", "expression_dna", "profile_specific", "boundary"]},
          "profile_scope": {"type": "string"},
          "confidence": {"enum": ["high", "medium", "low"]},
          "evidence_ids": {"type": "array", "items": {"type": "string"}},
          "status": {"enum": ["active", "conflicted", "deprecated"]}
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

- [ ] **Step 3: Add schema tests**

Create `tests/test_schemas.py`:

```python
import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load_schema(name):
    return json.loads(Path("schemas", name).read_text(encoding="utf-8"))


def test_person_meta_schema_accepts_minimal_valid_document():
    schema = load_schema("person.meta.schema.json")
    document = {
        "schema_version": "1",
        "slug": "zhang-san",
        "display_name": "张三",
        "profile_type": "colleague",
        "relationship_to_user": "coworker",
        "use_case": "work perspective advisor",
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local personal use"
        },
        "privacy_policy": {
            "raw_retention": "summary_only",
            "public_skill_allows_private_quotes": False
        },
        "lifecycle": {
            "version": "v1",
            "created_at": "2026-04-29T00:00:00+08:00",
            "updated_at": "2026-04-29T00:00:00+08:00"
        }
    }

    Draft202012Validator(schema).validate(document)


def test_evidence_pack_schema_accepts_minimal_valid_document():
    schema = load_schema("evidence_pack.schema.json")
    document = {
        "schema_version": "1",
        "person_slug": "zhang-san",
        "evidence": [
            {
                "evidence_id": "ev-0001",
                "source_type": "observer_report",
                "source_summary": "User reports that Zhang San asks for impact before discussing plans.",
                "retention": "summary_only",
                "confidence": "medium",
                "supports": ["claim-impact-first"],
                "conflicts_with": [],
                "notes": "observer report"
            }
        ],
        "claims": [
            {
                "claim_id": "claim-impact-first",
                "claim": "He asks for impact before discussing plans.",
                "claim_type": "decision_heuristic",
                "profile_scope": "colleague",
                "confidence": "medium",
                "evidence_ids": ["ev-0001"],
                "status": "active"
            }
        ]
    }

    Draft202012Validator(schema).validate(document)
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_schemas.py -q`

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add schemas/person.meta.schema.json schemas/evidence_pack.schema.json tests/test_schemas.py
git commit -m "feat: add human2skill schemas"
```

## Task 3: Profile Presets

**Files:**
- Create: `templates/profiles/colleague.json`
- Create: `templates/profiles/relationship.json`
- Create: `templates/profiles/mentor.json`
- Create: `templates/profiles/self.json`
- Create: `src/human2skill/profiles.py`
- Create: `tests/test_profiles.py`

- [ ] **Step 1: Create colleague profile**

Create `templates/profiles/colleague.json`:

```json
{
  "profile_type": "colleague",
  "display_name": "同事/合作者",
  "core_sections": ["mental_models", "expression_dna", "decision_heuristics", "pressure_response", "honest_boundaries"],
  "special_sections": ["work_scope", "workflow", "collaboration_rules", "output_preferences"],
  "weights": {
    "work_method": 5,
    "decision_standard": 5,
    "expression": 4,
    "relationship_interaction": 3,
    "emotional_support": 1
  }
}
```

- [ ] **Step 2: Create relationship profile**

Create `templates/profiles/relationship.json`:

```json
{
  "profile_type": "relationship",
  "display_name": "朋友/亲人",
  "core_sections": ["mental_models", "expression_dna", "decision_heuristics", "pressure_response", "honest_boundaries"],
  "special_sections": ["relationship_patterns", "emotional_triggers", "support_style", "conflict_repair", "boundaries"],
  "weights": {
    "relationship_interaction": 5,
    "emotional_response": 5,
    "expression": 5,
    "value_order": 4,
    "work_method": 1
  }
}
```

- [ ] **Step 3: Create mentor profile**

Create `templates/profiles/mentor.json`:

```json
{
  "profile_type": "mentor",
  "display_name": "导师/专家",
  "core_sections": ["mental_models", "expression_dna", "decision_heuristics", "pressure_response", "honest_boundaries"],
  "special_sections": ["view_system", "judgment_framework", "teaching_style", "feedback_style", "known_blindspots"],
  "weights": {
    "view_system": 5,
    "judgment_framework": 5,
    "teaching_feedback": 4,
    "expression": 4,
    "relationship_interaction": 3
  }
}
```

- [ ] **Step 4: Create self profile**

Create `templates/profiles/self.json`:

```json
{
  "profile_type": "self",
  "display_name": "自己",
  "core_sections": ["mental_models", "expression_dna", "decision_heuristics", "pressure_response", "honest_boundaries"],
  "special_sections": ["self_reflection", "decision_mirror", "long_term_preferences", "recurring_blindspots"],
  "weights": {
    "self_reflection": 5,
    "decision_mirror": 5,
    "long_term_preference": 5,
    "expression": 3,
    "relationship_interaction": 3
  }
}
```

- [ ] **Step 5: Implement profile loader**

Create `src/human2skill/profiles.py`:

```python
import json
from pathlib import Path


PROFILE_TYPES = ("colleague", "relationship", "mentor", "self")


def profile_dir() -> Path:
    return Path("templates/profiles")


def load_profile(profile_type: str) -> dict:
    if profile_type not in PROFILE_TYPES:
        raise ValueError(f"Unknown profile type: {profile_type}")
    return json.loads((profile_dir() / f"{profile_type}.json").read_text(encoding="utf-8"))


def infer_profile_type(text: str) -> str:
    normalized = text.lower()
    colleague_markers = ("公司", "同事", "上级", "下级", "项目", "评审", "prd", "review", "交付")
    relationship_markers = ("朋友", "亲人", "伴侣", "父母", "孩子", "关系", "情绪")
    mentor_markers = ("导师", "老师", "专家", "顾问", "课程", "方法论", "博主")
    self_markers = ("我自己", "过去的我", "未来的我", "self")

    if any(marker in normalized for marker in self_markers):
        return "self"
    if any(marker in normalized for marker in colleague_markers):
        return "colleague"
    if any(marker in normalized for marker in relationship_markers):
        return "relationship"
    if any(marker in normalized for marker in mentor_markers):
        return "mentor"
    return "relationship"
```

- [ ] **Step 6: Add profile tests**

Create `tests/test_profiles.py`:

```python
from human2skill.profiles import infer_profile_type, load_profile


def test_loads_all_profiles():
    for profile_type in ("colleague", "relationship", "mentor", "self"):
        profile = load_profile(profile_type)
        assert profile["profile_type"] == profile_type
        assert "core_sections" in profile
        assert "special_sections" in profile


def test_infers_colleague_from_work_context():
    assert infer_profile_type("字节同事，负责项目评审") == "colleague"


def test_infers_relationship_from_family_context():
    assert infer_profile_type("这是我的亲人，主要想理解关系和情绪") == "relationship"


def test_infers_mentor_from_expert_context():
    assert infer_profile_type("他是我的导师，擅长方法论") == "mentor"


def test_infers_self_from_self_context():
    assert infer_profile_type("我想蒸馏过去的我") == "self"
```

- [ ] **Step 7: Run tests**

Run: `python -m pytest tests/test_profiles.py -q`

Expected: `5 passed`.

- [ ] **Step 8: Commit**

```bash
git add templates/profiles src/human2skill/profiles.py tests/test_profiles.py
git commit -m "feat: add profile presets"
```

## Task 4: Evidence Validation

**Files:**
- Create: `src/human2skill/evidence.py`
- Create: `tests/test_evidence.py`

- [ ] **Step 1: Implement evidence validation helpers**

Create `src/human2skill/evidence.py`:

```python
SOURCE_WEIGHT = {
    "direct_quote_or_behavior": 3,
    "observer_report": 2,
    "model_inference": 1,
}


def evidence_by_id(pack: dict) -> dict[str, dict]:
    return {item["evidence_id"]: item for item in pack.get("evidence", [])}


def claim_support_level(pack: dict, claim: dict) -> str:
    evidence = evidence_by_id(pack)
    items = [evidence[eid] for eid in claim.get("evidence_ids", []) if eid in evidence]
    if not items:
        return "unsupported"
    direct_count = sum(1 for item in items if item["source_type"] == "direct_quote_or_behavior")
    observer_count = sum(1 for item in items if item["source_type"] == "observer_report")
    if direct_count >= 2 or (direct_count >= 1 and observer_count >= 1):
        return "high"
    if direct_count == 1 or observer_count >= 2:
        return "medium"
    return "low"


def find_overconfident_claims(pack: dict) -> list[dict]:
    result = []
    rank = {"unsupported": 0, "low": 1, "medium": 2, "high": 3}
    for claim in pack.get("claims", []):
        support = claim_support_level(pack, claim)
        if rank[support] < rank[claim["confidence"]]:
            result.append({"claim_id": claim["claim_id"], "claimed": claim["confidence"], "supported": support})
    return result
```

- [ ] **Step 2: Add evidence tests**

Create `tests/test_evidence.py`:

```python
from human2skill.evidence import claim_support_level, find_overconfident_claims


def test_claim_with_direct_and_observer_support_is_high():
    pack = {
        "evidence": [
            {"evidence_id": "ev-0001", "source_type": "direct_quote_or_behavior"},
            {"evidence_id": "ev-0002", "source_type": "observer_report"}
        ]
    }
    claim = {"evidence_ids": ["ev-0001", "ev-0002"], "confidence": "high"}

    assert claim_support_level(pack, claim) == "high"


def test_flags_overconfident_claim():
    pack = {
        "evidence": [
            {"evidence_id": "ev-0001", "source_type": "model_inference"}
        ],
        "claims": [
            {
                "claim_id": "claim-too-strong",
                "confidence": "high",
                "evidence_ids": ["ev-0001"]
            }
        ]
    }

    assert find_overconfident_claims(pack) == [
        {"claim_id": "claim-too-strong", "claimed": "high", "supported": "low"}
    ]
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_evidence.py -q`

Expected: `2 passed`.

- [ ] **Step 4: Commit**

```bash
git add src/human2skill/evidence.py tests/test_evidence.py
git commit -m "feat: validate evidence confidence"
```

## Task 5: Adaptive Interview

**Files:**
- Create: `src/human2skill/interview.py`
- Create: `tests/test_interview.py`

- [ ] **Step 1: Implement coverage and prompt selection**

Create `src/human2skill/interview.py`:

```python
CORE_DIMENSIONS = (
    "identity_context",
    "mental_models",
    "expression_dna",
    "decision_heuristics",
    "pressure_response",
    "profile_specific",
    "honest_boundaries",
    "evaluation_scenarios",
)


QUESTION_BANK = {
    "identity_context": "这个人是谁？你和他是什么关系？你最想用这个视角解决什么问题？",
    "mental_models": "他遇到复杂问题时，通常先看什么？能举一个具体场景吗？",
    "expression_dna": "他常说的三句话是什么？请尽量贴近原话。",
    "decision_heuristics": "他在什么情况下会推进、等待、拒绝或改变主意？",
    "pressure_response": "他被催、被质疑或遇到冲突时，通常怎么反应？",
    "profile_specific": "按这个人的身份，最能代表他的专项能力或互动方式是什么？",
    "honest_boundaries": "哪些问题上你不确定他会怎么想？有没有反例？",
    "evaluation_scenarios": "请给一个历史场景和一个新场景，用来测试生成后的 Skill。"
}


def initial_coverage() -> dict[str, str]:
    return {dimension: "missing" for dimension in CORE_DIMENSIONS}


def next_question(coverage: dict[str, str], turn_count: int) -> str:
    for dimension in CORE_DIMENSIONS:
        if coverage.get(dimension) in ("missing", "low"):
            if turn_count >= 20:
                return (
                    "目前已经接近默认访谈预算，但仍缺少关键信息。"
                    f" 下一步建议补充：{QUESTION_BANK[dimension]}"
                )
            return QUESTION_BANK[dimension]
    return "信息覆盖已经足够，可以进入蒸馏。"


def should_continue(coverage: dict[str, str]) -> bool:
    return any(value in ("missing", "low") for value in coverage.values())
```

- [ ] **Step 2: Add interview tests**

Create `tests/test_interview.py`:

```python
from human2skill.interview import initial_coverage, next_question, should_continue


def test_initial_coverage_marks_all_missing():
    coverage = initial_coverage()

    assert coverage["mental_models"] == "missing"
    assert coverage["expression_dna"] == "missing"


def test_next_question_targets_first_missing_dimension():
    coverage = initial_coverage()

    assert "这个人是谁" in next_question(coverage, turn_count=0)


def test_turn_twenty_prompts_before_extending():
    coverage = initial_coverage()
    coverage["identity_context"] = "medium"

    question = next_question(coverage, turn_count=20)

    assert "接近默认访谈预算" in question
    assert "复杂问题" in question


def test_should_stop_when_all_dimensions_medium_or_high():
    coverage = {key: "medium" for key in initial_coverage()}

    assert should_continue(coverage) is False
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_interview.py -q`

Expected: `4 passed`.

- [ ] **Step 4: Commit**

```bash
git add src/human2skill/interview.py tests/test_interview.py
git commit -m "feat: add adaptive interview coverage"
```

## Task 6: Skill Generation

**Files:**
- Create: `templates/skill/base-perspective-advisor.md`
- Create: `src/human2skill/generator.py`
- Create: `tests/test_generator.py`

- [ ] **Step 1: Create skill template**

Create `templates/skill/base-perspective-advisor.md`:

```markdown
---
name: {skill_name}
description: {description}
user-invocable: true
---

# {display_name} 视角顾问

此 Skill 基于用户提供材料和访谈提炼，用于模拟此人的思维和表达视角，不代表本人观点，也不冒充本人。

## 使用协议

- 以“视角顾问”方式回答，不声称自己就是 {display_name} 本人。
- 优先使用已提炼的思维模型和表达 DNA。
- 遇到证据不足的问题，明确说明不确定。
- 不输出私域原文，不代发消息，不替用户操控关系。

## 核心思维模型

{mental_models}

## 表达 DNA

{expression_dna}

## 决策启发式

{decision_heuristics}

## Profile 专项层

{profile_specific}

## 压力和冲突反应

{pressure_response}

## 诚实边界

{honest_boundaries}
```

- [ ] **Step 2: Implement generator**

Create `src/human2skill/generator.py`:

```python
from pathlib import Path


def render_list(items: list[str]) -> str:
    if not items:
        return "- 证据不足，暂不生成高置信度结论。"
    return "\n".join(f"- {item}" for item in items)


def render_skill(meta: dict, distilled: dict, template_path: Path | None = None) -> str:
    template = (template_path or Path("templates/skill/base-perspective-advisor.md")).read_text(encoding="utf-8")
    skill_name = f"{meta['slug']}-perspective"
    return template.format(
        skill_name=skill_name,
        description=f"{meta['display_name']} 的视角顾问 Skill",
        display_name=meta["display_name"],
        mental_models=render_list(distilled.get("mental_models", [])),
        expression_dna=render_list(distilled.get("expression_dna", [])),
        decision_heuristics=render_list(distilled.get("decision_heuristics", [])),
        profile_specific=render_list(distilled.get("profile_specific", [])),
        pressure_response=render_list(distilled.get("pressure_response", [])),
        honest_boundaries=render_list(distilled.get("honest_boundaries", [])),
    )
```

- [ ] **Step 3: Add generator tests**

Create `tests/test_generator.py`:

```python
from human2skill.generator import render_skill


def test_render_skill_uses_perspective_advisor_protocol():
    meta = {"slug": "zhang-san", "display_name": "张三"}
    distilled = {
        "mental_models": ["先问目标和 impact，再讨论方案。"],
        "expression_dna": ["短句、反问、结论先行。"],
        "decision_heuristics": ["没有明确收益时倾向推迟。"],
        "profile_specific": ["适合工作评审场景。"],
        "pressure_response": ["被质疑时先问判断依据。"],
        "honest_boundaries": ["亲密关系场景证据不足。"]
    }

    content = render_skill(meta, distilled)

    assert "张三 视角顾问" in content
    assert "不代表本人观点" in content
    assert "不声称自己就是 张三 本人" in content
    assert "先问目标和 impact" in content
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_generator.py -q`

Expected: `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add templates/skill/base-perspective-advisor.md src/human2skill/generator.py tests/test_generator.py
git commit -m "feat: render perspective advisor skill"
```

## Task 7: Review Checks

**Files:**
- Create: `src/human2skill/reviewer.py`
- Create: `tests/test_reviewer.py`

- [ ] **Step 1: Implement review checks**

Create `src/human2skill/reviewer.py`:

```python
PRIVATE_MARKERS = ("完整聊天记录", "身份证", "手机号", "原始私聊", "朋友圈原文")


def review_public_skill(content: str) -> dict:
    failures = []
    if "我就是" in content:
        failures.append("claims_to_be_person")
    if "诚实边界" not in content:
        failures.append("missing_honest_boundaries")
    if any(marker in content for marker in PRIVATE_MARKERS):
        failures.append("contains_private_raw_material")
    if "不代表本人观点" not in content:
        failures.append("missing_disclaimer")
    return {"passed": not failures, "failures": failures}
```

- [ ] **Step 2: Add reviewer tests**

Create `tests/test_reviewer.py`:

```python
from human2skill.reviewer import review_public_skill


def test_review_passes_safe_skill():
    content = "不代表本人观点\n## 诚实边界\n- 证据不足时会说明不确定。"

    assert review_public_skill(content) == {"passed": True, "failures": []}


def test_review_fails_impersonation():
    content = "我就是张三\n## 诚实边界\n不代表本人观点"

    result = review_public_skill(content)

    assert result["passed"] is False
    assert "claims_to_be_person" in result["failures"]


def test_review_fails_private_raw_material():
    content = "不代表本人观点\n## 诚实边界\n这里包含完整聊天记录。"

    result = review_public_skill(content)

    assert result["passed"] is False
    assert "contains_private_raw_material" in result["failures"]
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_reviewer.py -q`

Expected: `3 passed`.

- [ ] **Step 4: Commit**

```bash
git add src/human2skill/reviewer.py tests/test_reviewer.py
git commit -m "feat: review generated public skill"
```

## Task 8: Storage and Versions

**Files:**
- Create: `src/human2skill/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Implement storage helpers**

Create `src/human2skill/storage.py`:

```python
import json
import shutil
from pathlib import Path


def person_dir(root: Path, slug: str) -> Path:
    return root / "people" / slug


def initialize_person_dir(root: Path, slug: str) -> Path:
    base = person_dir(root, slug)
    for relative in (
        "public_skill",
        "private_evidence/interviews",
        "private_evidence/reviews",
        "versions",
    ):
        (base / relative).mkdir(parents=True, exist_ok=True)
    return base


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def snapshot_version(base: Path, version: str) -> Path:
    target = base / "versions" / version
    target.mkdir(parents=True, exist_ok=True)
    for relative in ("person.meta.json", "public_skill/SKILL.md", "private_evidence/evidence_pack.json"):
        source = base / relative
        if source.exists():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    return target
```

- [ ] **Step 2: Add storage tests**

Create `tests/test_storage.py`:

```python
from pathlib import Path

from human2skill.storage import initialize_person_dir, snapshot_version, write_json


def test_initialize_person_dir_creates_expected_layout(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "zhang-san")

    assert (base / "public_skill").is_dir()
    assert (base / "private_evidence/interviews").is_dir()
    assert (base / "private_evidence/reviews").is_dir()
    assert (base / "versions").is_dir()


def test_snapshot_version_copies_core_artifacts(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "zhang-san")
    write_json(base / "person.meta.json", {"slug": "zhang-san"})
    (base / "public_skill/SKILL.md").write_text("# skill", encoding="utf-8")
    write_json(base / "private_evidence/evidence_pack.json", {"schema_version": "1"})

    snapshot = snapshot_version(base, "v1")

    assert (snapshot / "person.meta.json").exists()
    assert (snapshot / "public_skill/SKILL.md").exists()
    assert (snapshot / "private_evidence/evidence_pack.json").exists()
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_storage.py -q`

Expected: `2 passed`.

- [ ] **Step 4: Commit**

```bash
git add src/human2skill/storage.py tests/test_storage.py
git commit -m "feat: manage person storage and versions"
```

## Task 9: End-to-End Smoke Flow

**Files:**
- Create: `tests/test_smoke_flow.py`

- [ ] **Step 1: Add smoke test**

Create `tests/test_smoke_flow.py`:

```python
from pathlib import Path

from human2skill.generator import render_skill
from human2skill.reviewer import review_public_skill
from human2skill.storage import initialize_person_dir, snapshot_version, write_json


def test_minimal_person_flow(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "zhang-san")
    meta = {
        "schema_version": "1",
        "slug": "zhang-san",
        "display_name": "张三",
        "profile_type": "colleague"
    }
    evidence_pack = {
        "schema_version": "1",
        "person_slug": "zhang-san",
        "evidence": [],
        "claims": []
    }
    distilled = {
        "mental_models": ["讨论方案前先问 impact。"],
        "expression_dna": ["短句，结论先行。"],
        "honest_boundaries": ["关系场景证据不足。"]
    }

    write_json(base / "person.meta.json", meta)
    write_json(base / "private_evidence/evidence_pack.json", evidence_pack)
    skill = render_skill(meta, distilled)
    (base / "public_skill/SKILL.md").write_text(skill, encoding="utf-8")

    review = review_public_skill(skill)
    snapshot = snapshot_version(base, "v1")

    assert review["passed"] is True
    assert (snapshot / "public_skill/SKILL.md").exists()
```

- [ ] **Step 2: Run full test suite**

Run: `python -m pytest -q`

Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/test_smoke_flow.py
git commit -m "test: add minimal person flow"
```

## Self-Review Checklist

- Spec coverage: product flow, architecture, evidence, adaptive interview, profiles, quality review, storage, and roadmap are covered.
- Placeholder scan: no implementation task uses unresolved placeholder markers or undefined future behavior.
- Type consistency: profile types are `colleague`, `relationship`, `mentor`, `self` across schemas, presets, and tests.
- Safety coverage: generated public skill is reviewed for impersonation, missing disclaimer, missing honest boundary, and private raw material.
