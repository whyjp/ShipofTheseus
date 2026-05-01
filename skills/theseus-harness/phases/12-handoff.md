# Phase 12 — Handoff & Summary

## Goal

Close the loop with a single, readable summary the user can act on. The conductor (you) writes this — no sub-agent.

## Inputs

- All artifacts in `.theseus/$RUN_ID/`.

## Output

`.theseus/$RUN_ID/12-handoff.md` and a chat message to the user containing:

- **What was built** — one paragraph, observable terms (mirrors `01-intent.md`'s "What" section).
- **Final score** — the score from the last sprint, with sub-scores.
- **Sprint count** — how many iterations it took.
- **Decisions captured** — bullet list of every choice the user made in Phases 4 and 5 (so it's recoverable).
- **Known gaps** — anything the rubric scored < 1.0 but ≥ 0.9, with one-line reasons.
- **Suggested follow-ups** — the critic's deferred items + any "out of scope but worth doing later" notes.
- **Bisect history** — if any sprints triggered Phase 11, list them with one-line resolutions.

## Chat message shape (to the user)

Three sentences. What you built. Final score and sprint count. Where the artifacts live. Then offer to walk through any artifact.

Example:
> Shipped the auth refactor (intent doc + plan + impl in `.theseus/20260501-…`). Final score 0.93 across 4 sprints; one regression bisected at sprint 3 and resolved by reverting the session-cookie change. Want me to walk through the bisect or the rubric breakdown?

## Success criterion

- Handoff file exists.
- Chat summary fits the user's screen without scrolling.
- Every artifact referenced is reachable from the handoff doc.
