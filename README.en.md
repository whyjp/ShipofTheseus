# Ship of Theseus — Recursive Multi-Agent Coding Harness

> Korean is the source language. This file is a single-page summary for English readers — see [`README.md`](README.md), [`PHILOSOPHY.md`](PHILOSOPHY.md), and the convention files for full content.

## One-line Definition

A Claude Code skill bundle that **guarantees an output can still be called by its originally-intended title — whether you re-assemble or break and re-build it.** 14 phases × 21 conventions × 13 agents are fragmented into 8 decomposition skills + 1 index + 1 flagship single-source-of-truth.

Entry points: [`theseus-orchestrator`](skills/theseus-orchestrator/SKILL.md) (auto-chains 8 sub-skills) or [`theseus-harness`](skills/theseus-harness/SKILL.md) (single call).

## Maturity — Honesty Box (v0.3.0)

> **v0.2.x and v0.3.0-alpha are scaffolding that only passes self-evaluation. 0 external real-project applications to date.**
>
> ⓐ Numbers like `self_lint 36/36 pass`, `sample_score 1.0`, `threshold 0.99999 cleared` measure **markdown / code-index consistency and example-input scoring of THIS repo** — not whether an LLM agent actually behaves like the prompts say.
> ⓑ self_lint inspects *markdown text patterns* only. "Phase 10 body contains `lessons` + `stagnation`" is verified; "implementer agent actually receives `lesson_pack` and avoids forbidden strategies" is not.
> ⓒ **Threshold 0.999 / 0.99999 are NOT SLO availability** — they are a 6-dimension weighted average + DIP single hard cap 0.6 + 5 hard caps. Don't read "99.999% reliable" — that's a mis-read.
> ⓓ **The single urgent goal of v0.3.0**: 1 external real-project application + post-mortem on 4 metrics (interrupts = 0 / 14-phase wall time / intent fidelity / adoption viability). New conventions and tools are frozen until that lands.
> ⓔ Self-evaluation is **OS-agnostic**: `bash scripts/self-check.sh` (Linux/Mac) or `scripts\self-check.bat` (Windows) reproduce the same `self_score = 1.0`. Up to v0.2.1, Windows + Korean locale silently produced 0.8 due to a cp949 latent bug — fixed in v0.2.2 with `scoring/conftest.py` + explicit `encoding="utf-8"` + self_lint C35 guard.

## Why "Ship of Theseus"

The thought experiment: if every plank of a ship is replaced one by one, can it still be called the same ship? In code: phases, sprints, modules are decomposed and re-built — but **the trust that the result still deserves the originally-intended title must accumulate, not erode**. Every gate, score, and regression bisect in this harness exists for that accumulation.

See [`PHILOSOPHY.md`](PHILOSOPHY.md) for the full pottery-craftsman metaphor and the synthesis of Ralph loop, OhMy series, AIDE tree search, and Karpathy's LLM Wiki.

## When to Use

ⓐ **Recommended (G3+)** — multi-module / FE+BE / unfamiliar domain / long-running refactor needing regression bisect.
ⓑ **Rejected (G1)** — one-liner edits, typos, single-function additions. The harness self-rejects via `grade_assess.py` at phase `intent`.
ⓒ **Mini mode (G2)** — single-module small features. Some phases skipped.

See [`examples/`](examples/) for 3 scenarios (evolving-spec / frozen-spec / fix-bug) with actual user input examples for the phase-04 catalog answers.

## 14-Phase Pipeline

| Stage | Phase | Skill | Output |
| ----: | ----- | ----- | ------ |
| 00 | Naming | `theseus-intent` | `naming/00-naming.md` |
| 01–05 | Intent · Mind-map · Cross-comprehension · Interview · Critique | `theseus-intent` | `intent/01..05*.md` |
| 06–07 | TODO DAG · re-comprehension | `theseus-plan` | `plan/06..07*.md` |
| 08 | Module impl (code + tests + build) | `theseus-implement` | `impl/08-impl-log.md` + code |
| 09 | 5 quality gates + Phase V validity | `theseus-quality` | `quality/09-quality-gate.md` |
| 10–11 | Infinite sprint loop + regression bisect + multiverse | `theseus-sprint` | `sprints/NN/{report,inputs,bisect}.*` |
| 12 | bun + hono + react interactive webview (6 tabs) | `theseus-webview` | `webview/` |
| 13 | One-liner summary + score timeline + (autonomous) PR creation | `theseus-handoff` | `handoff/13-handoff.md` |

