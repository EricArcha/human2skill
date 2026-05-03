# human2skill P0-P2 Complete Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the P0-P2 human2skill system: a hybrid Meta-skill + Python CLI workflow that creates, ingests, interviews, evidences, distills, reviews, exports, installs, updates, and versions private/person perspective skills.

**Architecture:** Keep high-judgment synthesis agent-assisted and make Python own durable state, validation, rendering, review, export, install, and versioning. Extend the current small core modules into focused units with schema-backed contracts and CLI integration. Public skills stay separate from private evidence; raw private material never enters public output.

**Tech Stack:** Python 3.11+, standard library, `jsonschema`, lightweight `pypdf` for PDF text extraction, pytest, local filesystem storage, Markdown Skill templates.

---

## Implementation Notes

- Work from the approved spec: `docs/superpowers/specs/2026-04-29-human2skill-p0-p2-complete-design.md`.
- Keep existing public APIs working unless a task explicitly replaces them.
- Use TDD per task: write failing tests first, then implementation, then full or targeted pytest.
- Do not write to real home directories in tests. All install/export tests must use `tmp_path`.
- Keep raw source material out of public skill fixtures.
- Commit after each task if executing this plan in a development branch.

## File Structure

Create or modify these focused units:

- `schemas/source_index.schema.json`: source index contract.
- `schemas/distillation.schema.json`: agent-assisted distillation contract.
- `schemas/review_report.schema.json`: structured review contract.
- `schemas/export_manifest.schema.json`: export manifest contract.
- `src/human2skill/constants.py`: shared enums and section names.
- `src/human2skill/timeutils.py`: deterministic timestamp helper with injectable clock.
- `src/human2skill/schemas.py`: schema loading and validation helpers.
- `src/human2skill/intake.py`: metadata initialization and profile defaults.
- `src/human2skill/ingest.py`: manual/text/markdown/pdf ingestion into source index records.
- `src/human2skill/evidence_builder.py`: evidence, claim, and conflict construction.
- `src/human2skill/distillation.py`: distillation validation and section mapping.
- `src/human2skill/reviewer.py`: upgrade existing review to structured review while preserving `review_public_skill`.
- `src/human2skill/scenario.py`: scenario replay report structure and validation.
- `src/human2skill/exporter.py`: host export packages and manifests.
- `src/human2skill/installer.py`: explicit install into caller-provided targets.
- `src/human2skill/flow.py`: orchestration helpers for create/build/update/export.
- `src/human2skill/cli.py`: argparse CLI entrypoint.
- `templates/skill/advisor.md`: advisor-mode public skill template.
- `templates/skill/first-person.md`: limited first-person public skill template.
- `human2skill-meta/SKILL.md`: conversational Meta-skill entry.
- `examples/`: three fictional person fixtures.

Modify:

- `pyproject.toml`: add `pypdf` and console script.
- `schemas/person.meta.schema.json`: add voice/export fields.
- `schemas/evidence_pack.schema.json`: add claim types and conflict records.
- `templates/profiles/*.json`: include value order and anti-pattern sections.
- `src/human2skill/storage.py`: support source, distillation, review, changelog, export, and rollback snapshots.
- `src/human2skill/interview.py`: add value/anti-pattern dimensions and perspective-specific questions.
- `src/human2skill/generator.py`: render advisor and first-person variants.
- `tests/`: add tests per task below.

---

## Task 1: Shared Constants, Schema Validation, and Dependency Setup

**Files:**
- Create: `src/human2skill/constants.py`
- Create: `src/human2skill/timeutils.py`
- Create: `src/human2skill/schemas.py`
- Modify: `pyproject.toml`
- Test: `tests/test_schema_helpers.py`

- [ ] **Step 1: Write failing tests for schema helper behavior**

Create `tests/test_schema_helpers.py` with tests that load an existing schema and reject an invalid document.

Required tests:

```python
import pytest

from human2skill.schemas import SchemaValidationError, load_schema, validate_document


def test_load_schema_reads_existing_schema():
    schema = load_schema("person.meta.schema.json")

    assert schema["type"] == "object"
    assert "properties" in schema


def test_validate_document_raises_readable_error():
    with pytest.raises(SchemaValidationError) as error:
        validate_document("person.meta.schema.json", {"schema_version": "1"})

    assert "person.meta.schema.json" in str(error.value)
    assert "required" in str(error.value)
```

- [ ] **Step 2: Run the focused test and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_schema_helpers.py -q
```

Expected: fails because `human2skill.schemas` does not exist.

- [ ] **Step 3: Implement shared constants**

Create `src/human2skill/constants.py` with:

```python
PROFILE_TYPES = ("colleague", "relationship", "mentor", "self")
VOICE_MODES = ("advisor", "first_person", "both")
RETENTION_POLICIES = ("no_raw_retention", "summary_only", "local_private_raw")
HOSTS = ("codex", "claude-code", "openclaw", "hermes")

SOURCE_KINDS = (
    "manual_text",
    "markdown",
    "txt",
    "pdf_text",
    "chat_excerpt",
    "meeting_note",
    "email_summary",
    "interview_answer",
    "screenshot_text",
)

CLAIM_TYPES = (
    "mental_model",
    "decision_heuristic",
    "expression_dna",
    "profile_specific",
    "pressure_response",
    "value_order",
    "anti_pattern",
    "boundary",
)

CONFLICT_TYPES = (
    "temporal",
    "contextual",
    "observer_conflict",
    "inherent_tension",
)

REVIEW_SCORE_KEYS = (
    "evidence_consistency",
    "confidence_calibration",
    "honest_boundary",
    "privacy_safety",
    "expression_similarity",
    "thinking_utility",
    "profile_fit",
)
```

- [ ] **Step 4: Implement deterministic timestamp helper**

Create `src/human2skill/timeutils.py` with:

```python
from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
```

- [ ] **Step 5: Implement schema helper**

Create `src/human2skill/schemas.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, exceptions


class SchemaValidationError(ValueError):
    pass


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def schema_dir() -> Path:
    return project_root() / "schemas"


def load_schema(name: str) -> dict:
    path = schema_dir() / name
    return json.loads(path.read_text(encoding="utf-8"))


def validate_document(schema_name: str, document: dict) -> None:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        path = ".".join(str(part) for part in first.path) or "<root>"
        raise SchemaValidationError(f"{schema_name} validation failed at {path}: {first.message}")
```

- [ ] **Step 6: Add lightweight PDF dependency and CLI script entry declaration**

Modify `pyproject.toml`:

```toml
dependencies = [
  "jsonschema>=4.22.0",
  "pypdf>=4.0.0"
]

[project.scripts]
human2skill = "human2skill.cli:main"
```

Do not create `cli.py` in this task; tests that use the console script come later.

- [ ] **Step 7: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_schema_helpers.py tests/test_import.py -q
```

Expected: all selected tests pass.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml src/human2skill/constants.py src/human2skill/timeutils.py src/human2skill/schemas.py tests/test_schema_helpers.py
git commit -m "chore: add schema helpers and shared constants"
```

---

## Task 2: Expand JSON Schemas

**Files:**
- Modify: `schemas/person.meta.schema.json`
- Modify: `schemas/evidence_pack.schema.json`
- Create: `schemas/source_index.schema.json`
- Create: `schemas/distillation.schema.json`
- Create: `schemas/review_report.schema.json`
- Create: `schemas/export_manifest.schema.json`
- Test: `tests/test_expanded_schemas.py`

- [ ] **Step 1: Write failing tests for new schemas**

Create `tests/test_expanded_schemas.py` with minimal valid documents for all schemas and negative cases for privacy and voice mode.

Required tests:

```python
from human2skill.schemas import validate_document
import pytest


