# theseus-harness

Recursive multi-agent coding harness for Claude Code. See [`SKILL.md`](SKILL.md) for the orchestrator instructions.

## Quick reference

- **Phases:** [`phases/`](phases/) — one doc per phase, in order 01 → 12.
- **Sub-agent prompts:** [`agents/`](agents/) — one prompt file per role.
- **Scoring:** [`scoring/rubric.md`](scoring/rubric.md) + [`scoring/score.py`](scoring/score.py).
- **Templates:** [`templates/`](templates/) — intent / plan / sprint-report.

## Install as a project skill

```bash
mkdir -p .claude/skills
cp -r path/to/shipoftheseus/skills/theseus-harness .claude/skills/
```

## Run

In a Claude Code session:

```
/theseus-harness <your feature request>
```

Claude will read `SKILL.md`, kick off Phase 1, and walk the 12 phases. All artifacts land in `.theseus/<run-id>/`.

## Verify the rubric

```bash
python -m pytest skills/theseus-harness/scoring/test_score.py -q
```
