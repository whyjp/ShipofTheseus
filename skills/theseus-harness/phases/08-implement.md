# Phase 8 — Implementation

## Goal

Walk the plan's TODO DAG, dispatching one implementer agent per TODO. Each agent ships code + tests + mock surface together — never code alone.

## Inputs

- `.theseus/$RUN_ID/06-plan.md`
- `.theseus/$RUN_ID/07-plan-review.md`

## Sub-agent

For each TODO, spawn `Agent(subagent_type="general-purpose")` with [`../agents/implementer.md`](../agents/implementer.md). The prompt to each implementer must include:

- The single TODO it owns (full text from the plan).
- Its dependencies' "done when" conditions (so it knows what it can rely on).
- The intent doc + decisions, so it can resolve micro-ambiguities without re-asking.
- An explicit instruction: **ship code + tests + mock surface in one invocation, or fail loudly.**

## Output

For each TODO, append to `.theseus/$RUN_ID/08-impl-log.md`:

- TODO ID and title.
- Files created/modified (path + line count).
- Test files added (path + test count).
- Mock/fake surface exposed (interface name + how to use it in tests).
- Any deviations from the plan (with one-sentence reason).

## Parallelism

TODOs with no shared dependencies *should* be dispatched in parallel — issue multiple `Agent` calls in a single message. Serialize only across edges of the DAG.

## Success criterion

- Every TODO in `06-plan.md` has a corresponding entry in `08-impl-log.md`.
- No TODO shipped code without tests.
- No TODO shipped tests without a mock surface for its external dependencies.

## When an implementer fails

If an implementer reports failure or partial completion:

1. Read its actual output (don't trust the summary — see CLAUDE.md "trust but verify").
2. If the failure is environmental (missing dep), fix and re-dispatch.
3. If the failure is conceptual (TODO too big, dependency wrong), go back to Phase 6 and split the TODO. Do not paper over.
