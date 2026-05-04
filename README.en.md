# Ship of Theseus — AIDE Multiverse Coding Harness

> Korean is the source language. This file is a single-page summary for English readers — see [`README.md`](README.md), [`PHILOSOPHY.md`](PHILOSOPHY.md), and the convention files for full content.

## One-line Definition

A Claude Code skill bundle that **explores a request as a tree of N parallel universes, runs a tournament to pick the winning universe, and guarantees the output can still be called by its originally-intended title.** The *real* differentiating engine is **AIDE Tree (Plan-Tree × Multi-Phase × Tournament × Ensemble Synthesis × Blind Rerun)** — phase 06 plan-tree is the seed, and v0.9.10~v0.9.15 expanded multiverse to phases 02 / 05 / 08 / 11 / 13. *Theseus* is the branding + trust-accumulation metaphor (the potter who breaks and re-throws). 15 phases × 47 conventions × 18 agents are operated by 2 SKILL.md (orchestrator entry + harness source-of-truth).

Entry points: [`theseus-orchestrator`](skills/theseus-orchestrator/SKILL.md) (user entry, HARD-RULE driver) — requires [`theseus-harness`](skills/theseus-harness/SKILL.md) (content source) installed alongside.

## Maturity — Honesty Box (v0.9.15)

> **v0.9.15 = budget-saturation + score-rubric-objectivity milestone.** 47 conventions + 18 agents + 15 phases + 2 domain adapters. Six external simulation-bench applications all hit the *94 plateau* — v0.9.15 attacks the ceiling with *budget ≥ 80% saturation* + *evidence 1:1 self-rating*.
>
> **Progress signals (2026-05-04)**:
> - ✅ Self-evaluation — all self_lint rules PASS / pytest no regression / `self_score = 1.0` / threshold 0.99999 cleared
> - ✅ **livetest 4/4 PASS** (G2/G3/G4/G5) — sandbox sub-claude fresh load + 15-phase artifacts produced
> - ✅ **HARD-RULE 1~9 stabilized** + **Layer 3 deliverable-hurdle supremacy** (memory / convention cannot override)
> - ✅ **6 external simulation-bench applications** — 18.5–44 min wall clock / intervention 0 / sanity 4 PASS
> - ✅ **AIDE multiverse fully expressed** — phase 06 width 3-6 + depth 1-2 + multi-phase to phases 02/05/08/11/13 + per-universe sequenceDiagram + tournament blind rerun + ensemble synthesis default
> - ✅ **94 plateau measured** — v01_cold (v0.9.9) / v091_cold01 (v0.9.12) / v0914_cold01 (v0.9.14) all self-estimate 94 — *content depth layer* alone breaks the ceiling
> - ⏸ **94 → 97+ ceiling-break verification pending** — v0.9.15 budget-saturation + objective rubric not yet validated in cold session.
>
> v1.0 = external maintainer prod adoption + ≥5 external applications + 94 plateau breakthrough.
>
> ⓐ Numbers like `self_lint pass`, `sample_score 1.0`, `threshold 0.99999 cleared` measure **markdown / code-index consistency and example-input scoring of THIS repo** — not whether an LLM agent actually behaves like the prompts say. External bench applications are the proxy for "agent really follows the prompt."
> ⓑ self_lint inspects *markdown text patterns* only. "Phase body contains keyword X" is verified; "implementer agent actually receives `lesson_pack` and avoids forbidden strategies" is verified via bench cold-session retro, not lint.
> ⓒ **Threshold 0.999 / 0.99999 are NOT SLO availability** — they are a 6-dimension weighted average + DIP single hard cap 0.6 + 5 hard caps. Don't read "99.999% reliable" — that's a mis-read.
> ⓓ **The single urgent goal of v0.9.15**: break the 94 plateau via budget 80% saturation (5-8 sprints) × evidence 1:1 self-rating × content-depth lessons.
> ⓔ Self-evaluation is **OS-agnostic**: `bash scripts/self-check.sh` (Linux/Mac) or `scripts\self-check.bat` (Windows) reproduce the same `self_score = 1.0`. cp949 latent bug fixed in v0.2.2 with `scoring/conftest.py` + explicit `encoding="utf-8"` + self_lint C35 guard.
> ⓕ **External pattern adoption methodology — Mirror Principle**: external skills are *blind-spot detection mirrors only*, not a synthesis license. Adopt only on *orthogonal axes* — augment one paragraph in an existing file rather than creating a new one. See [`PHILOSOPHY.md`](PHILOSOPHY.md) "External Pattern Adoption" section.
> ⓖ **Layer 3 deliverable-hurdle supremacy** (v0.9.14): memory rules / conventions / user pre-delegation *cannot override* the deliverable hurdle. v0913_cold01's design-only escape blocked + 003 / v091_cold01's code+execution result generalized.

## Why "AIDE Multiverse" — the Real Engine

