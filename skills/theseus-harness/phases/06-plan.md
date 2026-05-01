# Phase 6 — Plan (TODO-shaped)

## Goal

Produce an implementation plan as a flat list of TODO items, each small enough that a single sub-agent can finish it in one invocation, each with a defined "done" condition.

## Inputs

- `.theseus/$RUN_ID/01-intent.md`
- `.theseus/$RUN_ID/04-answers.md`
- `.theseus/$RUN_ID/05-critique.md` + `05-decisions.md`

## Sub-agent

Spawn `Agent(subagent_type="Plan")` with [`../agents/planner.md`](../agents/planner.md).

## Output

`.theseus/$RUN_ID/06-plan.md` using [`../templates/plan.template.md`](../templates/plan.template.md). Each TODO has:

- **ID** — `T-001`, `T-002`, …
- **Title** — imperative, one line.
- **Module** — which architectural module it lives in (e.g. `backend/auth`, `frontend/components/login`).
- **Layer** — `domain` | `application` | `adapter` | `ui` | `infra` | `test`.
- **Depends on** — list of TODO IDs.
- **Done when** — observable, testable condition.
- **Tests** — the unit and/or E2E tests this TODO must ship with.
- **Mock surface** — the port/interface this TODO exposes for mocking, if any.

The plan **must** include:

- A "scaffolding" section that creates the module boundaries before any logic is written.
- A "test infra" section that sets up the unit and E2E test harnesses *before* the first feature TODO.
- Backend and frontend TODOs interleaved by dependency, not lumped at the end.

## Success criterion

- Every TODO is achievable in one sub-agent invocation (rule of thumb: < 200 lines of code touched).
- Dependencies form a DAG — no cycles.
- Every leaf TODO has at least one test TODO downstream of it.
