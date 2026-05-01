# Philosophy

## Why "Ship of Theseus"?

The Ship of Theseus is the thought experiment about identity under continual replacement: if every plank is replaced, is it still the same ship? Software answers this in the affirmative — a feature reaches "done" only after every weak plank has been swapped for a sound one. The harness in this repo is the dock where that swapping happens, in disciplined, scored sprints.

## Lineage

The harness is a synthesis of three loop-shaped patterns from the AI-coding community:

- **Ralph loop** — A tight, recursive loop that asks the model to do the work, evaluate its own output, and re-attempt with the evaluation feedback wired back in. Strength: relentless iteration. Weakness: drift and over-confidence without external grounding.
- **OhMy-series harness** — Adds explicit *roles* (planner, implementer, reviewer, tester) and external evaluators so each role keeps the others honest. Strength: separation of concerns and adversarial review. Weakness: role transitions can lose context.
- **Ouroboros harness** — The serpent eats its tail: the harness's own outputs become the next iteration's inputs, with provenance preserved so any regression is bisectable. Strength: full traceability. Weakness: easy to bloat without scoring discipline.

Theseus harness combines these with a hard quality gate (score ≥ 0.9) and a regression-bisect step that compares the current code against the last known good plank when the score drops.

## Methodologies invoked

The quality gates and sprint loop are not arbitrary — each gate maps to a well-established practice:

- **TDD (Test-Driven Development)** — Red, green, refactor. The sprint loop *is* the red-green cycle, with refactor folded into each iteration's "improve until score ≥ threshold" step.
- **BDD (Behavior-Driven Development)** — Intent docs and clarifications follow a Given/When/Then shape so the spec is executable in spirit.
- **SOLID** — Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion. The quality gate explicitly checks for each (see `phases/10-quality-gates.md`).
- **DDD (Domain-Driven Design)** — Intent extraction asks for the ubiquitous language and bounded context before any code is written.
- **Hexagonal / Ports & Adapters** — The "individual modules with mocks" requirement is hexagonal in spirit: each module has a port, and the test harness can swap real adapters for mocks.
- **Clean Architecture** — Dependencies point inward toward the domain. Cross-cutting concerns live at the edges.
- **Property-based testing** — When unit tests pass but coverage feels shallow, the tester agent is instructed to add property-based tests (Hypothesis, fast-check, etc.) before claiming done.
- **Mutation testing** — Optional gate for high-stakes modules: a coverage number is only as good as the bugs it catches.

## The loop, in one paragraph

A request enters as raw intent. Agent A extracts and documents it; Agent B reviews the doc; a *fresh* Agent C re-comprehends it without seeing A's reasoning; Agent D runs a clarifying dialogue with the user; Agent E critiques the resulting spec for mis-choices and proposes alternatives. Only then does planning begin — and planning itself runs the same five-step loop. Implementation proceeds module by module, each module shipped with unit tests *and* mock-driven integration tests. A test sprint scores the result against a rubric (correctness, scope-fit, SOLID, coverage, FE/BE parity, E2E pass). If the score is below 0.9, the loop iterates. If the score *drops* between sprints, the regression-bisect agent compares the current state against the last known good sprint and surfaces the offending diff before any further work is allowed.

## Non-goals

- This harness does not replace human judgment on architectural direction — it surfaces options and forces the human (or top-level Claude) to choose explicitly.
- It does not chase 100% coverage. 0.9 is the gate; beyond that is diminishing returns.
- It does not run autonomously without supervision on production systems. The clarification phase is a hard checkpoint with the user.
