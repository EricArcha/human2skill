# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

human2skill is a Meta-skill for distilling limited source material and adaptive interviews about a person into a reusable "perspective advisor" Skill. The output is a runnable `SKILL.md` backed by a private evidence pack — private source material is separated from the distributable skill by design.

First version targets private/personally-known individuals (colleagues, friends, mentors, self), not public figures.

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

# Install dev dependencies (after cloning)
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
```

Python 3.11+ required. `.venv/` and `references/repos/` are in `.gitignore`.

## Architecture

The system is implemented as a local-first seven-module pipeline. P0-P2 currently covers project intake, evidence/source handling, agent-assisted distillation validation, variant skill generation, structured review gates, export/install helpers, examples, and CLI coverage.

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
- `cli.py` — command entrypoint for `create`, `ingest`, `question`, `build`, `review`, `export`, and `install`.
- `intake.py` / `flow.py` — create person projects, orchestrate build/review/snapshot flow, and handle update conflict gates.
- `ingest.py` — ingest local text/markdown/pdf-like source material into source indexes and evidence structures.
- `profiles.py` — load 4 bundled profile presets (`colleague`, `relationship`, `mentor`, `self`) and infer profile type from context.
- `evidence.py` / `evidence_builder.py` — three-tier evidence weights, claim support, overconfidence detection, claim/evidence/conflict builder APIs.
- `interview.py` — coverage map and gap-driven Chinese question selection.
- `distillation.py` — validates distillation JSON against schemas and evidence claim IDs, formats sections, detects overconfident distillation items.
- `generator.py` — renders advisor and first-person `SKILL.md` variants from bundled templates.
- `reviewer.py` — structured review with hard failures plus 1-5 score thresholds (evidence consistency ≥4, calibration ≥5, boundaries ≥5, privacy ≥5, expression ≥4, thinking utility ≥4, profile fit ≥4).
- `scenario.py` — scenario replay report across three required types (historical, counterfactual, boundary); passes only when all scenarios pass and all types are present.
- `schemas.py` — JSON Schema loading and validation via `importlib.resources`, used by reviewer and evidence pack builder to validate outputs.
- `constants.py` — enumerations for profile types, voice modes, retention policies, hosts, source kinds, claim types, conflict types, and review score keys.
- `timeutils.py` — `utc_now_iso()` helper for consistent UTC timestamps.
- `exporter.py` / `installer.py` — variant-specific export gates and host install helpers.
- `storage.py` — person directory initialization, JSON writing, and version snapshots.

**Package resources** live under `src/human2skill/schemas/` and `src/human2skill/templates/` and are loaded via `importlib.resources` so installed wheels work outside the source tree.

## Key Design Decisions

- **Perspective advisor, not impersonation** — generated skills never claim to be the person. Template includes mandatory disclaimer.
- **Public skill / private evidence separation** — raw private material never enters distributable `SKILL.md`. Retention policies: `summary_only` (default), `no_raw_retention`, `local_private_raw`.
- **Four profile types**: `colleague`, `relationship`, `mentor`, `self` — each with different `special_sections` and `weights`. Shared `core_sections` across all.
- **Three-tier evidence**: L1 (direct quote/behavior), L2 (observer report), L3 (model inference). Confidence: high/medium/low.
- **Structured review gate**: generated variants pass only when there are no hard failures and all required score thresholds are met.
- **Variant-specific export**: `advisor` and `first_person` exports require their matching review report to pass.
- **Multi-host**: core is host-neutral; current host list is defined in `src/human2skill/constants.py`.
- **Incremental evolution**: accepted conflicts may be scoped or marked low-confidence; only `halt_for_review` blocks build/review flow.
- **Version snapshots are gated**: `build_from_distillation` only creates a version snapshot when all variant reviews pass. This ensures every snapshot represents a passing state.
- **CLI build `--distillation` flag**: the `build` command accepts an optional `--distillation` path, defaulting to `private_evidence/distillation.json`.

## Current Implementation State

**P0-P2 implementation is merged locally.** The current suite has 132 pytest tests covering schemas, profile/template resources, intake, ingest, evidence building, distillation validation, generation, structured review, export/install, CLI flow, examples, and update conflict handling.

**Known boundary:** distillation synthesis is still agent-assisted through `distillation.json`; Python validates and renders durable artifacts but does not independently infer all human perspective content from raw sources.

**Reference repos:** `references/repos/colleague-skill` (engineering patterns) and `references/repos/nuwa-skill` (distillation methods) are not tracked in git (`.gitignore`).

**Existing skill:** `zg-strategy-distillation/` is a separate, working Claude Code skill for distilling Z哥's investment strategy knowledge — not part of the human2skill pipeline.
