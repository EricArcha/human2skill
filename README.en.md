# human2skill

[中文](README.md)

human2skill turns what you know about a real person into a reusable **perspective advisor Skill**.

It is not an impersonation tool. It takes limited private material, your observations, and adaptive interview answers, then turns them into an installable `SKILL.md` that can reason from that person's likely mental models, expression patterns, decision habits, and honest boundaries.

Example:

```text
You: Review this technical proposal from Li Ming's perspective.
Li Ming perspective advisor: He would likely start with three questions:
1. Is this solving the most painful problem right now?
2. Is there a smaller validation path?
3. Will someone understand why this design exists three months from now?

Based on his usual preferences, he would probably remove two unnecessary abstraction layers
and document the migration risks. I do not have enough evidence about his security and
compliance tradeoffs, so that part needs more source material.
```

## When Is It Useful?

**Colleagues and collaborators**

Preserve someone's working style, review taste, and decision habits. For example: "A senior teammate left, but I still want to check designs through their lens."

**Friends, partners, and family**

Not to manipulate relationships, but to understand how someone might receive a message, where misunderstandings may happen, and where the evidence is too thin.

**Mentors, experts, and advisors**

Turn repeated advice, feedback, and judgment patterns into a Skill that can help with new questions.

**Yourself and your future self**

Capture your principles, recurring mistakes, long-term goals, and retrospective lessons, then ask a clearer version of yourself for reminders.

## What Does It Produce?

human2skill produces two layers:

```text
people/{slug}/
  public_skill/
    SKILL.md                  # installable, shareable public Skill
    variants/
      advisor/SKILL.md        # default: perspective advisor
      first_person/SKILL.md   # optional: first-person variant for personal use
  private_evidence/
    source_index.json         # private source index
    evidence_pack.json        # structured evidence pack
    distillation.json         # agent-assisted distillation payload
    reviews/                  # quality and privacy review reports
  exports/
    codex/SKILL.md            # host-specific exported Skill
```

The public Skill is lightweight. It contains summarized mental models, expression DNA, decision heuristics, anti-patterns, and honest boundaries.

Private material stays in the local evidence pack and is not copied into the distributable `SKILL.md` by default. This separation is the core difference between human2skill and many "persona simulation" workflows.

## It Distills How Someone Thinks

A useful perspective Skill should not merely repeat catchphrases. human2skill focuses on five layers:

| Layer | What it captures |
| --- | --- |
| Mental models | How this person breaks down problems and chooses priorities |
| Expression DNA | How they explain, push back, comfort, review, or move discussions forward |
| Decision heuristics | How they make tradeoffs under incomplete information |
| Anti-patterns | Where their style may overfit, fail, or become less useful |
| Honest boundaries | What the Skill does not know enough to infer |

The default output is a perspective advisor, not "I am this person." It should tell you what is evidence-backed and what is low-confidence inference.

## Quick Start

Pick your AI tool:

**Claude Code**

```bash
cp -r exports/claude-code ~/.claude/skills/human2skill
```

Then type:

```text
human2skill
```

**OpenClaw**

```bash
cp -r exports/openclaw ~/.openclaw/skills/human2skill
```

Then type:

```text
human2skill
```

Trigger phrases:

- `human2skill`
- `人物蒸馏`
- `创建人物 Skill`
- `更新人物视角`

The meta-skill will guide you through choosing a profile, providing source material, answering adaptive interview questions, building evidence, generating a Skill, reviewing it, and exporting it.

For the detailed meta-skill flow, see [human2skill-meta/README.md](human2skill-meta/README.md).

## Example Use Case

Suppose you want to create a perspective advisor for a colleague named Li Ming.

You can provide:

- Technical proposals or review comments written by him.
- Meeting notes.
- Your observations about his working style.
- Interview answers such as "How does he make deadline tradeoffs?"

human2skill can turn that into:

- Mental model: "Break the problem down before choosing technology."
- Expression DNA: "Affirm the useful part first, then give improvement suggestions."
- Decision heuristic: "Move fast on reversible decisions; invite review for irreversible ones."
- Anti-pattern: "May over-architect simple problems."
- Honest boundary: "No evidence about non-work relationships, so do not infer private behavior."

Then you can ask:

```text
Use Li Ming's perspective to review whether this PR explanation is clear enough.
```

```text
If Li Ming reviewed this technical design, which assumptions would he challenge first?
```

```text
Would this feedback sound too harsh to Li Ming? Check it against his communication preferences.
```

Sample projects:

- [examples/colleague-li-ming](examples/colleague-li-ming)
- [examples/relationship-chen-yu](examples/relationship-chen-yu)
- [examples/self-future-me](examples/self-future-me)

## Why Evidence Packs?

Private-person Skills can easily fail in three ways:

1. **Overconfidence**: too little material, but the Skill sounds certain.
2. **Privacy leakage**: raw chats, social posts, or work documents end up in the public Skill.
3. **Impersonation**: the Skill says "I am this person" and blurs the boundary.

human2skill uses a local evidence pack to keep this under control:

- Claims should trace back to evidence or interview answers.
- Weak evidence lowers confidence or becomes an honest boundary.
- Public Skills avoid raw private material.
- Review and export gates block unsafe or low-quality outputs.

## Developer Notes

human2skill is also a Python CLI that powers the meta-skill workflow. The current implementation targets personally known people: colleagues, collaborators, friends, family members, mentors, experts, and self/future-self use cases. It is not designed for impersonating public figures.

### What Is Implemented

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

### Repository Layout

```text
src/human2skill/           Python package and CLI implementation
src/human2skill/schemas/   Bundled JSON Schemas
src/human2skill/templates/ Bundled profile and Skill templates
tests/                     Pytest suite
examples/                  Generated sample people and exported skills
exports/                   Ready-to-install meta-skill packages for each host
docs/                      Product, architecture, quality, and planning docs
human2skill-meta/          Meta-skill documentation
zg-strategy-distillation/  Existing reference skill kept in this repository
```

### Install For Development

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

### CLI Flow

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

Inspect the review JSON:

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

### Programmatic Use

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

### Quality And Privacy Gates

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

### Development

Run the full suite:

```bash
.venv/bin/python -m pytest -q
```

Build a wheel:

```bash
.venv/bin/python -m pip wheel . -w /tmp/human2skill-wheel --no-deps
```

The wheel should contain bundled schemas and templates from `src/human2skill/schemas/` and `src/human2skill/templates/`.

### Known Limits

- Distillation synthesis is still agent-assisted.
- The reviewer is deterministic but heuristic; it enforces thresholds, not semantic omniscience.
- The CLI `review` command supports `--variant`; without it, it preserves backward-compatible latest-file behavior.
- There is no remote service, database, or UI; state is local filesystem JSON and Markdown.
