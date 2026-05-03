# human2skill Review Gate Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the three merge-blocking review-gate issues on `feature/human2skill-p0-p2`: full review threshold enforcement, variant-specific export approval, and correct conflict blocking semantics.

**Architecture:** Keep the existing P0-P2 architecture intact. Make focused changes in `reviewer.py`, `exporter.py`, and `flow.py`, with regression tests proving each review finding is closed. Do not change schemas unless the existing schema blocks the specified behavior.

**Tech Stack:** Python 3.11+, pytest, existing `human2skill` package modules, local filesystem test fixtures.

---

## Implementation Notes

- Work in the feature worktree:

```bash
cd "/Users/eric/Documents/Vibe Coding/human2skill/.worktrees/feature/human2skill-p0-p2"
```

- Do not touch unrelated docs, examples, schemas, or generated artifacts unless a test requires it.
- Run the focused test after each task.
- Run full pytest after all fixes.
- Each task should be committed separately if executing in a development branch.

## File Structure

Modify:

- `src/human2skill/reviewer.py`: centralize pass thresholds and apply them to `passed`.
- `src/human2skill/exporter.py`: replace latest-review lookup with requested-variant review lookup.
- `src/human2skill/flow.py`: pass only blocking conflicts to `structured_review()`.
- `tests/test_reviewer.py`: threshold regression tests.
- `tests/test_exporter.py`: variant-specific export regression tests.
- `tests/test_flow.py`: conflict resolution regression tests.

No new production files are expected.

---

## Task 1: Enforce All Review Score Thresholds

**Files:**
- Modify: `src/human2skill/reviewer.py`
- Modify: `tests/test_reviewer.py`

- [ ] **Step 1: Add failing regression tests**

Append these tests to `tests/test_reviewer.py`:

```python
from human2skill.reviewer import structured_review


def review_content_without_expression_or_models() -> str:
    return "\n".join([
        "不代表本人观点",
        "不声称自己就是 李明 本人",
        "## 诚实边界",
        "- 关系场景证据不足。",
        "- 投资建议证据不足。",
        "- 医疗法律问题不适用。",
    ])


def review_content_meeting_all_thresholds() -> str:
    return "\n".join([
        "不代表本人观点",
        "不声称自己就是 李明 本人",
        "## 核心思维模型",
        "- 先确认影响范围，再讨论方案。",
        "## 表达 DNA",
        "- 短句，结论先行。",
        "## Profile 专项层",
        "- 适合工作评审和协作场景。",
        "## 诚实边界",
        "- 关系场景证据不足。",
        "- 投资建议证据不足。",
        "- 医疗法律问题不适用。",
    ])


def test_structured_review_fails_when_expression_score_below_threshold():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=review_content_without_expression_or_models(),
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert report["passed"] is False
    assert report["scores"]["expression_similarity"] < 4
    assert any("expression" in change.lower() or "表达" in change for change in report["required_changes"])


def test_structured_review_fails_when_thinking_score_below_threshold():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=review_content_without_expression_or_models(),
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert report["passed"] is False
    assert report["scores"]["thinking_utility"] < 4
    assert any("thinking" in change.lower() or "思维" in change for change in report["required_changes"])


def test_structured_review_passes_only_when_all_thresholds_met():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=review_content_meeting_all_thresholds(),
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert report["passed"] is True
    assert report["scores"]["evidence_consistency"] >= 4
    assert report["scores"]["confidence_calibration"] >= 4
    assert report["scores"]["honest_boundary"] == 5
    assert report["scores"]["privacy_safety"] == 5
    assert report["scores"]["expression_similarity"] >= 4
    assert report["scores"]["thinking_utility"] >= 4
    assert report["scores"]["profile_fit"] >= 4
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_reviewer.py -q
```

Expected before implementation: at least one new threshold test fails because `passed` ignores `expression_similarity`, `thinking_utility`, or `profile_fit`.

- [ ] **Step 3: Add threshold constants**

In `src/human2skill/reviewer.py`, near the top after `PRIVATE_MARKERS`, add:

```python
REVIEW_PASS_THRESHOLDS = {
    "evidence_consistency": 4,
    "confidence_calibration": 4,
    "honest_boundary": 5,
    "privacy_safety": 5,
    "expression_similarity": 4,
    "thinking_utility": 4,
    "profile_fit": 4,
}
```