def test_person_meta_accepts_voice_and_export_policy():
    validate_document("person.meta.schema.json", {
        "schema_version": "1",
        "slug": "li-ming",
        "display_name": "李明",
        "profile_type": "colleague",
        "relationship_to_user": "coworker",
        "use_case": "work review perspective",
        "voice_mode": "both",
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local private use"
        },
        "privacy_policy": {
            "raw_retention": "summary_only",
            "public_skill_allows_private_quotes": False
        },
        "export_policy": {
            "default_visibility": "private",
            "shareable_variants": ["advisor"],
            "requires_privacy_review": True
        },
        "lifecycle": {
            "version": "v1",
            "created_at": "2026-04-29T00:00:00+00:00",
            "updated_at": "2026-04-29T00:00:00+00:00"
        }
    })


def test_person_meta_rejects_public_private_quotes():
    document = {
        "schema_version": "1",
        "slug": "li-ming",
        "display_name": "李明",
        "profile_type": "colleague",
        "voice_mode": "advisor",
        "privacy_policy": {
            "raw_retention": "summary_only",
            "public_skill_allows_private_quotes": True
        },
        "export_policy": {
            "default_visibility": "private",
            "shareable_variants": ["advisor"],
            "requires_privacy_review": True
        },
        "lifecycle": {
            "version": "v1",
            "created_at": "2026-04-29T00:00:00+00:00",
            "updated_at": "2026-04-29T00:00:00+00:00"
        }
    }
    with pytest.raises(Exception):
        validate_document("person.meta.schema.json", document)


def test_source_index_accepts_summary_only_source():
    validate_document("source_index.schema.json", {
        "schema_version": "1",
        "person_slug": "li-ming",
        "sources": [{
            "source_id": "src-0001",
            "source_kind": "manual_text",
            "title": "手动摘要",
            "provided_by": "user",
            "retention": "summary_only",
            "contains_private_data": True,
            "allowed_in_public_skill": False,
            "summary": "用户提供了工作评审片段摘要。",
            "created_at": "2026-04-29T00:00:00+00:00"
        }]
    })


def test_distillation_requires_claim_links_for_model():
    validate_document("distillation.schema.json", {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [{
            "title": "Impact first",
            "content": "先问 impact，再讨论方案。",
            "claim_ids": ["claim-impact-first"],
            "confidence": "medium",
            "evidence_summary": "由会议摘要支持。",
            "limits": ["只覆盖工作评审场景。"]
        }],
        "decision_heuristics": [],
        "expression_dna": [],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [],
        "scenario_tests": []
    })


def test_review_report_accepts_structured_scores():
    validate_document("review_report.schema.json", {
        "schema_version": "1",
        "person_slug": "li-ming",
        "variant": "advisor",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "passed": True,
        "hard_failures": [],
        "scores": {
            "evidence_consistency": 4,
            "confidence_calibration": 4,
            "honest_boundary": 5,
            "privacy_safety": 5,
            "expression_similarity": 4,
            "thinking_utility": 4,
            "profile_fit": 4
        },
        "required_changes": [],
        "notes": []
    })


def test_export_manifest_accepts_codex_manifest():
    validate_document("export_manifest.schema.json", {
        "schema_version": "1",
        "host": "codex",
        "person_slug": "li-ming",
        "variant": "advisor",
        "created_at": "2026-04-29T00:00:00+00:00",
        "files": ["SKILL.md"],
        "install_hint": "~/.codex/skills/li-ming",
        "review_passed": True,
        "privacy_check_passed": True
    })
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_expanded_schemas.py -q
```

Expected: fails because new schemas and person fields are not present.

- [ ] **Step 3: Modify person schema**

Update `schemas/person.meta.schema.json`:

- Require `voice_mode` and `export_policy`.
- Keep existing required fields.
- Add `voice_mode` enum: `advisor`, `first_person`, `both`.
- Add `export_policy` with `default_visibility`, `shareable_variants`, `requires_privacy_review`.
- Keep `public_skill_allows_private_quotes` as `const: false`.

- [ ] **Step 4: Modify evidence schema**

Update `schemas/evidence_pack.schema.json`:

- Add claim types: `pressure_response`, `value_order`, `anti_pattern`.
- Add optional top-level `conflicts` array.
- Conflict item fields:
  - `conflict_id` pattern `^cf-[0-9]{4}$`
  - `claim_ids`
  - `evidence_ids`
  - `conflict_type`
  - `resolution`
  - `note`

- [ ] **Step 5: Create source index schema**

Create `schemas/source_index.schema.json` using the source fields from the spec. Make `allowed_in_public_skill` required and boolean.

- [ ] **Step 6: Create distillation schema**

Create `schemas/distillation.schema.json` with shared item shape:

- `title`
- `content`
- `claim_ids`
- `confidence`
- `evidence_summary`
- `limits`

Use this shape for all distilled sections except scenario tests.

- [ ] **Step 7: Create review report schema**

Create `schemas/review_report.schema.json` with required scores from `REVIEW_SCORE_KEYS`.

- [ ] **Step 8: Create export manifest schema**

Create `schemas/export_manifest.schema.json` with host enum and manifest fields from the spec.

- [ ] **Step 9: Run schema tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_schemas.py tests/test_expanded_schemas.py -q
```

Expected: all schema tests pass.

- [ ] **Step 10: Commit**

```bash
git add schemas tests/test_expanded_schemas.py
git commit -m "feat: expand schemas for p0 p2 flow"
```

---

## Task 3: Intake Router and Storage Layout

**Files:**
- Create: `src/human2skill/intake.py`
- Modify: `src/human2skill/storage.py`
- Test: `tests/test_intake.py`
- Test: `tests/test_storage.py`

- [ ] **Step 1: Write failing intake tests**

Create `tests/test_intake.py`:

```python
import json
from pathlib import Path

from human2skill.intake import create_person


def test_create_person_writes_meta_with_defaults(tmp_path: Path):
    base = create_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review perspective",
        voice_mode="both",
        now="2026-04-29T00:00:00+00:00",
    )

    meta = json.loads((base / "person.meta.json").read_text(encoding="utf-8"))

    assert meta["slug"] == "li-ming"
    assert meta["voice_mode"] == "both"
    assert meta["privacy_policy"]["raw_retention"] == "summary_only"
    assert meta["privacy_policy"]["public_skill_allows_private_quotes"] is False
    assert meta["export_policy"]["shareable_variants"] == ["advisor"]


def test_create_person_creates_full_layout(tmp_path: Path):
    base = create_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review perspective",
        now="2026-04-29T00:00:00+00:00",
    )

    assert (base / "public_skill/variants/advisor").is_dir()
    assert (base / "public_skill/variants/first_person").is_dir()
    assert (base / "private_evidence/interviews").is_dir()
    assert (base / "private_evidence/reviews").is_dir()
    assert (base / "private_evidence/changelog").is_dir()
    assert (base / "exports/codex").is_dir()
    assert (base / "versions").is_dir()
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_intake.py -q
```

Expected: fails because `human2skill.intake` does not exist.

- [ ] **Step 3: Extend storage layout**

Modify `initialize_person_dir()` in `src/human2skill/storage.py` to create:

```text
public_skill/variants/advisor
public_skill/variants/first_person
private_evidence/interviews
private_evidence/reviews
private_evidence/changelog
exports/codex
exports/claude-code
exports/openclaw
exports/hermes
versions
```

Keep old directories working.

- [ ] **Step 4: Implement intake**

Create `src/human2skill/intake.py`:

