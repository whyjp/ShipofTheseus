# Phase 4 — Clarification Dialogue

## Goal

Resolve every ambiguity in the intent doc by asking the user — directly, with concrete options. This is the only phase that *requires* the user's voice.

## Inputs

- `.theseus/$RUN_ID/01-intent.md`
- `.theseus/$RUN_ID/03-comprehension.md` (where the round-trip drifted)

## Sub-agent

Spawn `Agent(subagent_type="general-purpose")` with [`../agents/clarifier.md`](../agents/clarifier.md). The clarifier produces a *question list* — it does not ask the user directly. The conductor (you) is the one who asks via `AskUserQuestion`, because only the conductor has the live conversation.

## Output

Two files:

1. `.theseus/$RUN_ID/04-questions.md` — the clarifier's question list, each entry with: question text, why it matters, candidate answers (multiple choice when possible).
2. `.theseus/$RUN_ID/04-answers.md` — the user's answers, captured verbatim with timestamps.

## How the conductor asks

For each question in `04-questions.md`:

- If candidate answers exist → use `AskUserQuestion` with up to 4 options + "other".
- If freeform → ask in plain prose.
- **Never assume** an answer to push forward. If the user says "you decide," capture that explicitly as a deferred decision and flag it in the critique phase.

## Success criterion

`04-answers.md` covers every question in `04-questions.md`, with no `TBD` or `?` markers. Halts that warranted halting actually halted.
