# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

human2skill is a Meta-skill for distilling limited source material and adaptive interviews about a person into a reusable "perspective advisor" Skill. The output is a runnable `SKILL.md` backed by a private evidence pack — private source material is separated from the distributable skill by design.

First version targets private/personally-known individuals (colleagues, friends, mentors, self), not public figures.

## Repository Structure

```
human2skill/
  docs/
    design/          # Stable design docs (architecture, evidence model, interviews, review, profiles)
    plans/           # Product roadmap (P0-P3 phases)
    research/        # Reference repo analysis
    superpowers/
      specs/         # Formal design spec
      plans/         # Agentic worker execution plan (9 tasks)
  references/        # Reference repositories (colleague-skill, nuwa-skill)
  zg-strategy-distillation/  # Existing skill: Z哥 investment strategy knowledge distillation
  templates/         # (to be created per execution plan)
  schemas/           # (to be created per execution plan)
  src/human2skill/   # (to be created per execution plan)
  tests/             # (to be created per execution plan)
```

## Architecture

Seven-module pipeline:

1. **Intake Router** — confirms profile type, use case, consent status, privacy policy
2. **Corpus Ingestor** — ingests text/markdown/chat excerpts/meeting notes
3. **Coverage Analyzer** — maintains a coverage map across 8 dimensions, identifies gaps
4. **Adaptive Interviewer** — gap-driven questioning (~20 round budget, not fixed)
5. **Evidence Pack Builder** — structured evidence with 3 tiers: direct quote/behavior, observer report, model inference
6. **Distillation Engine** — extracts mental models, expression DNA, decision heuristics, pressure response, boundaries
7. **Skill Generator + Reviewer + Evolution Manager** — renders `SKILL.md`, dual-review, incremental merging with conflict detection

## Key Design Decisions

- **Perspective advisor, not impersonation** — generated skills never claim to be the person
- **Public skill / private evidence separation** — raw private material never enters distributable `SKILL.md`
- **Four profile types**: `colleague`, `relationship`, `mentor`, `self` — each with different weights, questions, and output sections
- **Three-tier evidence**: L1 (direct quote/behavior), L2 (observer report), L3 (model inference)
- **Dual review**: Reviewer A (evidence & boundary) + Reviewer B (expression & utility)
- **Multi-host**: core is host-neutral; adapters planned for Codex, Claude Code, OpenClaw, Hermes
- **Incremental evolution**: new material merges incrementally; conflicts are recorded, not forcibly resolved

## Current State

The project is in **design phase**. No Python package or implementation exists yet. The execution plan at `docs/superpowers/plans/2026-04-29-human2skill-execution-plan.md` defines 9 implementation tasks covering schemas, profiles, evidence validation, adaptive interview, skill generation, review checks, storage, and a smoke test.

The `zg-strategy-distillation/` skill is an existing, working Claude Code skill for distilling Z哥's investment strategy knowledge. It follows its own governance process (7-step flow, QA review with parallel sub-agents, mandatory contradiction halting).

## Tech Stack (per execution plan)

- **Language**: Python 3.11+
- **Dependencies**: jsonschema >= 4.22.0
- **Test framework**: pytest >= 8.0.0
- **Storage**: local filesystem (JSON schemas, Markdown skills)
- **Package layout**: `src/human2skill/` with `pyproject.toml`
