# Phase 7 — Plan Recursion (Re-plan)

## Goal

Run the same intent→review→comprehension→clarify→critique loop *on the plan itself*. The Ouroboros bites a second time: the plan is now the artifact under scrutiny.

## Inputs

- `.theseus/$RUN_ID/06-plan.md` (only)

## Sub-agent

Spawn a *fresh* `Agent(subagent_type="general-purpose")` with [`../agents/plan-reviewer.md`](../agents/plan-reviewer.md). The agent has not seen the intent doc — it reads the plan cold and must answer:

1. From this plan alone, what feature is being built?
2. What would I implement first?
3. What in this plan looks underspecified, oversized, or out of order?
4. What dependencies are missing or wrong?

## Output

`.theseus/$RUN_ID/07-plan-review.md` with the four answers above plus a verdict (`accept` | `revise` | `reject`).

## Conductor next steps

- The conductor diffs the reviewer's answer to (1) against `01-intent.md`. Mismatch = the plan does not encode the intent → re-run Phase 6.
- Verdict `revise` → re-run Phase 6 with the review attached. Cap at 3 attempts.
- Verdict `accept` → proceed to Phase 8.

## Why this phase exists

Most coding harnesses skip plan review and pay for it during implementation when "obvious" steps turn out to require unstated infra. Catching this here costs a single agent invocation; catching it during sprint 4 costs a full bisect.
