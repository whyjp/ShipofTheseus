# Ship of Theseus — Skill Harness Repo

A repository of Claude Code skills built around one central idea: **a feature, like the Ship of Theseus, gets replaced plank by plank until every piece is sound.** The flagship skill, `theseus-harness`, is a recursive multi-agent coding harness that drives a request from raw intent through specification, planning, implementation, and quality-gated test sprints, looping until a target quality score is reached.

## Skills in this repo

| Skill | Purpose |
| --- | --- |
| [`theseus-harness`](skills/theseus-harness/SKILL.md) | End-to-end recursive harness: intent → docs → cross-agent comprehension → clarification → critique → plan → re-plan → implement → quality gates → unit/E2E sprint loop → regression bisect. |

More skills can be added under `skills/<name>/SKILL.md`.

## Installation

### As a Claude Code project skill
```bash
git clone https://github.com/whyjp/shipoftheseus.git
mkdir -p .claude/skills
cp -r shipoftheseus/skills/theseus-harness .claude/skills/
```

Then in a Claude Code session: `/theseus-harness <your request>`.

### As a Claude Code user skill
```bash
mkdir -p ~/.claude/skills
cp -r shipoftheseus/skills/theseus-harness ~/.claude/skills/
```

## Philosophy

See [`PHILOSOPHY.md`](PHILOSOPHY.md) for the design rationale, references to Ralph loop, OhMy series, Ouroboros patterns, and the SOLID/TDD/BDD/DDD/Hexagonal/Clean Architecture lineage that informs the quality gates.

## Layout

```
skills/theseus-harness/
├── SKILL.md                # main orchestrator — Claude reads this first
├── phases/                 # 12 phase docs, one per stage of the harness
├── agents/                 # sub-agent prompt files (one per role)
├── scoring/                # rubric + score.py
└── templates/              # artifact templates (intent/plan/sprint-report)
```

## Artifacts the harness produces

For every run, the harness writes to `.theseus/<run-id>/`:

- `00-intent.md` — extracted intent (what + why + non-goals + constraints)
- `01-intent-review.md` — reviewer's verdict on the intent doc
- `02-independent-comprehension.md` — fresh sub-agent's read of the intent
- `03-clarifications.md` — Q&A with the user
- `04-critique.md` — mis-choices, alternatives, better approaches
- `05-plan.md` — TODO-shaped implementation plan
- `06-plan-review.md` — second pass over the plan
- `07-impl-log.md` — what was built, per module
- `08-quality-gate.md` — SOLID / scope / coverage / correctness checks
- `sprints/NN-report.md` — per-sprint test results, scores, deltas
- `sprints/NN-bisect.md` — when score drops, the bisection findings

## License

MIT. See [`LICENSE`](LICENSE).
