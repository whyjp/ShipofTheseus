# Phase 11 — Regression Bisect

## Goal

When a sprint's score drops > 0.05 from the previous sprint, find the offending change *before* any further implementation. The Ship of Theseus has a bad plank — replace it before laying more.

## Trigger

Phase 10's loop calls this whenever `score(sprint_n) < score(sprint_n-1) - 0.05`. Manual trigger: `score.py --bisect <run-id> <sprint>`.

## Inputs

- `.theseus/$RUN_ID/sprints/N-1-report.md` (last good)
- `.theseus/$RUN_ID/sprints/N-report.md` (the regression)
- The git diff between the two sprints' commits (each sprint commits a checkpoint — see `agents/tester.md`).
- Failing test names + error messages from sprint N.

## Sub-agent

Spawn `Agent(subagent_type="general-purpose")` with [`../agents/regression-analyst.md`](../agents/regression-analyst.md). The analyst is forbidden from editing code — it only diagnoses.

## Output

`.theseus/$RUN_ID/sprints/NN-bisect.md`:

- **What dropped** — which sub-scores dropped, by how much.
- **What changed** — diff summary between sprint N-1 and N (files, functions, lines).
- **Hypothesis** — single most likely root cause, named at the function-or-line level.
- **Evidence** — at least one failing test traced to the hypothesized change.
- **Counter-hypotheses** — at least one alternative explanation, with why it's less likely.
- **Recommendation** — one of:
  - `revert <commit-or-file>` (precise revert of the offending plank).
  - `re-architect <module>` (the change is symptomatic of a deeper SOLID violation — re-run from Phase 6 for that module).
  - `accept` (the regression is real but expected, e.g. a constraint changed mid-flight; user must confirm).

## Conductor next steps

The conductor presents the bisect summary to the user via `AskUserQuestion` with the analyst's recommendation as the default option. **No further implementation work proceeds without user ack.**

## Why this phase exists

This is the second Ouroboros bite specifically wired to refuse forward motion when the loop is going backward. Without it, recursive harnesses tend to "fix" regressions by piling on more code, ratcheting the system into worse shape sprint by sprint.

## Success criterion

A `bisect.md` exists, names a specific commit/file/function, and the user has explicitly ack'd one of the three recommendations. No bisect = no continuation.