Phase 06 plan-tree's result is not a single plan but **a tree of N universes**. Five seeds (domain-first / adapter-first / minimal-subtraction / tdd-topology / strict-layering) + 6 branching axes (process-vs-data / sync-vs-async / centralized-vs-distributed / dynamic-vs-static / push-vs-pull / mutable-vs-immutable) drive *meaning-divergent* universes. plan-reviewer scores each universe via fresh cold-read; tournament picks the winner. v0.9.10 ~ v0.9.15 elevated this from a single-phase trick to a *core differentiator*:

- **v0.9.10** — `aide-tree-symmetry` (per-universe sequenceDiagram mandatory) + `aide-tree-multi-phase` (extends to phases 02/05/08/11/13) + `tournament-blind-rerun` (anonymized re-tournament on threshold miss)
- **v0.9.11** — `interface-first-parallel-impl` (phase 06 interface mandatory + phase 08 sub-agent parallel fan-out)
- **v0.9.12** — `multiverse-impl-fan-out` (universe N all carry real code) + `analytical-bound-cross-validation` + `budget-aware-fallback`
- **v0.9.13** — `ensemble-synthesis-default` (G4+ tournament result is *algorithmic union by default*) + `deep-semantic-intent` + `domain-research-stacking`
- **v0.9.14** — `deliverable-hurdle-supremacy` (Layer 3 hurdle overrides memory/convention)
- **v0.9.15** — `budget-saturation-loop` + `score-rubric-objectivity`

**Why Doctor Strange viewed 14,000,605 futures — go to all of them before deciding.** Converting LLM non-determinism into a *branching engine* is the harness's only differentiating strength.

## Why "Ship of Theseus" — Branding & Trust Accumulation

Can a ship still be called the same ship after every plank has been replaced? It's the *branding + trust-accumulation metaphor*. While AIDE multiverse breaks and merges N universes, **the trust that the output still deserves the originally-intended title must accumulate, not erode**. The *potter's break-and-re-throw* (phase 11 `re-architect` + 6-dimensional trigger + score-timeline regression bisect) is what builds that trust. AIDE multiverse explores forward, the potter re-architects backward — they're complementary.

See [`PHILOSOPHY.md`](PHILOSOPHY.md) for the full pottery-craftsman metaphor, AIDE elevation, and the synthesis of Ralph loop / OhMy series / Ouroboros / Karpathy LLM Wiki / Da Capo.

## When to Use

ⓐ **Recommended (G3+)** — multi-module / FE+BE / unfamiliar domain / long-running refactor needing regression bisect / *external evaluator bench tasks* (auto-escalates to G4).
ⓑ **Mini mode (G2)** — single-module small features. Some phases skipped.
ⓒ **G1 (trivial)** — internal `mini_harness_tbd` modulation, not a hard rejection (v0.5.0 — grades are *internal modulation only*, no entry/reject gate).

See [`examples/`](examples/) for 3 scenarios (evolving-spec / frozen-spec / fix-bug) with actual user input examples for the phase-04 catalog answers.

## 15-Phase Pipeline

| Stage | Phase | Output |
| ----: | ----- | ------ |
| 00 | Naming (G3+) | `naming/00-naming.md` |
| 01 | Intent + mind-map | `intent/01-intent.md` |
| 02 | Doc-review (multi-reviewer multi-phase optional) | `intent/02-intent-review.md` |
| 03 | Cold re-comprehension (parallel framing) | `intent/03-comprehension.md` |
| 04 | User Q&A + stack + Q-D9 + Q-D-DELIVERABLE-MODE + Q-D-BUDGET-MODE | `intent/04-*.md` |
| 05 | Critique (multi-critic multi-phase optional) | `intent/05-critique.md` |
| 06 | **AIDE Plan-Tree** — N-universe tournament (G3-3 / G4-4 / G5-6 + depth 1-2 + ensemble synthesis default) | `plan/{tournament.md, 06-plan.md, candidates/universe-N/}` |
| 07 | Plan re-comprehension | `plan/07-plan-review.md` |
| 08 | Implementation (5-substep TDD + multiverse impl fan-out) | `impl/{08-impl-log.md, 08-test-scope.md}` + code |
| 09 | 7 quality gates + Gate 0 deliverable hurdle (H1~H5) supremacy | `quality/09-quality-gate.md` |
| 10 | Infinite sprint (budget-saturation-loop ≥80% mandatory) | `sprints/NN/` |
| 11 | Regression bisect (4 categories: plan/impl/data/external defect) | `sprints/NN/bisect.md` |
| 12 | theseus-view (skill progress tracking) | `webview/` |
| 13 | interactive-viewer (project output observability) | `interactive-viewer/` |
| 14 | Handoff (score-rubric-objectivity self_estimate + evidence_missing) | `handoff/14-handoff.md` |

## Q-D8 Verification Commands (oh-my-ralph latch)

The most important gate: **phase 04 ends with Q-D8** asking the user to provide bash verification commands (or a `manual_only: true` flag). If neither is supplied, `intent/04-verification.md` carries `entry_blocked: true` and phase 05 (critique) refuses to start with a `SkillEntryError`. See [`conventions/autonomy.md`](skills/theseus-harness/conventions/autonomy.md) §Q-D8.