```python
from __future__ import annotations

from pathlib import Path

from human2skill.constants import PROFILE_TYPES, VOICE_MODES
from human2skill.schemas import validate_document
from human2skill.storage import initialize_person_dir, write_json
from human2skill.timeutils import utc_now_iso


def normalize_profile(profile_type: str | None) -> str:
    if profile_type in PROFILE_TYPES:
        return profile_type
    return "relationship"


def normalize_voice_mode(voice_mode: str | None) -> str:
    if voice_mode in VOICE_MODES:
        return voice_mode
    return "advisor"


def build_person_meta(
    *,
    slug: str,
    display_name: str,
    profile_type: str | None,
    relationship_to_user: str,
    use_case: str,
    voice_mode: str | None = None,
    now: str | None = None,
) -> dict:
    timestamp = now or utc_now_iso()
    meta = {
        "schema_version": "1",
        "slug": slug,
        "display_name": display_name,
        "profile_type": normalize_profile(profile_type),
        "relationship_to_user": relationship_to_user,
        "use_case": use_case,
        "voice_mode": normalize_voice_mode(voice_mode),
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local private use unless explicitly changed",
        },
        "privacy_policy": {
            "raw_retention": "summary_only",
            "public_skill_allows_private_quotes": False,
        },
        "export_policy": {
            "default_visibility": "private",
            "shareable_variants": ["advisor"],
            "requires_privacy_review": True,
        },
        "lifecycle": {
            "version": "v1",
            "created_at": timestamp,
            "updated_at": timestamp,
        },
    }
    validate_document("person.meta.schema.json", meta)
    return meta


def create_person(
    *,
    root: Path,
    slug: str,
    display_name: str,
    profile_type: str | None,
    relationship_to_user: str,
    use_case: str,
    voice_mode: str | None = None,
    now: str | None = None,
) -> Path:
    base = initialize_person_dir(root, slug)
    meta = build_person_meta(
        slug=slug,
        display_name=display_name,
        profile_type=profile_type,
        relationship_to_user=relationship_to_user,
        use_case=use_case,
        voice_mode=voice_mode,
        now=now,
    )
    write_json(base / "person.meta.json", meta)
    return base
```

- [ ] **Step 5: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_intake.py tests/test_storage.py -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/human2skill/intake.py src/human2skill/storage.py tests/test_intake.py tests/test_storage.py
git commit -m "feat: add intake router and expanded storage layout"
```

---

## Task 4: Corpus Ingestor and Source Index

**Files:**
- Create: `src/human2skill/ingest.py`
- Test: `tests/test_ingest.py`

- [ ] **Step 1: Write failing ingestion tests**

Create `tests/test_ingest.py`:

```python
import json
from pathlib import Path

from human2skill.ingest import add_text_source, ingest_file, load_source_index
from human2skill.storage import initialize_person_dir


