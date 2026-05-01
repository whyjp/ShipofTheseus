# Phase 1 — Intent Extraction

## Goal

Turn the user's raw request into a structured intent document so every downstream agent has the same starting point.

## Inputs

- `.theseus/$RUN_ID/00-request.txt` — the raw request.
- The repo's `README.md` and any obvious entry points (so the agent grounds the request in real code).

## Sub-agent

Spawn `Agent(subagent_type="general-purpose")` with the prompt at [`../agents/intent-extractor.md`](../agents/intent-extractor.md). Pass the raw request and the repo root as context.

## Output

Write `.theseus/$RUN_ID/01-intent.md` using the template at [`../templates/intent.template.md`](../templates/intent.template.md). The doc must contain:

- **What** — one paragraph, observable outcome.
- **Why** — the problem being solved or the value delivered.
- **Non-goals** — things explicitly out of scope.
- **Constraints** — hard requirements (perf, compat, security, deadline).
- **Ubiquitous language** — domain terms with definitions.
- **Stakeholders** — who consumes the output.
- **Open questions** — anything the agent could not resolve from the request alone.

## Success criterion

The doc is *self-contained*: someone who has not seen the original request can read the intent doc and know exactly what to build. If you, as the conductor, find yourself filling in gaps from memory, the phase failed — re-run it.

## Common failure modes

- Agent restates the request verbatim instead of extracting intent. Re-run with explicit instruction to *interpret*, not echo.
- Agent assumes a tech stack not mentioned. The intent doc is technology-agnostic; stack decisions happen in Phase 6.
- Open questions list is empty. There are *always* open questions. Empty list = lazy extraction.