## Q-D-DELIVERABLE-MODE / Q-D-BUDGET-MODE (v0.9.14 / v0.9.15)

Phase 04 also asks two new questions:

- **Q-D-DELIVERABLE-MODE** — 1=Standalone production (default, all 5 hurdles H1~H5 mandatory) / 2=Integration (existing repo patch, only H1) / 3=Design-only (explicit user ack required, all hurdles waived)
- **Q-D-BUDGET-MODE** — 1=Saturation (default, ≥80% sprint loop) / 2=Quick-stop (early termination on threshold first-try) / 3=Custom budget cap

## Quick Start

```bash
# In a Claude Code session:
/plugin marketplace add https://github.com/whyjp/shipoftheseus
/plugin install shipoftheseus@shipoftheseus

# Then:
/shipoftheseus:theseus-orchestrator <your requirement>   # 15-phase autonomous driver
```

> **`claude plugin install <url>` (direct URL install) does NOT work** — Claude Code's plugin manager requires the marketplace to be registered first.

For local/symlink installs without the plugin manager, see [`INSTALL.md`](INSTALL.md).

## Output Tree

```
.ShipofTheseus/<project_id>/
├── timing/start.json
├── naming/{00-candidates.md, 00-naming.md}
├── intent/{01..05}*.md          (incl. 04-verification.md — Q-D8 latch)
├── plan/{06-plan.md, 07-plan-review.md, tournament.md, candidates/universe-N/}
├── impl/{08-impl-log.md, 08-test-scope.md}
├── code/                          (standalone context — Layer 3 hurdle H1~H5)
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, score.json, unit.json, e2e.json}
├── webview/                       (phase 12 — theseus-view, bun + hono + react)
├── interactive-viewer/            (phase 13 — project output observability)
└── handoff/14-handoff.md          (score-rubric-objectivity self_estimate)
```

## Self-Evaluation (Bootstrapping)

The harness applies its own gates to itself — *what I impose on you, I must impose on me.* See [`BOOTSTRAP.md`](BOOTSTRAP.md).

```bash
bash scripts/self-check.sh        # Linux/Mac
scripts\self-check.bat            # Windows
```

Steps: 60+ self_lint rules → pytest (score-tests + component tests) → sample-input scoring → self-score (threshold 0.99999) → fingerprint chain integrity. Results accumulate in `.ShipofTheseus/theseus-self/` for cross-iteration regression detection.

## Hard Rules (Summary)

ⓐ No phase skipped — even when irrelevant, run it and record "no findings."
ⓑ Phases 03 / 07 are *fresh* `Agent` calls — no shared context.
ⓒ Phase 04 is the *only* user-interrupt point. Sub-delegation Q-D1~Q-D9 + Q-D-DELIVERABLE-MODE + Q-D-BUDGET-MODE must all be answered or phase 05 entry is refused.
ⓓ **Threshold default 0.999** (G3/G4 unified, v0.9.15) — infinite sprint until budget ≥80% used (saturation loop).
ⓔ **DIP is the highest SOLID priority** — single violation hard cap 0.6.
ⓕ Korean Go default for backend, bun + React + TS for frontend.
ⓖ All modules ship `.sh` + `.bat` build scripts, TOML config + `.example`, `docs/` folder, ruff lint/format.
ⓗ Modify-then-discard ordering — preserve intermediate artifacts before they're live.
ⓘ Parallel sub-agents allowed within RAM 50% / 2 concurrent E2E / same-file serial guard.
ⓙ Cumulative wall-clock time always shown in the live report.
ⓚ All artifacts carry frontmatter (`skill_name / version / phase / project_id / fingerprint / prev_fingerprint / produced_at`).
ⓛ The conductor never edits phase outputs by hand — re-run the phase if wrong.
ⓜ **Layer 3 deliverable-hurdle supremacy** — memory / convention / user pre-delegation cannot override H1~H5. Only Q-D-DELIVERABLE-MODE = 3 explicit ack waives.

## Grade System ([`conventions/grades.md`](skills/theseus-harness/conventions/grades.md))

Phase 04's first question (`Q-G1`) confirms the grade after `grade_assess.py` proposes it. **Grades are *internal modulation only* — they do NOT entry/reject. All grades proceed.**

| Grade | When | Internal modulation |
| ----- | ---- | ------------------ |
| **G1** Trivial | one-liner / rename / typo | `mini_harness_tbd` (modulation under design) |
| **G2** Simple | single-module ~100 LOC | Mini (5 phases / 7 conventions / threshold 0.95) |
| **G3** Standard | multi-module single-side | 12-13 phases / 12 conventions / threshold 0.999 |
| **G4** Complex | FE+BE / new domain / SOLID refactor / external bench (default) | Full 15 phases / 26+ conventions / threshold 0.999 |
| **G5** Mission Critical | payments / finance / safety | Full 15 + tight mode / threshold 0.99999 / multiverse width 5-6 + depth 2 |

## License

MIT. See [`LICENSE`](LICENSE).