def test_add_text_source_creates_source_index(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")

    source = add_text_source(
        base,
        title="manual note",
        text="李明在评审时先问 impact，再看方案。",
        source_kind="manual_text",
        now="2026-04-29T00:00:00+00:00",
    )

    index = load_source_index(base)
    assert source["source_id"] == "src-0001"
    assert index["person_slug"] == "li-ming"
    assert index["sources"][0]["allowed_in_public_skill"] is False
    assert "impact" in index["sources"][0]["summary"]


def test_ingest_markdown_file_records_markdown_kind(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    file_path = tmp_path / "notes.md"
    file_path.write_text("# Notes\n\n李明喜欢先确认目标。", encoding="utf-8")

    source = ingest_file(base, file_path, now="2026-04-29T00:00:00+00:00")

    assert source["source_kind"] == "markdown"
    assert source["title"] == "notes.md"


def test_ingest_unsupported_file_type_rejects(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    file_path = tmp_path / "notes.bin"
    file_path.write_bytes(b"\x00\x01")

    try:
        ingest_file(base, file_path)
    except ValueError as error:
        assert "Unsupported file type" in str(error)
    else:
        raise AssertionError("unsupported file did not fail")
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_ingest.py -q
```

Expected: fails because `human2skill.ingest` does not exist.

- [ ] **Step 3: Implement source index helpers**

Create `src/human2skill/ingest.py` with functions:

- `source_index_path(base: Path) -> Path`
- `load_source_index(base: Path) -> dict`
- `write_source_index(base: Path, payload: dict) -> None`
- `next_source_id(index: dict) -> str`
- `add_text_source(...) -> dict`
- `ingest_file(base: Path, file_path: Path, ...) -> dict`

Behavior:

- New index shape: `{"schema_version": "1", "person_slug": base.name, "sources": []}`.
- IDs are sequential `src-0001`.
- Summary can be the first 500 stripped characters of text.
- Default retention is `summary_only`.
- Default `contains_private_data` is true.
- Default `allowed_in_public_skill` is false.
- Validate `source_index.schema.json` after each write.

- [ ] **Step 4: Implement file extraction**

Supported suffixes:

- `.md`: `markdown`
- `.txt`: `txt`
- `.pdf`: `pdf_text`

PDF extraction:

```python
from pypdf import PdfReader

reader = PdfReader(str(file_path))
text = "\n".join(page.extract_text() or "" for page in reader.pages)
```

If extracted PDF text is empty, raise `ValueError("PDF text extraction produced no text: <path>")`.

- [ ] **Step 5: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_ingest.py -q
```

Expected: tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/human2skill/ingest.py tests/test_ingest.py
git commit -m "feat: ingest manual and file sources"
```

---

## Task 5: Adaptive Interview Upgrade

**Files:**
- Modify: `src/human2skill/interview.py`
- Test: `tests/test_interview.py`

- [ ] **Step 1: Add failing tests for new dimensions and perspectives**

Modify `tests/test_interview.py` to include:

```python
from human2skill.interview import next_question_for_profile


def test_initial_coverage_includes_value_order_and_anti_patterns():
    coverage = initial_coverage()

    assert coverage["value_order"] == "missing"
    assert coverage["anti_patterns"] == "missing"


def test_self_perspective_uses_self_wording():
    coverage = initial_coverage()
    coverage["identity_context"] = "medium"

    question = next_question_for_profile(
        coverage,
        profile_type="self",
        perspective="self_answer",
        turn_count=1,
    )

    assert "你" in question
    assert "自己" in question or "过去" in question or "未来" in question


def test_observer_perspective_asks_for_observable_behavior():
    coverage = initial_coverage()
    coverage["identity_context"] = "medium"

    question = next_question_for_profile(
        coverage,
        profile_type="colleague",
        perspective="observer_answer",
        turn_count=1,
    )

    assert "具体" in question or "观察" in question or "场景" in question
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_interview.py -q
```

Expected: fails because new dimensions and function are missing.

- [ ] **Step 3: Extend interview dimensions**

Modify `CORE_DIMENSIONS` to include:

- `value_order`
- `anti_patterns`

Keep existing dimensions.

- [ ] **Step 4: Add profile and perspective question banks**

Add question banks:

- General observer questions ask for observable behavior, approximate wording, context, and counterexamples.
- Self questions ask for self-reflection, recurring decisions, long-term preferences, and blind spots.
- Profile-specific wording for colleague, relationship, mentor, self.

- [ ] **Step 5: Implement `next_question_for_profile`**

Signature:

```python
def next_question_for_profile(
    coverage: dict[str, str],
    *,
    profile_type: str,
    perspective: str,
    turn_count: int,
) -> str:
```

Rules:

- Choose first missing or low dimension in priority order.
- Use self bank when `perspective == "self_answer"`.
- Use observer bank otherwise.
- At `turn_count >= 20`, prefix with the existing budget warning.
- Return enough-information message if all dimensions are medium/high.

- [ ] **Step 6: Keep backward compatibility**

Keep `next_question(coverage, turn_count)` and make it call `next_question_for_profile(... profile_type="relationship", perspective="observer_answer")`.

- [ ] **Step 7: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_interview.py -q
```

Expected: all interview tests pass.

- [ ] **Step 8: Commit**

```bash
git add src/human2skill/interview.py tests/test_interview.py
git commit -m "feat: upgrade adaptive interview coverage"
```

---

## Task 6: Evidence Pack Builder

**Files:**
- Create: `src/human2skill/evidence_builder.py`
- Modify: `src/human2skill/evidence.py`
- Test: `tests/test_evidence_builder.py`
- Test: `tests/test_evidence.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_evidence_builder.py`:

```python
from human2skill.evidence_builder import (
    add_claim,
    add_conflict,
    add_evidence,
    empty_evidence_pack,
)
from human2skill.evidence import find_overconfident_claims


def test_add_evidence_and_claim_links_ids():
    pack = empty_evidence_pack("li-ming")
    evidence = add_evidence(
        pack,
        source_type="observer_report",
        source_summary="用户观察到李明先问 impact。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    claim = add_claim(
        pack,
        claim="讨论方案前先问 impact。",
        claim_type="decision_heuristic",
        confidence="medium",
        evidence_ids=[evidence["evidence_id"]],
        profile_scope="colleague",
    )

    assert evidence["evidence_id"] == "ev-0001"
    assert claim["claim_id"].startswith("claim-")
    assert claim["evidence_ids"] == ["ev-0001"]


def test_add_conflict_records_halt_resolution():
    pack = empty_evidence_pack("li-ming")
    conflict = add_conflict(
        pack,
        claim_ids=["claim-a", "claim-b"],
        evidence_ids=["ev-0001", "ev-0002"],
        conflict_type="contextual",
        resolution="halt_for_review",
        note="工作场景直接，关系场景回避。",
    )

    assert conflict["conflict_id"] == "cf-0001"
    assert pack["conflicts"][0]["resolution"] == "halt_for_review"


def test_overconfident_value_order_claim_is_flagged():
    pack = empty_evidence_pack("li-ming")
    evidence = add_evidence(
        pack,
        source_type="model_inference",
        source_summary="模型推断其重视效率。",
        retention="summary_only",
        confidence="low",
        supports=[],
    )
    claim = add_claim(
        pack,
        claim="效率高于关系维护。",
        claim_type="value_order",
        confidence="high",
        evidence_ids=[evidence["evidence_id"]],
    )

    assert find_overconfident_claims(pack) == [{
        "claim_id": claim["claim_id"],
        "claimed": "high",
        "supported": "low",
    }]
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_evidence_builder.py -q
```

Expected: fails because `evidence_builder.py` does not exist.

- [ ] **Step 3: Implement evidence builder**

Create `src/human2skill/evidence_builder.py`.

Functions:

- `empty_evidence_pack(person_slug: str) -> dict`
- `next_evidence_id(pack: dict) -> str`
- `next_conflict_id(pack: dict) -> str`
- `claim_id_from_text(text: str) -> str`
- `add_evidence(...) -> dict`
- `add_claim(...) -> dict`
- `add_conflict(...) -> dict`

Rules:

- Evidence IDs are `ev-0001`.
- Conflict IDs are `cf-0001`.
- Claim ID slugifies first meaningful text into `claim-...`.
- If duplicate claim ID exists, suffix `-2`, `-3`.
- Validate evidence pack after changes.

- [ ] **Step 4: Update evidence helper for new claim types**

Ensure `find_overconfident_claims()` still works with `value_order`, `anti_pattern`, `pressure_response`, and claims without `profile_scope`.

- [ ] **Step 5: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_evidence.py tests/test_evidence_builder.py -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/human2skill/evidence.py src/human2skill/evidence_builder.py tests/test_evidence.py tests/test_evidence_builder.py
git commit -m "feat: build evidence packs with conflicts"
```

---

## Task 7: Distillation Contract and Mapping

**Files:**
- Create: `src/human2skill/distillation.py`
- Test: `tests/test_distillation.py`

- [ ] **Step 1: Write failing distillation tests**

Create `tests/test_distillation.py`:

```python
import pytest

from human2skill.distillation import DistillationError, distillation_to_sections, validate_distillation


def valid_distillation():
    return {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [{
            "title": "Impact first",
            "content": "先问 impact，再讨论方案。",
            "claim_ids": ["claim-impact-first"],
            "confidence": "medium",
            "evidence_summary": "会议摘要支持。",
            "limits": ["只覆盖工作评审。"]
        }],
        "decision_heuristics": [],
        "expression_dna": [],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [{
            "title": "关系场景不足",
            "content": "关系场景证据不足。",
            "claim_ids": [],
            "confidence": "low",
            "evidence_summary": "无直接证据。",
            "limits": ["不推断亲密关系。"]
        }],
        "scenario_tests": []
    }


def test_validate_distillation_accepts_claim_links():
    validate_distillation(valid_distillation(), available_claim_ids={"claim-impact-first"})


def test_validate_distillation_rejects_missing_claim_link():
    payload = valid_distillation()
    payload["mental_models"][0]["claim_ids"] = ["claim-missing"]

    with pytest.raises(DistillationError) as error:
        validate_distillation(payload, available_claim_ids={"claim-impact-first"})

    assert "claim-missing" in str(error.value)


def test_distillation_to_sections_maps_all_skill_sections():
    sections = distillation_to_sections(valid_distillation())

    assert "mental_models" in sections
    assert "honest_boundaries" in sections
    assert "Impact first" in sections["mental_models"][0]
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_distillation.py -q
```

Expected: fails because `distillation.py` does not exist.

- [ ] **Step 3: Implement distillation validation**

Create `src/human2skill/distillation.py` with:

- `DistillationError`
- `validate_distillation(payload, available_claim_ids)`
- `format_distilled_item(item)`
- `distillation_to_sections(payload)`

Rules:

- Validate schema first.
- For all sections except `honest_boundaries`, every item must have at least one claim ID.
- Every claim ID must exist in `available_claim_ids`.
- Boundaries may have no claim IDs.
- Format each item as `Title: content (confidence; evidence summary)` plus limits when present.

- [ ] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_distillation.py -q
```

Expected: tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/human2skill/distillation.py tests/test_distillation.py
git commit -m "feat: validate agent distillation output"
```

---

## Task 8: Skill Templates and Generator Variants

**Files:**
- Create: `templates/skill/advisor.md`
- Create: `templates/skill/first-person.md`
- Modify: `templates/skill/advisor.md`
- Modify: `src/human2skill/generator.py`
- Test: `tests/test_generator.py`

- [ ] **Step 1: Write failing tests for variants**

Extend `tests/test_generator.py`:

```python
from human2skill.generator import render_skill_variant, render_skill_variants


def full_distilled_sections():
    return {
        "mental_models": ["Impact first: 先问 impact。"],
        "expression_dna": ["短句，结论先行。"],
        "decision_heuristics": ["没有收益则推迟。"],
        "profile_specific": ["适合工作评审。"],
        "pressure_response": ["被质疑时问依据。"],
        "value_order": ["效果高于优雅。"],
        "anti_patterns": ["不接受无目标讨论。"],
        "honest_boundaries": ["关系场景证据不足。"],
    }


def test_render_advisor_variant_keeps_non_impersonation():
    meta = {"slug": "li-ming", "display_name": "李明", "voice_mode": "advisor"}

    content = render_skill_variant(meta, full_distilled_sections(), variant="advisor")

    assert "视角顾问" in content
    assert "不代表本人观点" in content
    assert "不声称自己就是 李明 本人" in content
    assert "价值排序" in content
    assert "反模式" in content


def test_render_first_person_variant_has_mandatory_disclaimer():
    meta = {"slug": "li-ming", "display_name": "李明", "voice_mode": "first_person"}

    content = render_skill_variant(meta, full_distilled_sections(), variant="first_person")

    assert "有限第一人称" in content
    assert "非本人观点" in content
    assert "不得声称自己就是李明本人" in content
    assert "我" in content


def test_render_both_variants_returns_two_entries():
    meta = {"slug": "li-ming", "display_name": "李明", "voice_mode": "both"}

    variants = render_skill_variants(meta, full_distilled_sections())

    assert set(variants) == {"advisor", "first_person"}
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_generator.py -q
```

Expected: fails because variant functions/templates do not exist.

- [ ] **Step 3: Create advisor template**

Create `templates/skill/advisor.md` with sections:

- frontmatter
- title
- non-impersonation disclaimer
- activation protocol
- core mental models
- expression DNA
- decision heuristics
- profile-specific layer
- pressure/conflict response
- value order
- anti-patterns
- honest boundaries
- evidence/confidence summary

- [ ] **Step 4: Create first-person template**

Create `templates/skill/first-person.md` with:

- frontmatter
- mandatory first activation disclaimer
- limited first-person operating protocol
- explicit non-impersonation line
- no message sending
- no manipulation
- same content sections as advisor

- [ ] **Step 5: Implement generator variants**

Modify `src/human2skill/generator.py`:

- Keep `render_skill()` for backward compatibility.
- Add `template_root()`.
- Add `render_skill_variant(meta, sections, variant)`.
- Add `render_skill_variants(meta, sections)`.
- Add `write_skill_variants(base, meta, sections)`.

Rules:

- `advisor` renders advisor only.
- `first_person` renders first-person only.
- `both` renders both.
- `public_skill/SKILL.md` should be advisor when available, otherwise the selected variant.
- Empty sections use existing evidence-insufficient fallback.

- [ ] **Step 6: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_generator.py -q
```

Expected: tests pass.

- [ ] **Step 7: Commit**

```bash
git add templates/skill src/human2skill/generator.py tests/test_generator.py
git commit -m "feat: render advisor and first person skills"
```

---

## Task 9: Structured Reviewer and Privacy Check

**Files:**
- Modify: `src/human2skill/reviewer.py`
- Test: `tests/test_reviewer.py`

- [ ] **Step 1: Write failing structured review tests**

Extend `tests/test_reviewer.py`:

```python
from human2skill.reviewer import structured_review


def safe_content():
    return "\n".join([
        "不代表本人观点",
        "不声称自己就是 李明 本人",
        "## 核心思维模型",
        "- Impact first",
        "## 表达 DNA",
        "- 短句",
        "## 诚实边界",
        "- 关系场景证据不足。",
        "- 投资建议证据不足。",
        "- 医疗法律问题不适用。",
    ])


def test_structured_review_passes_safe_advisor():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=safe_content(),
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-29T00:00:00+00:00",
    )

    assert report["passed"] is True
    assert report["scores"]["privacy_safety"] == 5
    assert report["scores"]["honest_boundary"] == 5


def test_structured_review_fails_first_person_without_disclaimer():
    report = structured_review(
        person_slug="li-ming",
        variant="first_person",
        content="## 诚实边界\n- 不确定。\n我就是李明",
        overconfident_claims=[],
        unresolved_conflicts=[],
        generated_at="2026-04-29T00:00:00+00:00",
    )

    assert report["passed"] is False
    assert "claims_to_be_person" in report["hard_failures"]


def test_structured_review_fails_overconfident_claims():
    report = structured_review(
        person_slug="li-ming",
        variant="advisor",
        content=safe_content(),
        overconfident_claims=[{"claim_id": "claim-a", "claimed": "high", "supported": "low"}],
        unresolved_conflicts=[],
        generated_at="2026-04-29T00:00:00+00:00",
    )

    assert report["passed"] is False
    assert "unsupported_high_confidence_claims" in report["hard_failures"]
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_reviewer.py -q
```

Expected: fails because `structured_review` does not exist.

- [ ] **Step 3: Implement structured review**

Modify `src/human2skill/reviewer.py`:

- Keep existing `review_public_skill(content)` wrapper.
- Add `structured_review(...) -> dict`.
- Score dimensions:
  - evidence consistency
  - confidence calibration
  - honest boundary
  - privacy safety
  - expression similarity
  - thinking utility
  - profile fit
- Hard failures:
  - `claims_to_be_person`
  - `missing_honest_boundaries`
  - `contains_private_raw_material`
  - `missing_disclaimer`
  - `unsupported_high_confidence_claims`
  - `unresolved_conflicts`
  - `first_person_missing_disclaimer`

Pass only when no hard failures and thresholds are met.

- [ ] **Step 4: Validate review report schema**

Call `validate_document("review_report.schema.json", report)` before returning.

- [ ] **Step 5: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_reviewer.py -q
```

Expected: tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/human2skill/reviewer.py tests/test_reviewer.py
git commit -m "feat: add structured privacy and quality review"
```

---

## Task 10: Scenario Replay Reports

**Files:**
- Create: `src/human2skill/scenario.py`
- Test: `tests/test_scenario.py`

- [ ] **Step 1: Write failing scenario tests**

Create `tests/test_scenario.py`:

```python
from human2skill.scenario import build_scenario_replay_report, scenario_summary_passed


def test_build_scenario_replay_report_requires_three_types():
    report = build_scenario_replay_report(
        person_slug="li-ming",
        variant="advisor",
        generated_at="2026-04-29T00:00:00+00:00",
        scenarios=[
            {
                "scenario_type": "historical",
                "input": "评审延期需求",
                "expected_behavior": "先问 impact",
                "actual_behavior": "先问目标和 impact",
                "passed": True,
                "notes": []
            },
            {
                "scenario_type": "counterfactual",
                "input": "高收益但实现很脏",
                "expected_behavior": "权衡收益和维护成本",
                "actual_behavior": "先问收益再看风险",
                "passed": True,
                "notes": []
            },
            {
                "scenario_type": "boundary",
                "input": "亲密关系建议",
                "expected_behavior": "承认证据不足",
                "actual_behavior": "说明关系场景证据不足",
                "passed": True,
                "notes": []
            },
        ],
    )

    assert scenario_summary_passed(report) is True
    assert len(report["scenarios"]) == 3
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_scenario.py -q
```

Expected: fails because `scenario.py` does not exist.

- [ ] **Step 3: Implement scenario module**

Create `src/human2skill/scenario.py`:

- `build_scenario_replay_report(...) -> dict`
- `scenario_summary_passed(report: dict) -> bool`

Rules:

- Required scenario types: `historical`, `counterfactual`, `boundary`.
- Report passes when all scenarios pass and all three types are present.
- Include `missing_scenario_types` if any are absent.

- [ ] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_scenario.py -q
```

Expected: tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/human2skill/scenario.py tests/test_scenario.py
git commit -m "feat: add scenario replay reports"
```

---

## Task 11: Storage Snapshots, Changelog, and Rollback

**Files:**
- Modify: `src/human2skill/storage.py`
- Test: `tests/test_storage.py`

- [ ] **Step 1: Write failing storage tests**

Extend `tests/test_storage.py`:

```python
from human2skill.storage import restore_version, write_changelog


def test_snapshot_version_copies_new_core_artifacts(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    write_json(base / "person.meta.json", {"slug": "li-ming"})
    write_json(base / "private_evidence/source_index.json", {"sources": []})
    write_json(base / "private_evidence/distillation.json", {"schema_version": "1"})
    write_json(base / "private_evidence/reviews/review-v1.json", {"passed": True})
    (base / "public_skill/SKILL.md").write_text("# skill", encoding="utf-8")

    snapshot = snapshot_version(base, "v1")

    assert (snapshot / "private_evidence/source_index.json").exists()
    assert (snapshot / "private_evidence/distillation.json").exists()
    assert (snapshot / "private_evidence/reviews/review-v1.json").exists()


def test_write_changelog_creates_version_markdown(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")

    path = write_changelog(base, "v2", ["Added src-0002"], ["claim-impact-first"], [])

    assert path.name == "v2.md"
    assert "Added src-0002" in path.read_text(encoding="utf-8")


def test_restore_version_restores_public_skill(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    (base / "public_skill/SKILL.md").write_text("# v1", encoding="utf-8")
    snapshot_version(base, "v1")
    (base / "public_skill/SKILL.md").write_text("# v2", encoding="utf-8")

    restore_version(base, "v1")

    assert (base / "public_skill/SKILL.md").read_text(encoding="utf-8") == "# v1"
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_storage.py -q
```

Expected: fails because new functions or copy behavior are missing.

- [ ] **Step 3: Extend snapshot behavior**

Modify `snapshot_version()` to copy:

- `person.meta.json`
- `public_skill/SKILL.md`
- `public_skill/variants/`
- `private_evidence/evidence_pack.json`
- `private_evidence/source_index.json`
- `private_evidence/distillation.json`
- `private_evidence/reviews/`
- `private_evidence/changelog/`

- [ ] **Step 4: Add changelog writer**

Implement:

```python
def write_changelog(base: Path, version: str, added_sources: list[str], changed_claims: list[str], conflicts: list[str]) -> Path:
```

Markdown sections:

- Added sources
- Changed claims
- Conflicts

- [ ] **Step 5: Add rollback restore**

Implement:

```python
def restore_version(base: Path, version: str) -> Path:
```

Rules:

- Restore files copied by snapshot.
- Raise `FileNotFoundError` if version does not exist.
- Return restored version directory.

- [ ] **Step 6: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_storage.py -q
```

Expected: tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/human2skill/storage.py tests/test_storage.py
git commit -m "feat: snapshot and restore full person artifacts"
```

---

## Task 12: Exporter

**Files:**
- Create: `src/human2skill/exporter.py`
- Test: `tests/test_exporter.py`

- [ ] **Step 1: Write failing exporter tests**

Create `tests/test_exporter.py`:

```python
import json
from pathlib import Path

from human2skill.exporter import export_skill
from human2skill.storage import initialize_person_dir, write_json


def prepare_skill(base: Path):
    (base / "public_skill/variants/advisor").mkdir(parents=True, exist_ok=True)
    (base / "public_skill/variants/advisor/SKILL.md").write_text("# advisor", encoding="utf-8")
    write_json(base / "private_evidence/reviews/review-v1.json", {"passed": True})


def test_export_codex_writes_manifest_and_skill(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    prepare_skill(base)

    export_dir = export_skill(
        base,
        host="codex",
        variant="advisor",
        created_at="2026-04-29T00:00:00+00:00",
    )

    assert (export_dir / "SKILL.md").exists()
    manifest = json.loads((export_dir / "export_manifest.json").read_text(encoding="utf-8"))
    assert manifest["host"] == "codex"
    assert manifest["review_passed"] is True
    assert manifest["privacy_check_passed"] is True


def test_export_rejects_unknown_host(tmp_path: Path):
    base = initialize_person_dir(tmp_path, "li-ming")
    prepare_skill(base)

    try:
        export_skill(base, host="unknown", variant="advisor")
    except ValueError as error:
        assert "Unknown host" in str(error)
    else:
        raise AssertionError("unknown host did not fail")
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_exporter.py -q
```

Expected: fails because `exporter.py` does not exist.

- [ ] **Step 3: Implement exporter**

Create `src/human2skill/exporter.py`:

- `latest_review_passed(base: Path) -> bool`
- `variant_skill_path(base: Path, variant: str) -> Path`
- `export_skill(base: Path, host: str, variant: str = "advisor", created_at: str | None = None) -> Path`

Rules:

- Validate host against `HOSTS`.
- Refuse export when latest review is missing or not passed.
- Copy selected `SKILL.md` into `outputs/{slug}/exports/{host}/`.
- Write `export_manifest.json` and validate schema.
- Host-specific package may be minimal in this task: `SKILL.md`, `README.md`, `export_manifest.json`.

- [ ] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_exporter.py -q
```

Expected: tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/human2skill/exporter.py tests/test_exporter.py
git commit -m "feat: export reviewed skills for hosts"
```

---

## Task 13: Explicit Installer

**Files:**
- Create: `src/human2skill/installer.py`
- Test: `tests/test_installer.py`

- [ ] **Step 1: Write failing installer tests**

Create `tests/test_installer.py`:

```python
from pathlib import Path

from human2skill.installer import install_export


def test_install_export_copies_to_explicit_target(tmp_path: Path):
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    (export_dir / "SKILL.md").write_text("# skill", encoding="utf-8")
    target = tmp_path / "target"

    installed = install_export(export_dir, target, package_name="li-ming")

    assert installed == target / "li-ming"
    assert (installed / "SKILL.md").exists()


def test_install_export_requires_existing_export(tmp_path: Path):
    try:
        install_export(tmp_path / "missing", tmp_path / "target", package_name="li-ming")
    except FileNotFoundError as error:
        assert "missing" in str(error)
    else:
        raise AssertionError("missing export did not fail")
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_installer.py -q
```

Expected: fails because `installer.py` does not exist.

- [ ] **Step 3: Implement installer**

Create `src/human2skill/installer.py`:

- `install_export(export_dir: Path, target_dir: Path, package_name: str, force: bool = True) -> Path`

Rules:

- Export dir must exist.
- Target is caller-provided.
- Copy export directory to `target_dir/package_name`.
- If target exists and `force` is true, replace it.
- If target exists and `force` is false, raise `FileExistsError`.

- [ ] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_installer.py -q
```

Expected: tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/human2skill/installer.py tests/test_installer.py
git commit -m "feat: install exported skills explicitly"
```

---

## Task 14: Flow Orchestration

**Files:**
- Create: `src/human2skill/flow.py`
- Test: `tests/test_flow.py`
- Test: `tests/test_smoke_flow.py`

- [ ] **Step 1: Write failing flow tests**

Create `tests/test_flow.py`:

```python
import json
from pathlib import Path

from human2skill.evidence_builder import add_claim, add_evidence
from human2skill.flow import build_from_distillation, create_project_person


def test_create_project_person_initializes_person(tmp_path: Path):
    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-29T00:00:00+00:00",
    )

    assert (base / "person.meta.json").exists()
    assert (base / "private_evidence/source_index.json").exists()


def test_build_from_distillation_renders_and_reviews(tmp_path: Path):
    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-29T00:00:00+00:00",
    )
    pack = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "evidence": [],
        "claims": [],
        "conflicts": [],
    }
    ev = add_evidence(pack, source_type="observer_report", source_summary="先问 impact。", retention="summary_only", confidence="medium", supports=[])
    add_claim(pack, claim="先问 impact。", claim_type="decision_heuristic", confidence="medium", evidence_ids=[ev["evidence_id"]])
    (base / "private_evidence/evidence_pack.json").write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    distillation = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [],
        "decision_heuristics": [{
            "title": "Impact first",
            "content": "先问 impact。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"]
        }],
        "expression_dna": [],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [{
            "title": "关系不足",
            "content": "关系场景证据不足。",
            "claim_ids": [],
            "confidence": "low",
            "evidence_summary": "无证据。",
            "limits": ["不推断关系。"]
        }],
        "scenario_tests": []
    }

    result = build_from_distillation(base, distillation, generated_at="2026-04-29T00:00:00+00:00")

    assert result["review"]["passed"] is True
    assert (base / "public_skill/SKILL.md").exists()
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_flow.py -q
```

Expected: fails because `flow.py` does not exist.

- [ ] **Step 3: Implement create flow**

Create `src/human2skill/flow.py`:

- `create_project_person(...) -> Path`

Behavior:

- Calls intake `create_person`.
- Creates empty source index.
- Creates empty evidence pack.

- [ ] **Step 4: Implement build flow**

Add:

- `load_meta(base)`
- `load_evidence_pack(base)`
- `available_claim_ids(pack)`
- `build_from_distillation(base, distillation, generated_at=None) -> dict`

Behavior:

- Validate distillation.
- Write `private_evidence/distillation.json`.
- Map distillation to sections.
- Render skill variants.
- Run structured review for each rendered variant.
- Write review JSON.
- Snapshot version.
- Return result dict with review and variant paths.

- [ ] **Step 5: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_flow.py tests/test_smoke_flow.py -q
```

Expected: tests pass. Existing smoke test may need minor adjustment to include required meta fields after schema expansion.

- [ ] **Step 6: Commit**

```bash
git add src/human2skill/flow.py tests/test_flow.py tests/test_smoke_flow.py
git commit -m "feat: orchestrate person skill build flow"
```

---

## Task 15: Incremental Update Flow

**Files:**
- Modify: `src/human2skill/flow.py`
- Test: `tests/test_update_flow.py`

- [ ] **Step 1: Write failing update tests**

Create `tests/test_update_flow.py`:

```python
from human2skill.flow import detect_update_conflicts, summarize_update


def test_detect_update_conflicts_halts_on_active_conflict():
    pack = {
        "claims": [
            {"claim_id": "claim-a", "status": "active"},
            {"claim_id": "claim-b", "status": "active"},
        ],
        "conflicts": [{
            "conflict_id": "cf-0001",
            "claim_ids": ["claim-a", "claim-b"],
            "evidence_ids": ["ev-0001", "ev-0002"],
            "conflict_type": "contextual",
            "resolution": "halt_for_review",
            "note": "场景冲突"
        }]
    }

    result = detect_update_conflicts(pack)

    assert result["halted"] is True
    assert result["conflicts"][0]["conflict_id"] == "cf-0001"


def test_summarize_update_lists_sources_claims_and_conflicts():
    summary = summarize_update(
        added_sources=["src-0002"],
        changed_claims=["claim-impact-first"],
        conflicts=["cf-0001"],
    )

    assert "src-0002" in summary
    assert "claim-impact-first" in summary
    assert "cf-0001" in summary
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_update_flow.py -q
```

Expected: fails because update helpers do not exist.

- [ ] **Step 3: Implement update helpers**

Add to `flow.py`:

- `detect_update_conflicts(pack: dict) -> dict`
- `summarize_update(added_sources, changed_claims, conflicts) -> str`

Rules:

- Any conflict with `resolution == "halt_for_review"` halts update.
- Summary uses simple Markdown sections.

- [ ] **Step 4: Wire changelog use**

When future build/update calls pass update metadata, write changelog via `write_changelog`.

- [ ] **Step 5: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_update_flow.py -q
```

Expected: tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/human2skill/flow.py tests/test_update_flow.py
git commit -m "feat: detect conflicts during incremental updates"
```

---

## Task 16: CLI Entry Point

**Files:**
- Create: `src/human2skill/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Create `tests/test_cli.py`:

```python
import json
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str, cwd: Path):
    return subprocess.run(
        [sys.executable, "-m", "human2skill.cli", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )


def test_cli_create_and_ingest(tmp_path: Path):
    result = run_cli(
        "create",
        "--root",
        str(tmp_path),
        "--slug",
        "li-ming",
        "--name",
        "李明",
        "--profile",
        "colleague",
        "--relationship",
        "coworker",
        "--use-case",
        "work review",
        cwd=tmp_path,
    )

    assert "created" in result.stdout.lower()

    note = tmp_path / "note.txt"
    note.write_text("李明先问 impact。", encoding="utf-8")
    ingest = run_cli("ingest", "--root", str(tmp_path), "--slug", "li-ming", "--file", str(note), cwd=tmp_path)

    assert "src-0001" in ingest.stdout
    index = json.loads((tmp_path / "outputs/li-ming/private_evidence/source_index.json").read_text(encoding="utf-8"))
    assert index["sources"][0]["source_id"] == "src-0001"
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q
```

Expected: fails because `cli.py` does not exist.

- [ ] **Step 3: Implement argparse CLI**

Create `src/human2skill/cli.py` with subcommands:

- `create`
- `ingest`
- `question`
- `build`
- `review`
- `export`
- `install`

Minimum behavior in this task:

- `create` calls `create_project_person`.
- `ingest` calls `ingest_file`.
- `question` calls `next_question_for_profile`.
- `export` calls `export_skill`.
- `install` calls `install_export`.

Build/review can be wired to flow if required arguments are provided.

- [ ] **Step 4: Keep outputs machine-readable enough**

Print concise success lines:

- `created: <path>`
- `ingested: src-0001`
- `exported: <path>`
- `installed: <path>`

- [ ] **Step 5: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q
```

Expected: tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/human2skill/cli.py tests/test_cli.py
git commit -m "feat: add human2skill cli"
```

---

## Task 17: Meta-skill Entry Document

**Files:**
- Create: `human2skill-meta/SKILL.md`
- Test: `tests/test_meta_skill_docs.py`

- [ ] **Step 1: Write failing doc tests**

Create `tests/test_meta_skill_docs.py`:

```python
from pathlib import Path


def test_meta_skill_documents_required_flow():
    content = Path("human2skill-meta/SKILL.md").read_text(encoding="utf-8")

    assert "human2skill create" in content
    assert "human2skill ingest" in content
    assert "distillation.json" in content
    assert "summary_only" in content
    assert "不输出私域原文" in content
    assert "advisor" in content
    assert "first_person" in content


def test_meta_skill_mentions_checkpoints():
    content = Path("human2skill-meta/SKILL.md").read_text(encoding="utf-8")

    assert "Source Coverage Checkpoint" in content
    assert "Distillation Checkpoint" in content
    assert "Review Checkpoint" in content
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_meta_skill_docs.py -q
```

Expected: fails because the Meta-skill document does not exist.

- [ ] **Step 3: Create Meta-skill document**

Create `human2skill-meta/SKILL.md` with:

- frontmatter name and description.
- user flow:
  1. confirm subject
  2. choose profile
  3. choose voice mode
  4. confirm privacy defaults
  5. ingest source
  6. interview
  7. build evidence
  8. write `distillation.json`
  9. call build/review/export
- CLI command examples.
- agent-assisted distillation requirements.
- privacy rules.
- checkpoint names:
  - `Source Coverage Checkpoint`
  - `Distillation Checkpoint`
  - `Review Checkpoint`
- stop rules for conflict and privacy failure.

- [ ] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_meta_skill_docs.py -q
```

Expected: tests pass.

- [ ] **Step 5: Commit**

```bash
git add human2skill-meta/SKILL.md tests/test_meta_skill_docs.py
git commit -m "docs: add human2skill meta skill entry"
```

---

## Task 18: Examples

**Files:**
- Create: `examples/colleague-li-ming/`
- Create: `examples/relationship-chen-yu/`
- Create: `examples/self-future-me/`
- Test: `tests/test_examples.py`

- [ ] **Step 1: Write failing example tests**

Create `tests/test_examples.py`:

```python
import json
from pathlib import Path


EXAMPLES = [
    Path("examples/colleague-li-ming"),
    Path("examples/relationship-chen-yu"),
    Path("examples/self-future-me"),
]


def test_examples_have_public_skill_private_evidence_and_review():
    for base in EXAMPLES:
        assert (base / "public_skill/SKILL.md").exists()
        assert (base / "private_evidence/evidence_pack.json").exists()
        assert (base / "private_evidence/reviews/review-v1.json").exists()


def test_examples_do_not_allow_private_quotes():
    for base in EXAMPLES:
        meta = json.loads((base / "person.meta.json").read_text(encoding="utf-8"))
        assert meta["privacy_policy"]["public_skill_allows_private_quotes"] is False


def test_examples_review_passed():
    for base in EXAMPLES:
        review = json.loads((base / "private_evidence/reviews/review-v1.json").read_text(encoding="utf-8"))
        assert review["passed"] is True
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_examples.py -q
```

Expected: fails because examples do not exist.

- [ ] **Step 3: Generate examples using implemented flow**

Create three fictional examples:

- `colleague-li-ming`: work review and collaboration.
- `relationship-chen-yu`: friend/family support and conflict repair.
- `self-future-me`: self reflection and future-self decision mirror.

Each example includes:

- `person.meta.json`
- `public_skill/SKILL.md`
- `public_skill/variants/advisor/SKILL.md`
- optional first-person variant when voice mode requires it
- `private_evidence/source_index.json`
- `private_evidence/evidence_pack.json`
- `private_evidence/distillation.json`
- `private_evidence/reviews/review-v1.json`
- `exports/codex/export_manifest.json`

Use fictional source summaries only.

- [ ] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_examples.py -q
```

Expected: tests pass.

- [ ] **Step 5: Commit**

```bash
git add examples tests/test_examples.py
git commit -m "test: add fictional human2skill examples"
```

---

## Task 19: End-to-End Integration

**Files:**
- Modify: `tests/test_smoke_flow.py`
- Create: `tests/test_end_to_end_p0_p2.py`
- Modify: docs if CLI usage changed: `docs/README.md`

- [ ] **Step 1: Write full e2e test**

Create `tests/test_end_to_end_p0_p2.py`:

```python
import json
from pathlib import Path

from human2skill.evidence_builder import add_claim, add_evidence, empty_evidence_pack
from human2skill.exporter import export_skill
from human2skill.flow import build_from_distillation, create_project_person
from human2skill.ingest import add_text_source


def test_p0_p2_end_to_end_flow(tmp_path: Path):
    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="both",
        now="2026-04-29T00:00:00+00:00",
    )
    source = add_text_source(
        base,
        title="manual note",
        text="李明在方案评审时先问 impact 和目标。",
        source_kind="manual_text",
        now="2026-04-29T00:00:00+00:00",
    )
    pack = empty_evidence_pack("li-ming")
    evidence = add_evidence(
        pack,
        source_type="observer_report",
        source_summary=source["summary"],
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    claim = add_claim(
        pack,
        claim="方案评审前先问 impact 和目标。",
        claim_type="decision_heuristic",
        confidence="medium",
        evidence_ids=[evidence["evidence_id"]],
        profile_scope="colleague",
    )
    (base / "private_evidence/evidence_pack.json").write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    distillation = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [],
        "decision_heuristics": [{
            "title": "Impact first",
            "content": "方案评审前先问 impact 和目标。",
            "claim_ids": [claim["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "手动观察摘要支持。",
            "limits": ["只覆盖工作评审。"]
        }],
        "expression_dna": [],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [{
            "title": "关系场景不足",
            "content": "关系场景证据不足。",
            "claim_ids": [],
            "confidence": "low",
            "evidence_summary": "没有关系场景材料。",
            "limits": ["不推断亲密关系。"]
        }],
        "scenario_tests": []
    }

    result = build_from_distillation(base, distillation, generated_at="2026-04-29T00:00:00+00:00")
    export_dir = export_skill(base, host="codex", variant="advisor", created_at="2026-04-29T00:00:00+00:00")

    assert result["review"]["passed"] is True
    assert (base / "public_skill/variants/advisor/SKILL.md").exists()
    assert (base / "public_skill/variants/first_person/SKILL.md").exists()
    assert (export_dir / "SKILL.md").exists()
```

- [ ] **Step 2: Run e2e test and confirm failures**

Run:

```bash
.venv/bin/python -m pytest tests/test_end_to_end_p0_p2.py -q
```

Expected: any missing integration behavior fails.

- [ ] **Step 3: Fix integration gaps only**

Resolve gaps in the smallest relevant modules. Do not add new subsystems.

Allowed fixes:

- Missing file writes.
- Review report path mismatch.
- Variant path mismatch.
- Schema validation mismatch.
- Export manifest mismatch.

- [ ] **Step 4: Update docs README with CLI summary**

Add concise CLI usage to `docs/README.md`:

```markdown
## P0-P2 Flow

Use `human2skill create`, `ingest`, `build`, `review`, `export`, and `install` for the local flow. Distillation remains agent-assisted through `distillation.json`; Python validates and renders the durable artifacts.
```

- [ ] **Step 5: Run full test suite**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src tests docs/README.md
git commit -m "test: cover p0 p2 end to end flow"
```

---

## Task 20: Final Verification and Plan Closure

**Files:**
- No new implementation files expected.
- Verify all changed files.

- [ ] **Step 1: Run full tests**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run incomplete-marker scan**

Run:

```bash
rg -n "T""BD|T""ODO|implement"" later|fill"" in|待""定|稍""后" src tests schemas templates human2skill-meta examples docs
```

Expected: no matches in new production/test/docs content except third-party or historical text that is intentionally unchanged.

- [ ] **Step 3: Run privacy scan on examples**

Run:

```bash
rg -n "完整聊天记录|身份证|手机号|原始私聊|朋友圈原文" examples
```

Expected: no matches.

- [ ] **Step 4: Inspect git status**

Run:

```bash
git status --short
```

Expected: only intended files are modified or untracked before final commit.

- [ ] **Step 5: Commit final verification updates if any**

If verification required docs or test adjustments:

```bash
git add <changed-files>
git commit -m "chore: finalize human2skill p0 p2 implementation"
```

If no files changed after the last task, skip this commit.

---

## Self-Review Checklist

- Spec coverage:
  - P0 create/build/review is covered by Tasks 3, 7, 8, 9, 14, 19.
  - P1 ingest/update/conflict/version is covered by Tasks 4, 6, 11, 15.
  - P2 structured review/scenario/export/install is covered by Tasks 9, 10, 12, 13.
  - Hybrid Meta-skill entry is covered by Task 17.
  - Examples are covered by Task 18.
  - P3 exclusions are preserved; no OCR engine, UI/TUI, encryption, multi-observer merge, or drift monitor is planned.
- Type consistency:
  - `voice_mode` uses `advisor | first_person | both`.
  - Host names use `codex | claude-code | openclaw | hermes`.
  - Source IDs use `src-0001`.
  - Evidence IDs use `ev-0001`.
  - Conflict IDs use `cf-0001`.
  - Claim IDs use `claim-...`.
- Safety:
  - Public skill rendering includes non-impersonation boundaries.
  - First-person rendering includes mandatory disclaimer.
  - Export requires a passed review.
  - Install requires explicit target directory.
- Verification:
  - Every implementation task has a focused test.
  - Final task runs full pytest, incomplete-marker scan, and privacy scan.
