# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

human2skill is a Meta-skill for distilling limited source material and adaptive interviews about a person into a reusable "perspective advisor" Skill. The output is a runnable `SKILL.md` backed by a private evidence pack — private source material is separated from the distributable skill by design.

First version targets private/personally-known individuals (colleagues, friends, mentors, self), not public figures.

The project itself is also an installable meta-skill (see `SKILL.md` root frontmatter), invokable via `/human2skill` or `人物蒸馏`.

## Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
.venv/bin/python -m pytest

# Run a single test file
.venv/bin/python -m pytest tests/test_schemas.py -q

# Run a single test function
.venv/bin/python -m pytest tests/test_profiles.py::test_infers_colleague_from_work_context -q

# Quality check on a generated SKILL.md
python scripts/quality_check.py outputs/<slug>/public_skill/SKILL.md
# also works on variant files:
python scripts/quality_check.py outputs/<slug>/public_skill/variants/advisor/SKILL.md

# Regenerate example projects
python scripts/generate_examples.py

# Install dev dependencies (after cloning)
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# Quick install
make install && make test
```

Python 3.11+ required. `.venv/` and `references/repos/` are in `.gitignore`.

## Architecture

The system is implemented as a local-first seven-module pipeline:

| # | Module | Status | Location |
|---|--------|--------|----------|
| 1 | Intake Router | implemented | `src/human2skill/intake.py`, `src/human2skill/flow.py`, `src/human2skill/cli.py` |
| 2 | Corpus Ingestor | implemented | `src/human2skill/ingest.py` |
| 3 | Coverage Analyzer | implemented | `src/human2skill/interview.py` |
| 4 | Adaptive Interviewer | implemented | `src/human2skill/interview.py` |
| 5 | Evidence Pack Builder | implemented | `src/human2skill/evidence_builder.py`, `src/human2skill/evidence.py` |
| 6 | Distillation Engine | validation and mapping implemented; synthesis remains agent-assisted | `src/human2skill/distillation.py` |
| 7 | Skill Generator + Reviewer + Evolution | implemented for P0-P2 | `src/human2skill/generator.py`, `src/human2skill/reviewer.py`, `src/human2skill/scenario.py`, `src/human2skill/exporter.py`, `src/human2skill/installer.py`, `src/human2skill/storage.py` |

**Implemented modules** (`src/human2skill/`):
- `cli.py` — command entrypoint for `create`, `ingest`, `question`, `build`, `review`, `export`, `install`, `interview`, `check-coverage`, `status`.
- `intake.py` / `flow.py` — create person projects, orchestrate build/review/snapshot flow, handle update conflict gates. `flow.py` is the main orchestrator: `create_project_person()` sets up a project, `build_from_distillation()` runs the full build → render → review → snapshot pipeline.
- `ingest.py` — ingest local text/markdown/pdf source material into source indexes and evidence structures. Automatically scans for PII via `PRIVATE_MARKERS` and raises on match.
- `profiles.py` — load 4 bundled profile presets (`colleague`, `relationship`, `mentor`, `self`) and infer profile type from Chinese-language context.
- `evidence.py` / `evidence_builder.py` — three-tier evidence weights (L1 direct/behavior, L2 observer, L3 inference), claim support level calculator, overconfidence detection, claim/evidence/conflict builder APIs with schema validation.
- `interview.py` — coverage map and gap-driven Chinese question selection. 10 dimensions, 20-question budget. Profile-specific question banks override generic ones. `run_interview_loop()` is interactive stdin/stdout.
- `distillation.py` — validates distillation JSON against schemas + claim ID integrity, formats sections into markdown, detects overconfident distillation items.
- `generator.py` — renders `advisor` and `first_person` SKILL.md variants from bundled Jinja-less templates (`templates/skill/`). Uses `str.format()` with sections as pre-formatted markdown blocks.
- `reviewer.py` — structured review with 7 hard failure checks plus 7 scoring dimensions (each 1-5, with pass thresholds: evidence_consistency ≥4, calibration ≥5, boundaries ≥5, privacy ≥5, expression ≥4, thinking utility ≥4, profile fit ≥4).
- `scenario.py` — scenario replay report across three required types (historical, counterfactual, boundary); passes only when all scenarios pass and all types are present.
- `schemas.py` — JSON Schema loading via `importlib.resources` and `Draft202012Validator`. Used by reviewer, evidence_builder, exporter, and ingest to validate outputs at production boundaries.
- `constants.py` — single-source for all enumerations: profile types, voice modes, retention policies, hosts, source kinds, claim types, conflict types, review score keys, private markers, interview budget.
- `timeutils.py` — `utc_now_iso()` helper for consistent UTC timestamps across the pipeline.
- `exporter.py` / `installer.py` — variant-specific export gates (require passing review + privacy check), 4-host install helpers (codex, claude-code, openclaw, hermes).
- `storage.py` — person directory initialization, JSON writing, version snapshots, backup-before-update, changelog writing, version restore.

**Package resources** live under `src/human2skill/schemas/` (6 JSON schemas for evidence_pack, distillation, review_report, person.meta, source_index, export_manifest) and `src/human2skill/templates/` (4 profile json presets + 2 skill markdown templates). Loaded via `importlib.resources` so installed wheels work outside the source tree.

**`__init__.py`** version-sources via `importlib.metadata.version("human2skill")`, sourced from `pyproject.toml`.

## Key Design Decisions

- **Perspective advisor, not impersonation** — generated skills never claim to be the person. Templates include mandatory disclaimer. Hard failure in reviewer if "我就是" appears in content.
- **Public skill / private evidence separation** — raw private material never enters distributable `SKILL.md`. Retention policies: `summary_only` (default), `no_raw_retention`, `local_private_raw`.
- **Four profile types**: `colleague`, `relationship`, `mentor`, `self` — each with different `special_sections` and `weights`. Shared `core_sections` across all.
- **Three-tier evidence**: L1 (direct quote/behavior), L2 (observer report), L3 (model inference). Confidence: high/medium/low. Overconfidence detection warns when claim confidence exceeds evidence support.
- **Structured review gate**: generated variants pass only when there are no hard failures AND all 7 score thresholds are met. `build_from_distillation` only snapshots versions when all variants pass.
- **Variant-specific export**: `advisor` and `first_person` exports require their matching review report to pass. Privacy re-check at export time.
- **Multi-host**: core is host-neutral; current hosts (codex, claude-code, openclaw, hermes) defined in `src/human2skill/constants.py`.
- **Incremental evolution**: accepted conflicts may be scoped or marked low-confidence; only `halt_for_review` blocks build/review flow. `backup_before_update()` archives pre-update state.
- **Version snapshots are gated**: `build_from_distillation` only creates a version snapshot when all variant reviews pass. This ensures every snapshot represents a passing state.
- **PII scanning at ingest**: `ingest.py` scans text against `PRIVATE_MARKERS` (完整聊天记录, 身份证, 手机号, etc.) and raises `ValueError` on match. Safety by default.
- **Governance rules**: `GOVERNANCE.md` documents the Phase workflow, checkpoints, iteration limits, and safety rules for the distillation process.

## Test Patterns

Tests use pytest with `tmp_path` for filesystem isolation. The integration test in `test_end_to_end_p0_p2.py` is the canonical full-flow example: create project → ingest source → build evidence → add distillation → `build_from_distillation()` → `export_skill()` → assert all artifacts exist.

Key test files cover: schemas (8), profiles (4), evidence building (12+), distillation validation (16+), generator rendering (16+), structured review (12+), exporter/installer (8+), CLI smoke tests, example validation, update conflict handling, and scenario replay.

## Current Implementation State

**P0-P2 implementation is merged locally.** The current suite has 132+ pytest tests covering schemas, profile/template resources, intake, ingest, evidence building, distillation validation, generation, structured review, export/install, CLI flow, examples, and update conflict handling.

**Voice mode**: `voice_mode` defaults auto-inferred from profile type: `self` and `relationship` → `first_person`, `colleague` and `mentor` → `advisor`. Override with `--voice-mode`.

**Templates**: `advisor.md` (third-person observer with structured evidence sections) and `first_person.md` (immersive first-person with role-playing rules, identity card, routing, and signature quotes). Both support optional `quote`/`quote_source` fields in distillation items.

**Quality**: `scripts/quality_check.py` runs 7 automated checks (mental model count, limitations per model, expression DNA distinctiveness, honest boundaries, internal tensions, primary source ratio, corpus archive). `corpus/raw/` archives ingested source text for verification.

**Examples**: 3 bundled example personas under `examples/` — `colleague-li-ming`, `relationship-chen-yu`, `self-future-me`. Each has complete evidence packs, public skills, review reports, and version snapshots. Generated by `scripts/generate_examples.py`.

**Known boundary:** distillation synthesis is still agent-assisted through `distillation.json`; Python validates and renders durable artifacts but does not independently infer all human perspective content from raw sources.

**Reference repos:** `references/repos/colleague-skill` (engineering patterns) and `references/repos/nuwa-skill` (distillation methods) are not tracked in git (`.gitignore`).

**Version changes**: see `CHANGELOG.md`.
