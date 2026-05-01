---
name: theseus-harness
description: Recursive multi-agent coding harness for non-trivial features. Drives a request from raw intent → spec → cross-agent comprehension → user clarification → critique → plan → re-plan → implementation → quality gates → unit/E2E sprint loop until a quality score ≥ 0.9, with regression-bisect when scores drop. Use when the user asks for a feature involving multiple modules, frontend + backend, or anything where unclear intent + insufficient testing would cause real harm. Skip for trivial one-line edits.
---

# theseus-harness — Recursive Coding Harness

You are the **conductor** of this harness. You do *not* do the work yourself — you spawn specialized sub-agents (via the `Agent` tool) and feed their artifacts forward. Every artifact lives under `.theseus/<run-id>/` so the run is fully reproducible and bisectable.

## Pre-flight (do this once)

1. Generate a run id: `RUN_ID=$(date +%Y%m%d-%H%M%S)-$(echo "$REQUEST" | sha1sum | cut -c1-6)`.
2. Create `.theseus/$RUN_ID/`, `.theseus/$RUN_ID/sprints/`.
3. Write the user's raw request to `.theseus/$RUN_ID/00-request.txt`.
4. Use `TodoWrite` to mirror the 12 phases below as todos. Mark each `in_progress` before invoking, `completed` after the artifact is written and you have read it.

## The 12 phases

Each phase has its own doc under [`phases/`](phases/) describing the inputs, the sub-agent to spawn, the output artifact, and the success criterion. **Read the phase doc immediately before invoking the phase** — do not guess.

| # | Phase | Phase doc | Sub-agent prompt |
| - | ----- | --------- | ---------------- |
| 1 | Intent extraction | [`phases/01-intent.md`](phases/01-intent.md) | [`agents/intent-extractor.md`](agents/intent-extractor.md) |
| 2 | Document review | [`phases/02-document.md`](phases/02-document.md) | [`agents/doc-reviewer.md`](agents/doc-reviewer.md) |
| 3 | Independent comprehension | [`phases/03-independent-comprehension.md`](phases/03-independent-comprehension.md) | [`agents/independent-comprehender.md`](agents/independent-comprehender.md) |
| 4 | Clarification dialogue | [`phases/04-clarify.md`](phases/04-clarify.md) | [`agents/clarifier.md`](agents/clarifier.md) |
| 5 | Critique & alternatives | [`phases/05-critique.md`](phases/05-critique.md) | [`agents/critic.md`](agents/critic.md) |
| 6 | Plan (TODO-shaped) | [`phases/06-plan.md`](phases/06-plan.md) | [`agents/planner.md`](agents/planner.md) |
| 7 | Plan recursion (re-plan) | [`phases/07-plan-recursion.md`](phases/07-plan-recursion.md) | [`agents/plan-reviewer.md`](agents/plan-reviewer.md) |
| 8 | Implementation | [`phases/08-implement.md`](phases/08-implement.md) | [`agents/implementer.md`](agents/implementer.md) |
| 9 | Quality gates | [`phases/09-quality-gates.md`](phases/09-quality-gates.md) | [`agents/quality-gate.md`](agents/quality-gate.md) |
| 10 | Test sprint loop | [`phases/10-test-loop.md`](phases/10-test-loop.md) | [`agents/tester.md`](agents/tester.md) |
| 11 | Regression bisect | [`phases/11-regression-bisect.md`](phases/11-regression-bisect.md) | [`agents/regression-analyst.md`](agents/regression-analyst.md) |
| 12 | Handoff & summary | [`phases/12-handoff.md`](phases/12-handoff.md) | (no sub-agent — you do this) |

## Hard rules

1. **No phase may be skipped.** If a phase seems unnecessary, run it anyway and let the sub-agent record "no findings" — the audit trail matters more than five minutes saved.
2. **Phases 3 and 7 must use a *fresh* `Agent` invocation** (no shared context). The whole point is independent comprehension. Pass them only the prior artifact, not your reasoning about it.
3. **Phase 4 (clarification) is a hard checkpoint with the user.** Use `AskUserQuestion`. If the user does not respond, halt — do not assume.
4. **Every implementation module must ship with mocks.** A module without a fakeable port fails Phase 9 even if its tests pass.
5. **Backend and frontend are scored separately.** A feature that's solid on one side and untested on the other fails Phase 10.
6. **Score ≥ 0.9 to exit.** See [`scoring/rubric.md`](scoring/rubric.md). The score is computed by [`scoring/score.py`](scoring/score.py) — no eyeball estimates.
7. **Score-drop triggers Phase 11 immediately**, before any further implementation. The bisect agent must surface the offending diff or the loop is halted for human review.
8. **You are not allowed to edit artifacts written by sub-agents.** If an artifact is wrong, re-run the phase. Edits destroy provenance.

## The sprint loop (Phase 10 detail)

```
sprint_n = 1
while True:
    run unit tests (backend) + unit tests (frontend) + E2E
    score = score.py(rubric, results, prior_sprint)
    write sprints/{sprint_n:02d}-report.md
    if score >= 0.9:
        break
    if sprint_n > 1 and score < prior_score - 0.05:
        run Phase 11 (regression bisect) → sprints/{sprint_n:02d}-bisect.md
        require human ack before continuing
    spawn implementer with the failing tests + delta from rubric
    sprint_n += 1
    if sprint_n > 8:  # safety cap
        halt and ask user for direction
```

## When to invoke this skill

- Multi-module features (frontend + backend, or service + database).
- Anything where ambiguity in intent would cause meaningful rework.
- Refactors that touch SOLID boundaries.
- New domains where the ubiquitous language hasn't been settled.

## When *not* to invoke this skill

- One-line bug fixes. Just fix it.
- Renames and mechanical refactors.
- Spike code where the user has explicitly said "throwaway."

## See also

- [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) — design rationale and lineage.
- [`scoring/rubric.md`](scoring/rubric.md) — what gets scored and how.
- [`templates/`](templates/) — artifact templates the sub-agents fill in.
