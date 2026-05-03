# human2skill

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-2.3.0-blue)](https://github.com/EricArcha/human2skill/blob/main/CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![skills.sh](https://skills.sh/b/EricArcha/human2skill)](https://skills.sh/EricArcha/human2skill)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-orange)](https://claude.ai/code)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-orange)](https://openclaw.ai)

[中文](README.md)

**They're leaving. Their way of thinking doesn't have to.**

You know this person — through chat logs, meeting observations, problems solved together. Give what you have to human2skill. It won't impersonate them. It will ask questions you hadn't thought of, then structure everything into an installable "perspective advisor."

Next time you need their judgment, ask it to help you see from a different angle.

> You: Help me review this technical proposal through Li Ming's lens.
>
> Li Ming Perspective Advisor:
> He'd likely ask three questions first:
> 1. Is this solving the actual top pain point?
> 2. Is there a smaller validation path?
> 3. Will someone understand why this was designed this way in three months?
>
> Based on his preferences, he'd suggest cutting two unnecessary abstraction layers
> and documenting risks in the migration plan.
> **But I don't have enough evidence to judge how he'd handle compliance trade-offs —
> you'll need to supplement here.**

It's not Li Ming. But it remembers how he thought.

---

## Table of Contents

- [Try it in 5 minutes](#try-it-in-5-minutes)
- [The 20 Questions experience](#the-20-questions-experience)
- [What problems does this solve?](#what-problems-does-this-solve)
- [How is this different?](#how-is-this-different)
- [What does it distill?](#what-does-it-distill)
- [What you get](#what-you-get)
- [See actual outputs](#see-actual-outputs)
- [Quick Start](#quick-start)
- [Roadmap](#roadmap)
- [For Developers](#for-developers)

---

## Try it in 5 minutes

```text
1. npx skills add EricArcha/human2skill
2. In Claude Code, type /human2skill Q20
3. Answer 15-20 minutes of questions (type done to exit anytime)
4. Get an installable perspective advisor Skill
```

No documents needed. No prompt writing. Just sit down and answer questions.

---

## The 20 Questions Experience

This is human2skill's most distinctive interaction. Not a rigid questionnaire — an **adaptive structured interview**. The system evaluates information coverage across 10 dimensions, probes gaps, and digs deeper into blind spots.

Questions adapt to the relationship type:

**Creating a Skill for a colleague:**

> In your collaboration, what area of judgment or capability makes you think "this is where they're most reliable"? Can you give a specific example?

**Creating a Skill for a friend:**

> What's one trait or way of handling things that's left the deepest impression on you in this relationship?

**Creating a Skill for yourself:**

> Looking back at your major decisions, what values have consistently stayed at the top of your priority list? Have you ever sacrificed one value for another?

Coverage updates after every response.

```text
--- Question 12/20 ---
Under what conditions do they push forward, wait, say no, or change their mind?

> [your answer...]

--- Question 13/20 ---
What practices, habits, or ways of thinking do they most dislike or avoid?
Any counterexamples?
```

When 20 rounds are spent or coverage is sufficient, you hit **Checkpoint A**:

```text
⛔ Checkpoint A — Coverage Review
Dimensions covered: 6/10 ≥ medium | Honest boundaries: documented
Gaps: anti_patterns, evaluation_scenarios
Status: ✅ Sufficient to proceed to distillation
```

Your answers become structured evidence, then enter the distillation pipeline. Zero code required.

---

## What problems does this solve?

These aren't feature descriptions. These are situations you might recognize.

**"They left the company."**

A senior colleague is gone. Their review instincts, technical intuition, their sense of "that's over-engineering" — none of this lives in documentation. You have scattered chat logs, hazy memories of their code reviews. human2skill turns limited materials into a perspective advisor you can consult anytime.

**"I keep misreading them."**

Friend, partner, family — you think you're communicating clearly, but their reactions keep surprising you. What you lack isn't good intentions. It's a reference model for "how would they likely receive this?" human2skill turns your observations into a structured perspective map, so you can shift angles before you speak.

**"Great advice, terrible recall."**

Your mentor gave you dozens of insights, but when a new situation arises, all you remember is a vague "they said something about this..." Your notes are buried. Chat logs don't search well. human2skill distills the judgment patterns behind the advice — not repeating their words, but applying their thinking framework to new problems.

**"I know what I should do. I just don't do it."**

Your principles are in your journal. Your long-term goals are on the wall. But in the moment, emotion overrides reason. What you need isn't just a "clearer version of yourself" — it's a perspective reference you can invoke when choices get hard. One that remembers what you decided when you were calm.

---

## How is this different?

If any of these options already cover your needs, use them. human2skill is for when you want **structure, evidence, and honest boundaries**.

| Alternative | What it does | Why human2skill is different |
|-------------|-------------|------------------------------|
| **Custom GPT / system prompt** | Upload docs + write a prompt | No quality control, no evidence grading. Prompts confabulate confidently in gaps. human2skill labels "insufficient evidence" |
| **character.ai and roleplay tools** | "Chat with anyone" impersonation | human2skill is a perspective advisor, not an impersonator. It never says "I am this person." It says "I don't know" when it doesn't |
| **Taking notes / journaling** | Record observations and thoughts | Static records. human2skill turns observations into an interactive advisor — applying distilled patterns to new problems |
| **Notion / personal wiki** | Archive someone's ideas and behaviors | Descriptive — records "what is." human2skill is generative — "what would this person likely think about X?" |
| **Hand-written prompt** | "Act as a rigorous engineer who..." | Written from memory. No evidence pack, no audit trail, no verification funnel. Quality depends entirely on what you recall right now |
| **nuwa-skill** | General Skill distillation methodology | nuwa is a methodological framework defining universal principles for distilling skills. human2skill is a vertical implementation focused exclusively on "person perspective" — with profile system, adaptive interviews, privacy separation, and evidence grading |
| **colleague-skill** | Engineering collaboration pattern reference | colleague-skill is a specific engineering-scenario skill example. human2skill is the **meta-tool that generates this kind of person skill** — it doesn't give engineering advice, it helps you build your own "colleague-skill" |

---

## What does it distill?

human2skill doesn't care about "does it sound like them." It cares about **thinking structure**.

| Layer | What it extracts | Example (from sample persons) |
|-------|-----------------|-------------------------------|
| **Mental models** | How this person breaks down problems, finds key variables, weighs priorities | "Problem decomposition first — fully break down the problem before technology choices, validate assumptions with the simplest approach" |
| **Expression DNA** | How they explain, give feedback, disagree, comfort, or move discussions forward | "Acknowledge then improve — when reviewing others' work, first point out what's done well, then offer suggestions" |
| **Decision heuristics** | How they make trade-offs with incomplete information | "Reversible decisions: move fast. Irreversible decisions: pull in more people and review thoroughly" |
| **Anti-patterns** | Patterns they overuse, misapply, or where they fall short | "Using tactical busyness to avoid the strategically hard but important thing" |
| **Honest boundaries** | What there isn't enough evidence for — and refusing to pretend otherwise | "Non-work scenarios: insufficient evidence — all evidence comes from workplace, no inference on social contexts" |

Every conclusion is tagged with its evidence tier:

| Tier | Source | Meaning |
|------|--------|---------|
| **L1** | Direct quote / behavior record | Backed by direct evidence |
| **L2** | Observer report | Second-hand observation or feedback |
| **L3** | Model inference | Reasonable pattern-based inference, lower confidence |

**Most AI personality tools fabricate in evidence gaps. human2skill labels them.** This is the fundamental difference.

---

## What you get

One folder. Two halves.

```text
outputs/{slug}/
├── public_skill/
│   ├── SKILL.md                  # ← Shareable, installable perspective advisor
│   └── SKILL.first_person.md     # ← Personal first-person variant
├── private_evidence/             # ← Stays local, full traceability, never distributed
│   ├── evidence_pack.json        #    Structured evidence pack
│   ├── distillation.json         #    Distillation results
│   └── reviews/                  #    Quality review reports
├── corpus/                       # ← Source text archive, for verification
└── exports/                      # ← Multi-host exports (Claude Code / OpenClaw / …)
```

The **public** `SKILL.md` can be shared, installed in Claude Code, sent to a friend. They get the distilled lens — mental models, decision heuristics, expression preferences, honest boundaries.

The **private** evidence pack stays local. They will never see your raw materials.

This is the most important difference between human2skill and other "personality simulation" tools.

---

## See actual outputs

The repo contains three fictional example persons, each with complete evidence packs, public Skills, and review reports. Browse the full outputs:

| Example | Type | Most distinctive distillation |
|---------|------|------------------------------|
| [Li Ming's Lens](examples/colleague-li-ming/public_skill/SKILL.md) | Colleague | "Reversible decisions: move fast. Irreversible: review thoroughly" |
| [Chen Yu's Lens](examples/relationship-chen-yu/public_skill/SKILL.md) | Relationship | "Being seen > Being solved" |
| [Future Me Lens](examples/self-future-me/public_skill/SKILL.md) | Self | "Using tactical busyness to avoid the strategically hard thing" |

Run it yourself: type `/human2skill`. In 15 minutes, you'll have one too.

---

## Quick Start

### One-click install (recommended)

```bash
npx skills add EricArcha/human2skill
```

### Manual install

**Claude Code**

```bash
git clone https://github.com/EricArcha/human2skill.git ~/.claude/skills/human2skill
```

**OpenClaw**

```bash
git clone https://github.com/EricArcha/human2skill.git ~/.openclaw/skills/human2skill
```

### Python CLI (optional)

```bash
pip install git+https://github.com/EricArcha/human2skill.git
```

Then use any of these triggers:

| Trigger | Effect |
|---------|--------|
| `/human2skill Q20` | **Shortcut**: jump straight into 20 Questions |
| `human2skill` | Standard entry: full Phase 0-5 workflow |
| `人物蒸馏` | Chinese trigger |
| `创建人物 Skill` | Chinese trigger |
| `更新人物视角` | Incremental update for existing Skill |

Requires Python 3.11+. The Agent auto-detects and prompts for installation on first use.

---

## Roadmap

- [x] Core pipeline (intake, interview, evidence, distillation, build, review, export)
- [x] Phased workflow + 3 mandatory checkpoints + human-in-the-loop
- [x] 4-layer verification funnel + automated quality checks (7 items)
- [x] 20-question interactive interview + coverage review
- [x] Immersive first-person templates + evidence citation system
- [x] 4 profile types (colleague / relationship / mentor / self)
- [x] Multi-host export (Claude Code / OpenClaw / Codex / Hermes)
- [x] 3 complete fictional example persons
- [ ] Multi-persona cross-perspective
- [ ] Public figure corpus library
- [ ] Web UI

---

## For Developers

human2skill is also a Python CLI — the underlying tool for the workflow.

```bash
# Set up dev environment
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# Run tests
.venv/bin/python -m pytest
```

See [CLAUDE.md](CLAUDE.md) for development details, [GOVERNANCE.md](GOVERNANCE.md) for rules and governance, [CHANGELOG.md](CHANGELOG.md) for version history.

The repo includes three example persons (`examples/` directory), each with complete private evidence, public Skills, review reports, and version snapshots.

---

> Created by [Eric](https://github.com/EricArcha) · [human2skill](https://github.com/EricArcha/human2skill)
