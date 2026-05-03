# human2skill Review Gate Fixes Design Spec

## Summary

This spec covers the three blocking review findings found on branch `feature/human2skill-p0-p2`.

The affected area is the P2 release gate:

- `structured_review()` currently marks some low-quality skills as passing because it only enforces privacy and honest-boundary scores.
- `export_skill()` currently checks whichever review JSON sorts last instead of the review for the requested variant.
- `build_from_distillation()` currently treats accepted conflict resolutions as unresolved because it blocks every conflict whose resolution is not literal `resolved`, even though `resolved` is not an allowed evidence schema value.

The fix must make review, export, and conflict semantics match the approved P0-P2 spec before the branch is mergeable.

## Goals

- Enforce all required review score thresholds.
- Make export approval variant-specific.
- Treat only blocking conflicts as export/review blockers.
- Preserve existing CLI behavior and public module names.
- Add regression tests that fail on the current implementation and pass after the fix.
- Keep the patch scoped to release-gate correctness.

## Non-Goals

- Do not redesign the reviewer scoring heuristics beyond threshold enforcement.
- Do not add new review dimensions.
- Do not change schemas unless a test proves a schema mismatch.
- Do not implement P3 features.
- Do not change example content except if needed to satisfy corrected gates.

## Current Behavior

### Review Pass

`src/human2skill/reviewer.py` computes scores for:

- `evidence_consistency`
- `confidence_calibration`
- `honest_boundary`
- `privacy_safety`
- `expression_similarity`
- `thinking_utility`
- `profile_fit`

But `passed` only checks:

- no hard failures
- `honest_boundary == 5`
- `privacy_safety == 5`

This contradicts the approved spec, where the pass thresholds are:

- `evidence_consistency >= 4`
- `confidence_calibration >= 4`
- `honest_boundary == 5`
- `privacy_safety == 5`
- `expression_similarity >= 4`
- `thinking_utility >= 4`
- `profile_fit >= 4`

### Export Gate

`src/human2skill/exporter.py` uses `latest_review_passed(base)`, which sorts all review JSON files and reads the last file. This is not tied to the requested `variant`.

When both `advisor.json` and `first_person.json` exist:

- exporting `first_person` may pass because `review-v1.json` or another variant passed.
- exporting `advisor` may fail because an unrelated variant failed.

Export must validate the review report matching the requested variant.

### Conflict Gate

`src/human2skill/flow.py` builds `unresolved_conflicts` with:

```python
c for c in pack.get("conflicts", []) if c.get("resolution") != "resolved"
```

But `schemas/evidence_pack.schema.json` allows only:

- `halt_for_review`
- `keep_both_with_scope`
- `mark_low_confidence`

The approved spec says only blocking conflicts should stop review/export. Accepted conflicts may remain visible with scope or low confidence.

## Required Behavior

### Review Thresholds

`structured_review()` must pass only when:

- there are no hard failures.
- every threshold below is satisfied:

```python
REVIEW_PASS_THRESHOLDS = {
    "evidence_consistency": 4,
    "confidence_calibration": 5,
    "honest_boundary": 5,
    "privacy_safety": 5,
    "expression_similarity": 4,
    "thinking_utility": 4,
    "profile_fit": 4,
}
```

If a score misses its threshold:

- `passed` must be false.
- `required_changes` must include a concrete change for that score dimension.
- `notes` should identify weak dimensions.

Hard failure behavior remains unchanged.

### Variant-Specific Export

`export_skill(base, host, variant)` must check the review for that exact variant.

Review lookup order:

1. `private_evidence/reviews/{variant}.json`
2. If the requested variant is `advisor`, allow fallback to `review-v1.json` only when `review-v1.json` has `"variant": "advisor"` or has no `variant` field for backward compatibility.
3. No fallback for `first_person`.

Export must fail if:

- variant skill file is missing.
- variant review is missing.
- variant review did not pass.
- review report variant mismatches the requested variant.
- privacy check fails.

Export manifest must continue to report:

- `review_passed`
- `privacy_check_passed`

### Conflict Resolution Semantics

The system must classify blocking conflicts explicitly.

Blocking:

- `halt_for_review`

Accepted:

- `keep_both_with_scope`
- `mark_low_confidence`

`build_from_distillation()` must pass only blocking conflicts to `structured_review()` as unresolved conflicts.

Accepted conflicts must remain in `evidence_pack.json`; they are not deleted or hidden. They simply do not create a hard review failure.

`detect_update_conflicts()` already treats `halt_for_review` as blocking and should remain consistent with this behavior.

## Files To Change

- `src/human2skill/reviewer.py`
- `src/human2skill/exporter.py`
- `src/human2skill/flow.py`
- `tests/test_reviewer.py`
- `tests/test_exporter.py`
- `tests/test_flow.py` or `tests/test_update_flow.py`

No schema changes are expected.

## Test Requirements

### Reviewer Tests

Add tests that prove:

- a skill with no hard failures but `expression_similarity < 4` fails.
- a skill with no hard failures but `thinking_utility < 4` fails.
- a skill that meets all thresholds passes.

The failing-content fixture should include:

- disclaimer
- three honest-boundary bullets
- no private markers
- enough sections to pass privacy and boundary checks
- missing or empty expression/thinking/profile content to trigger threshold failure

### Exporter Tests

Add tests that prove:

- exporting `first_person` fails when `first_person.json` is missing even if `advisor.json` passed.
- exporting `first_person` fails when `first_person.json` exists but `passed` is false.
- exporting `advisor` uses `advisor.json` and is not blocked by a failed `first_person.json`.
- exporting fails when the review file variant mismatches the requested variant.

### Flow Conflict Tests

Add tests that prove:

- `keep_both_with_scope` does not produce a review hard failure.
- `mark_low_confidence` does not produce a review hard failure.
- `halt_for_review` still produces `unresolved_conflicts` and fails review.

## Acceptance Criteria

- `structured_review()` enforces all required score thresholds.
- `export_skill()` enforces the review report for the requested variant.
- accepted conflict resolutions do not fail review.
- blocking conflicts still fail review.
- all new regression tests fail before the fix and pass after the fix.
- full test suite passes:

```bash
.venv/bin/python -m pytest -q
```

## Merge Standard

After these fixes, the branch may be considered for merge if:

- all tests pass.
- no new broad refactor was introduced.
- example fixtures still pass review/export.
- no real home directory writes are added.
- no P3 work is introduced.
