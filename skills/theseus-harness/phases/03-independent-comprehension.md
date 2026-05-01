# Phase 3 — Independent Comprehension

## Goal

Verify the intent doc transmits meaning, not just words. A *fresh* sub-agent — with no knowledge of the original request, the reviewer's verdict, or your own reasoning — reads the intent doc and writes back what it understood. If the round-trip loses meaning, the doc is wrong.

## Inputs

- `.theseus/$RUN_ID/01-intent.md` (only — nothing else)

## Sub-agent

Spawn a *new* `Agent(subagent_type="general-purpose")` with [`../agents/independent-comprehender.md`](../agents/independent-comprehender.md). The prompt must be self-contained: do not reference earlier conversation. Treat the agent as if it walked into the building this morning.

## Output

`.theseus/$RUN_ID/03-comprehension.md`:

- **What I understand the goal to be** — restated in the agent's own words.
- **What success looks like** — observable outcomes.
- **Where I'd start** — first 3 implementation steps the agent would take.
- **What I'm uncertain about** — list of "I would need to ask the user…" items.

## Success criterion

The conductor (you) does a *diff* between this doc and `01-intent.md`. If the comprehender's "what I understand" diverges meaningfully from the intent's "what" — different scope, different stakeholders, different success metric — the intent doc failed and Phase 1 must be re-run with the divergence as feedback.

## Why this phase exists

This is the first Ouroboros bite: the harness's own output (`01-intent.md`) becomes the next agent's input, and the agent's output is checked against the original. Drift gets caught here, before any code costs time.
