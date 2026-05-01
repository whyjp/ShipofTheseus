# Phase 5 — Critique & Alternatives

## Goal

Before the plan is written, attack the *intent itself*: is this the right thing to build, in the right way? The critic agent surfaces mis-choices, scope traps, simpler alternatives, and known pitfalls.

## Inputs

- `.theseus/$RUN_ID/01-intent.md`
- `.theseus/$RUN_ID/04-answers.md`
- The repo's existing code (the critic should look for prior art that already solves part of this).

## Sub-agent

Spawn `Agent(subagent_type="general-purpose")` with [`../agents/critic.md`](../agents/critic.md). The critic is explicitly adversarial — its job is to be useful, not agreeable.

## Output

`.theseus/$RUN_ID/05-critique.md`:

- **Mis-choices** — places where the stated approach will likely backfire (with reasoning).
- **Scope risks** — features that smell like "while we're at it" creep.
- **Existing solutions** — code in the repo (or well-known libraries) that already does part of this.
- **Alternative approaches** — at least 2, with trade-offs.
- **Recommended path** — the critic's pick + why.
- **Open trade-offs the user should choose** — not for the critic to decide unilaterally.

## What the conductor does next

For every "open trade-off the user should choose," go back to `AskUserQuestion`. Capture answers in `.theseus/$RUN_ID/05-decisions.md`. Only then proceed to Phase 6.

## Success criterion

At least one mis-choice or scope risk is named. If the critic finds nothing, it didn't try — re-run with explicit instruction to be adversarial.