- [ ] **Step 4: Make required changes include every threshold miss**

Update `_derive_required_changes()` so it adds a change whenever `score < REVIEW_PASS_THRESHOLDS[dimension]`, not only when `score < 3`.

Use this implementation:

```python
    for dimension, score in scores.items():
        threshold = REVIEW_PASS_THRESHOLDS.get(dimension)
        if threshold is not None and score < threshold and dimension in score_to_change:
            changes.append(score_to_change[dimension])
```

- [ ] **Step 5: Make notes identify every threshold miss**

Update `_derive_notes()` so weak dimensions are threshold misses:

```python
    weak = [
        dim
        for dim, score in scores.items()
        if score < REVIEW_PASS_THRESHOLDS.get(dim, 1)
    ]
```

- [ ] **Step 6: Enforce thresholds in `structured_review()`**

Replace the `passed = ...` block with:

```python
    threshold_failures = [
        dimension
        for dimension, threshold in REVIEW_PASS_THRESHOLDS.items()
        if scores[dimension] < threshold
    ]

    passed = not hard_failures and not threshold_failures
```

Do not add threshold misses to `hard_failures`; they are quality failures, not hard safety failures.

- [ ] **Step 7: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_reviewer.py -q
```

Expected: all reviewer tests pass.

- [ ] **Step 8: Commit**

```bash
git add src/human2skill/reviewer.py tests/test_reviewer.py
git commit -m "fix: enforce structured review score thresholds"
```

---

## Task 2: Make Export Approval Variant-Specific

**Files:**
- Modify: `src/human2skill/exporter.py`
- Modify: `tests/test_exporter.py`

- [ ] **Step 1: Add failing exporter regression tests**

Append these tests to `tests/test_exporter.py`:

```python
import json
from pathlib import Path

from human2skill.exporter import export_skill
from human2skill.storage import initialize_person_dir, write_json


def write_variant(base: Path, variant: str, content: str = "# skill") -> None:
    path = base / "public_skill" / "variants" / variant
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(content, encoding="utf-8")


def write_review(base: Path, filename: str, *, variant: str, passed: bool) -> None:
    write_json(
        base / "private_evidence" / "reviews" / filename,
        {
            "schema_version": "1",
            "person_slug": base.name,
            "variant": variant,
            "generated_at": "2026-04-30T00:00:00+00:00",
            "passed": passed,
            "hard_failures": [],
            "scores": {
                "evidence_consistency": 4,
                "confidence_calibration": 4,
                "honest_boundary": 5,
                "privacy_safety": 5,
                "expression_similarity": 4,
                "thinking_utility": 4,
                "profile_fit": 4,
            },
            "required_changes": [],
            "notes": [],
        },
    )


