# human2skill — Turn someone you know into a reusable perspective advisor

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-132%20passed-brightgreen)](https://github.com/EricArcha/human2skill/actions)
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/EricArcha/human2skill/blob/main/CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![AgentSkills](https://img.shields.io/badge/standard-AgentSkills-orange)](https://agentskills.io)

[中文](README.md)

Take what you know about a real person and distill it into a reusable **perspective advisor Skill**.

This isn't AI impersonation. It takes limited materials, your observations, and rounds of follow-up questions, then assembles them into an installable `SKILL.md`. When you face a problem, you can ask it to look at things the way that person would — through their thinking patterns, expression habits, judgment preferences, and known boundaries.

For example:

```text
You: Review this technical proposal from Li Ming's perspective.
Li Ming's lens: He'd likely ask three questions first:
1. Is this solving the actual top pain point right now?
2. Is there a smaller validation path?
3. If someone picks this up three months later, will they understand
   why it's designed this way?

Based on his preferences, he'd suggest cutting two unnecessary
abstraction layers and moving risk items into the migration plan.
But I don't have enough evidence for his stance on security compliance,
so you'll need to supplement that.
```

## Who is it for?

**Colleagues and collaborators**

Preserve someone's working methods, review style, and decision habits. "That senior colleague left the team, but I still want to run technical proposals through their lens."

**Friends, partners, and family**

Not about manipulating relationships. It's about understanding how someone might receive a message, where misunderstandings might happen, and which judgments lack evidence.

**Mentors, experts, and advisors**

Capture the advice, feedback, and judgment that someone has given you over time. Let it keep providing guidance on new questions.

**Yourself — past or future**

Turn your principles, anti-patterns, long-term goals, and reflections into a Skill. When facing a choice, let a "clearer version of yourself" remind you what you'd actually want.

## What does it produce?

human2skill generates two kinds of artifacts:

```text
outputs/{slug}/
  public_skill/
    SKILL.md                  # Installable, shareable public Skill
    SKILL.first_person.md      # Optional: first-person variant for self-use
  private_evidence/
    source_index.json          # Private material index
    evidence_pack.json         # Structured evidence pack
    distillation.json          # Agent-assisted distillation
    reviews/                   # Quality and privacy reviews
  corpus/                      # Raw text archive (local only, for verification)
  exports/                     # Exports for different hosts
```

The public Skill is lightweight: it keeps only summarized mental models, expression DNA, decision heuristics, anti-patterns, and honest boundaries.

**Private materials stay in the local evidence pack. They are never copied into the distributable `SKILL.md` by default.** This is the key difference between human2skill and other personality-simulation tools.

## It distills "how they think", not "how they sound"

A useful person Skill shouldn't just parrot catchphrases. human2skill focuses on five layers:

| Layer | What it distills |
| --- | --- |
| Mental models | How they break down problems, find key variables, and judge priorities |
| Expression DNA | How they explain, give feedback, push back, comfort, or move discussions forward |
| Decision heuristics | How they make trade-offs with incomplete information |
| Anti-patterns | Patterns they tend to overuse, misjudge, or apply in wrong contexts |
| Honest boundaries | What the evidence can't support — things it won't pretend to know |

That's why the default mode is "perspective advisor", not "I am this person". It tells you which judgments come from evidence and which are low-confidence inferences.

## Quick start

Choose your AI tool:

**Claude Code**

```bash
git clone https://github.com/EricArcha/human2skill.git ~/.claude/skills/human2skill
```

**OpenClaw**

```bash
git clone https://github.com/EricArcha/human2skill.git ~/.openclaw/skills/human2skill
```

Then type **human2skill** to launch. Requires Python 3.11+ — the Agent auto-detects and prompts if setup is needed.

Trigger words (shared across Claude Code and OpenClaw):

- `human2skill`
- `人物蒸馏`
- `创建人物 Skill`
- `更新人物视角`

Once started, the meta-skill guides you through the full process: confirm subject → ingest materials → adaptive interview → build evidence → distill → build Skill → verify → export.

## Roadmap

| Phase | Status |
|------|------|
| P0-P2 Core pipeline (ingest, interview, evidence, distillation, build, review, export) | ✅ Complete |
| Phased workflow + 3 mandatory checkpoints + human-in-the-loop | ✅ Complete |
| 4-layer verification funnel + automated quality check | ✅ Complete |
| P3 Multi-person cross-perspective, public figure corpus, Web UI | 🔜 Planned |

---

## For developers

human2skill is also a Python CLI that powers the meta-skill workflow.

```bash
# Set up dev environment
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# Run tests
.venv/bin/python -m pytest
```

For development details, see [CLAUDE.md](CLAUDE.md). For the governance and rule system, see [docs/GOVERNANCE.md](docs/GOVERNANCE.md). For version history, see [CHANGELOG.md](CHANGELOG.md).

The repo includes three example persons (in the `examples/` directory), each with a complete private evidence pack, public Skill, review reports, and version snapshots.


---

> Created by [Eric](https://github.com/EricArcha) · [human2skill](https://github.com/EricArcha/human2skill)

