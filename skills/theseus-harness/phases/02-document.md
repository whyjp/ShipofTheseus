# Phase 2 — Document Review

## Goal

Have a reviewer agent stress-test the intent doc from Phase 1 *as a document* — clarity, completeness, internal consistency — before any implementation reasoning happens.

## Inputs

- `.theseus/$RUN_ID/01-intent.md`

## Sub-agent

Spawn `Agent(subagent_type="general-purpose")` with [`../agents/doc-reviewer.md`](../agents/doc-reviewer.md). Do **not** pass the original raw request — the reviewer must judge the intent doc on its own terms.

## Output

`.theseus/$RUN_ID/02-intent-review.md` with:

- **Verdict** — `accept` | `revise` | `reject`.
- **Clarity issues** — sentences that are ambiguous or under-defined.
- **Consistency issues** — internal contradictions (e.g. constraint A and non-goal B fighting).
- **Missing sections** — anything from the template that wasn't filled in meaningfully.
- **Suggested rewrites** — concrete proposed wording for the worst offenders.

## Success criterion

The verdict is justified by line-level evidence from `01-intent.md`. A verdict without quotes is insufficient — re-run.

## What the conductor does next

- `accept` → proceed to Phase 3.
- `revise` → re-run Phase 1 with the review attached. Track the iteration count; stop after 3 attempts and ask the user.
- `reject` → halt and ask the user. The intent is fundamentally unclear.