def test_export_first_person_requires_first_person_review(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_variant(base, "first_person")
    write_review(base, "advisor.json", variant="advisor", passed=True)

    try:
        export_skill(base, host="codex", variant="first_person")
    except ValueError as error:
        assert "first_person" in str(error)
    else:
        raise AssertionError("first_person export passed without first_person review")


def test_export_first_person_rejects_failed_first_person_review(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_variant(base, "first_person")
    write_review(base, "first_person.json", variant="first_person", passed=False)

    try:
        export_skill(base, host="codex", variant="first_person")
    except ValueError as error:
        assert "did not pass" in str(error)
    else:
        raise AssertionError("failed first_person review allowed export")


def test_export_advisor_ignores_failed_first_person_review(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_variant(base, "advisor")
    write_review(base, "advisor.json", variant="advisor", passed=True)
    write_review(base, "first_person.json", variant="first_person", passed=False)

    export_dir = export_skill(
        base,
        host="codex",
        variant="advisor",
        created_at="2026-04-30T00:00:00+00:00",
    )

    manifest = json.loads((export_dir / "export_manifest.json").read_text(encoding="utf-8"))
    assert manifest["variant"] == "advisor"
    assert manifest["review_passed"] is True


def test_export_rejects_review_variant_mismatch(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_variant(base, "advisor")
    write_review(base, "advisor.json", variant="first_person", passed=True)

    try:
        export_skill(base, host="codex", variant="advisor")
    except ValueError as error:
        assert "variant" in str(error)
    else:
        raise AssertionError("mismatched review variant allowed export")
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_exporter.py -q
```

Expected before implementation: variant-specific tests fail because export reads the latest review instead of the requested variant review.

- [ ] **Step 3: Replace latest review helper**

In `src/human2skill/exporter.py`, replace `latest_review_passed()` with:

```python
def review_path_for_variant(base: Path, variant: str) -> Path | None:
    reviews_dir = base / "private_evidence" / "reviews"
    direct = reviews_dir / f"{variant}.json"
    if direct.exists():
        return direct

    legacy = reviews_dir / "review-v1.json"
    if variant == "advisor" and legacy.exists():
        return legacy

    return None


def load_review_for_variant(base: Path, variant: str) -> dict:
    path = review_path_for_variant(base, variant)
    if path is None:
        raise ValueError(f"Cannot export {variant}: review report is missing.")

    report = json.loads(path.read_text(encoding="utf-8"))
    report_variant = report.get("variant")
    if report_variant is not None and report_variant != variant:
        raise ValueError(
            f"Cannot export {variant}: review report variant mismatch: {report_variant}"
        )
    return report


def review_passed_for_variant(base: Path, variant: str) -> bool:
    return bool(load_review_for_variant(base, variant).get("passed", False))
```

- [ ] **Step 4: Update `export_skill()` gate**

In `export_skill()`, replace:

```python
    if not latest_review_passed(base):
        raise ValueError("Cannot export: latest review is missing or did not pass.")
```

with:

```python
    review = load_review_for_variant(base, variant)
    if not review.get("passed", False):
        raise ValueError(f"Cannot export {variant}: review did not pass.")
```

- [ ] **Step 5: Update manifest review result**

Replace:

```python
        "review_passed": latest_review_passed(base),
```

with:

```python
        "review_passed": bool(review.get("passed", False)),
```

- [ ] **Step 6: Make privacy failure block export**

After copying the skill and before writing the manifest, compute privacy:

```python
    privacy_passed = _privacy_check_passed(dest_skill)
    if not privacy_passed:
        raise ValueError(f"Cannot export {variant}: privacy check failed.")
```

Then set:

```python
        "privacy_check_passed": privacy_passed,
```

- [ ] **Step 7: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_exporter.py -q
```

Expected: all exporter tests pass.

- [ ] **Step 8: Commit**

```bash
git add src/human2skill/exporter.py tests/test_exporter.py
git commit -m "fix: enforce variant-specific export reviews"
```

---

## Task 3: Block Only Halt-for-Review Conflicts

**Files:**
- Modify: `src/human2skill/flow.py`
- Modify: `tests/test_flow.py`

- [ ] **Step 1: Add failing conflict regression tests**

Append these helpers and tests to `tests/test_flow.py`:

```python
import json
from pathlib import Path

from human2skill.evidence_builder import add_claim, add_conflict, add_evidence, empty_evidence_pack
from human2skill.flow import build_from_distillation, create_project_person


def build_base_with_conflict(tmp_path: Path, resolution: str) -> tuple[Path, dict]:
    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-30T00:00:00+00:00",
    )
    pack = empty_evidence_pack("li-ming")
    ev1 = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="工作场景直接指出问题。",
        retention="summary_only",
        confidence="high",
        supports=[],
    )
    ev2 = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="关系场景会放缓语气。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    claim1 = add_claim(
        pack,
        claim="工作场景直接指出问题。",
        claim_type="pressure_response",
        confidence="medium",
        evidence_ids=[ev1["evidence_id"]],
    )
    claim2 = add_claim(
        pack,
        claim="关系场景会放缓语气。",
        claim_type="pressure_response",
        confidence="medium",
        evidence_ids=[ev2["evidence_id"]],
    )
    add_conflict(
        pack,
        claim_ids=[claim1["claim_id"], claim2["claim_id"]],
        evidence_ids=[ev1["evidence_id"], ev2["evidence_id"]],
        conflict_type="contextual",
        resolution=resolution,
        note="不同场景保留不同规则。",
    )
    (base / "private_evidence/evidence_pack.json").write_text(
        json.dumps(pack, ensure_ascii=False),
        encoding="utf-8",
    )
    return base, claim1


def conflict_distillation(claim_id: str) -> dict:
    return {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-30T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [],
        "decision_heuristics": [],
        "expression_dna": [{
            "title": "直接但会分场景",
            "content": "工作场景直接，关系场景放缓。",
            "claim_ids": [claim_id],
            "confidence": "medium",
            "evidence_summary": "冲突按场景保留。",
            "limits": ["只覆盖已观察场景。"],
        }],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [
            {
                "title": "关系边界",
                "content": "亲密关系细节证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "仅有观察者描述。",
                "limits": ["不推断深层动机。"],
            },
            {
                "title": "时间边界",
                "content": "只覆盖当前阶段。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "没有长期材料。",
                "limits": ["不推断长期变化。"],
            },
            {
                "title": "领域边界",
                "content": "非工作领域证据较弱。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "工作材料更多。",
                "limits": ["不泛化到所有关系。"],
            },
        ],
        "scenario_tests": [],
    }


def test_build_allows_keep_both_with_scope_conflict(tmp_path: Path):
    base, claim = build_base_with_conflict(tmp_path, "keep_both_with_scope")

    result = build_from_distillation(
        base,
        conflict_distillation(claim["claim_id"]),
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert "unresolved_conflicts" not in result["review"]["hard_failures"]


def test_build_allows_mark_low_confidence_conflict(tmp_path: Path):
    base, claim = build_base_with_conflict(tmp_path, "mark_low_confidence")

    result = build_from_distillation(
        base,
        conflict_distillation(claim["claim_id"]),
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert "unresolved_conflicts" not in result["review"]["hard_failures"]


def test_build_blocks_halt_for_review_conflict(tmp_path: Path):
    base, claim = build_base_with_conflict(tmp_path, "halt_for_review")

    result = build_from_distillation(
        base,
        conflict_distillation(claim["claim_id"]),
        generated_at="2026-04-30T00:00:00+00:00",
    )

    assert "unresolved_conflicts" in result["review"]["hard_failures"]
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_flow.py -q
```

Expected before implementation: the accepted-conflict tests fail because all schema-allowed conflict resolutions are treated as unresolved.

- [ ] **Step 3: Add blocking conflict helper**

In `src/human2skill/flow.py`, add:

```python
BLOCKING_CONFLICT_RESOLUTIONS = {"halt_for_review"}


def blocking_conflicts(pack: dict) -> list[dict]:
    return [
        conflict
        for conflict in pack.get("conflicts", [])
        if conflict.get("resolution") in BLOCKING_CONFLICT_RESOLUTIONS
    ]
```

- [ ] **Step 4: Use helper in build flow**

Replace:

```python
    unresolved_conflicts = [
        c for c in pack.get("conflicts", [])
        if c.get("resolution") != "resolved"
    ]
```

with:

```python
    unresolved_conflicts = blocking_conflicts(pack)
```

- [ ] **Step 5: Align update conflict helper**

Update `detect_update_conflicts()` to use `blocking_conflicts(pack)`:

```python
    blocking = blocking_conflicts(pack)
```

This preserves current behavior and keeps update/build semantics in one place.

- [ ] **Step 6: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_flow.py tests/test_update_flow.py -q
```

Expected: all selected tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/human2skill/flow.py tests/test_flow.py
git commit -m "fix: only block halt-for-review conflicts"
```

---

## Task 4: Full Verification

**Files:**
- No new files expected.

- [ ] **Step 1: Run full test suite**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run targeted smoke commands**

Run:

```bash
.venv/bin/python -m pytest tests/test_reviewer.py tests/test_exporter.py tests/test_flow.py tests/test_update_flow.py -q
```

Expected: all selected tests pass.

- [ ] **Step 3: Check git diff**

Run:

```bash
git diff --stat main..HEAD
git status --short
```

Expected:

- worktree clean after commits.
- diff includes only intended fixes and tests on top of existing feature branch work.

- [ ] **Step 4: Re-review merge criteria**

Confirm:

- review pass requires all thresholds.
- export checks the requested variant review.
- accepted conflict resolutions do not fail review.
- `halt_for_review` still fails review.
- no P3 scope added.
- no real home-directory writes added.

If all are true, the branch is ready for another merge-standard review.

## Self-Review Checklist

- Finding 1 is covered by Task 1.
- Finding 2 is covered by Task 2.
- Finding 3 is covered by Task 3.
- No schemas are changed.
- No generated examples are changed unless tests force it.
- All regression tests are explicit and tied to a review finding.
