# Install human2skill

## Meta-skill users

Install the meta-skill to use `/human2skill` in your AI tool:

```bash
# Claude Code (global, all projects)
git clone https://github.com/EricArcha/human2skill.git ~/.claude/skills/human2skill

# OpenClaw
git clone https://github.com/EricArcha/human2skill.git ~/.openclaw/skills/human2skill
```

Then type **human2skill** in Claude Code or OpenClaw to launch.

The meta-skill requires Python 3.11+ for its CLI tools. On first run, the Agent will check if `human2skill` is available and prompt you if setup is needed.

## Developers

```bash
git clone https://github.com/EricArcha/human2skill.git
cd human2skill
make install
make test
```

---

> Created by [Eric](https://github.com/EricArcha) · [human2skill](https://github.com/EricArcha/human2skill)
