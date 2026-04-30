# human2skill

[中文说明](README.zh-CN.md)

human2skill distills limited private source material and adaptive interviews about a real person into a reusable "perspective advisor" Skill. The generated public `SKILL.md` is backed by a private evidence pack, while raw private material stays outside distributable outputs.

The current implementation targets personally known people: colleagues, collaborators, friends, family members, mentors, experts, and self/future-self use cases. It is not designed for impersonating public figures.

## What Is Implemented

The merged P0-P2 system includes:

- Project intake for a person directory under `people/{slug}`.
- Source ingestion for `.txt`, `.md`, and text-extractable `.pdf` files.
- Profile presets for `colleague`, `relationship`, `mentor`, and `self`.
- Gap-driven interview question selection.
- Evidence pack builder APIs for evidence, claims, and conflicts.
- Agent-assisted distillation validation through `distillation.json`.
- Advisor and first-person skill variant rendering.
- Structured review reports with hard failures and score thresholds.
- Variant-specific export gates for supported hosts.
- Install helper for exported skills.
- Version snapshots, changelog helpers, and restore support.
- Example projects under `examples/`.
- 132 pytest tests covering the current P0-P2 flow.

Important boundary: human2skill does not fully synthesize a person's perspective from raw material by itself. A host agent still prepares `private_evidence/distillation.json`; Python owns validation, rendering, review, export, install, and durable state.

## Repository Layout

```text
src/human2skill/          Python package and CLI implementation
src/human2skill/schemas/  Bundled JSON Schemas
src/human2skill/templates/ Bundled profile and skill templates
tests/                    Pytest suite
examples/                 Generated sample people and exported skills
docs/                     Product, architecture, quality, and planning docs
human2skill-meta/         Meta-skill documentation
zg-strategy-distillation/ Existing reference skill kept in this repository
```

Local-only directories such as `.venv/`, `.pytest_cache/`, `.worktrees/`, `build/`, `dist/`, `.claude/`, and `references/repos/` are ignored.

## Install

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
.venv/bin/pip install ".[dev]"
```

After installation, the console command is:

```bash
human2skill --help
```

For active source editing, tests also work directly from the checkout because `pyproject.toml` configures `src` as pytest's import path. Reinstall the package after CLI or package metadata changes.

## CLI Flow

Create a person project:

```bash
human2skill create \
  --root workspace \
  --slug li-ming \
  --name "李明" \
  --profile colleague \
  --relationship coworker \
  --use-case "work review and collaboration" \
  --voice-mode both
```

Ingest private source material:

```bash
human2skill ingest \
  --root workspace \
  --slug li-ming \
  --file notes/li-ming.md
```

Ask for the next gap-driven interview question:

```bash
human2skill question \
  --root workspace \
  --slug li-ming \
  --profile colleague \
  --perspective observer_answer \
  --turn 1
```

Prepare `workspace/people/li-ming/private_evidence/distillation.json` with a host agent, then build:

```bash
human2skill build --root workspace --slug li-ming
```

Inspect the latest review JSON:

```bash
human2skill review --root workspace --slug li-ming --variant advisor
```

Export a reviewed variant:

```bash
human2skill export \
  --root workspace \
  --slug li-ming \
  --host codex \
  --variant advisor
```

Install an exported skill into a target skills directory:

```bash
human2skill install \
  --export workspace/people/li-ming/exports/codex \
  --target ~/.codex/skills \
  --name li-ming-perspective
```

Supported hosts are defined in `src/human2skill/constants.py`: `codex`, `claude-code`, `openclaw`, and `hermes`.

## Programmatic Use

```python
from pathlib import Path

from human2skill.flow import create_project_person, build_from_distillation
from human2skill.ingest import ingest_file
from human2skill.exporter import export_skill

root = Path("workspace")

base = create_project_person(
    root=root,
    slug="li-ming",
    display_name="李明",
    profile_type="colleague",
    relationship_to_user="coworker",
    use_case="work review and collaboration",
    voice_mode="advisor",
)

ingest_file(base, Path("notes/li-ming.md"))

# distillation is agent-assisted and loaded from your own JSON payload.
# result = build_from_distillation(base, distillation)
# export_dir = export_skill(base, host="codex", variant="advisor")
```

## Quality And Privacy Gates

Generated skills are perspective advisors, not impersonations. Public skill output must include disclaimers and honest boundaries.

Structured review blocks export when:

- The skill claims to be the person.
- Required disclaimers or honest boundaries are missing.
- Raw private markers appear in public output.
- Unsupported high-confidence claims are present.
- Blocking conflicts remain unresolved.
- Any required score threshold is below the pass line.

Export is variant-specific: exporting `advisor` requires an advisor review, and exporting `first_person` requires a first-person review.

Conflict semantics:

- `halt_for_review` blocks build/review flow.
- `keep_both_with_scope` and `mark_low_confidence` are accepted conflict resolutions and do not fail review by themselves.

## Examples

The repository includes sample people:

- `examples/colleague-li-ming`
- `examples/relationship-chen-yu`
- `examples/self-future-me`

Each example includes private evidence artifacts, generated public skills, review reports, exports, and version snapshots. These are fixtures for understanding the durable file layout and for regression tests.

## Development

Run the full suite:

```bash
.venv/bin/python -m pytest -q
```

Build a wheel:

```bash
.venv/bin/python -m pip wheel . -w /tmp/human2skill-wheel --no-deps
```

The wheel should contain bundled schemas and templates from `src/human2skill/schemas/` and `src/human2skill/templates/`.

## Known Limits

- Distillation synthesis is still agent-assisted.
- The reviewer is deterministic but heuristic; it enforces thresholds, not semantic omniscience.
- The CLI `review` command supports `--variant`; without it, it preserves backward-compatible latest-file behavior.
- There is no remote service, database, or UI; state is local filesystem JSON and Markdown.