The flagship [`theseus-harness`](skills/theseus-harness/SKILL.md) is the *content single source of truth*. Decomposition skills define the *shape and interface only*, delegating bodies.

## Q-D8 Verification Commands (v0.3.0, oh-my-ralph latch)

The most important gate: **phase 04 ends with Q-D8** asking the user to provide bash verification commands (or a `manual_only: true` flag). If neither is supplied, `intent/04-verification.md` carries `entry_blocked: true` and phase 05 (critique) refuses to start with a `SkillEntryError`. This is the [oh-my-ralph](https://github.com/team-attention/oh-my-ralph) "Verification Commands or no start" rule, ported into the phase-04 sub-delegation catalog. See [`conventions/autonomy.md`](skills/theseus-harness/conventions/autonomy.md) §Q-D8.

## Quick Start

```bash
# In a Claude Code session:
/plugin marketplace add https://github.com/whyjp/shipoftheseus
/plugin install shipoftheseus@shipoftheseus

# Then:
/theseus-orchestrator <your requirement>     # auto-chains 14 phases
/theseus-harness     <your requirement>      # single source of truth
/theseus-<sub-skill> --from <dir>            # resume from existing artifacts
```

> **`claude plugin install <url>` (direct URL install) does NOT work** — Claude Code's plugin manager requires the marketplace to be registered first. The two commands above are the standard.

For local/symlink installs without the plugin manager, see [`INSTALL.md`](INSTALL.md).

## Output Tree

```
.ShipofTheseus/<project_id>/
├── timing/start.json
├── naming/00-naming.md
├── intent/01..05*.md          (incl. 04-verification.md — Q-D8 latch)
├── plan/06..07*.md
├── impl/08-impl-log.md
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, score.json, unit.json, e2e.json}
├── webview/                   (bun + hono + react)
└── handoff/13-handoff.md
```

## Self-Evaluation (Bootstrapping)

The harness applies its own gates to itself — *what I impose on you, I must impose on me.* See [`BOOTSTRAP.md`](BOOTSTRAP.md).

```bash
bash scripts/self-check.sh        # Linux/Mac
scripts\self-check.bat            # Windows
```

Steps: 36 self_lint checks → pytest (12 score-tests + 87 component tests) → sample-input scoring → self-score (threshold 0.99999) → fingerprint chain integrity. Results accumulate in `.ShipofTheseus/theseus-self/` for cross-iteration regression detection.

## Hard Rules (Summary)

ⓐ No phase skipped — even when irrelevant, run it and record "no findings."
ⓑ Phases 03 / 07 are *fresh* `Agent` calls — no shared context.
ⓒ Phase 04 is the *only* user-interrupt point. Sub-delegation Q-D1~Q-D8 must all be answered or phase 05 entry is refused.
ⓓ **Threshold 0.999** — infinite sprint until met, no cap. User ack only on regression (and Q-D1 answer determines whether even that auto-applies).
ⓔ **DIP is the highest SOLID priority** — single violation hard cap 0.6.
ⓕ Korean Go default for backend, bun + React + TS for frontend.
ⓖ All modules ship `.sh` + `.bat` build scripts, TOML config + `.example`, `docs/` folder.
ⓗ Modify-then-discard ordering — preserve intermediate artifacts before they're live.
ⓘ Parallel sub-agents allowed within RAM 50% / 2 concurrent E2E / same-file serial guard.
ⓙ Cumulative wall-clock time always shown in the live report.
ⓚ All artifacts carry frontmatter (`skill_name / version / phase / project_id / fingerprint / prev_fingerprint / produced_at`).
ⓛ The conductor never edits phase outputs by hand — re-run the phase if wrong.

## Grade System ([`conventions/grades.md`](skills/theseus-harness/conventions/grades.md))

Phase 04's first question (`Q-G1`) confirms the grade after `grade_assess.py` proposes it.

| Grade | When | Harness behavior |
| ----- | ---- | ---------------- |
| **G1** Trivial | one-liner / rename / typo | **Reject harness call**, recommend simple response |
| **G2** Simple | single-module ~100 LOC | Mini (5 phases / 7 conventions / threshold 0.95) |
| **G3** Standard | multi-module single-side | 12 phases / 12 conventions / threshold 0.97 |
| **G4** Complex | FE+BE / new domain / SOLID refactor (default) | Full 14 phases / 26 conventions / threshold 0.999 |
| **G5** Mission Critical | payments / finance / safety | Full 14 + tight mode / threshold 0.99999 |

## License

MIT. See [`LICENSE`](LICENSE).
