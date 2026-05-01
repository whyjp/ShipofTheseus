# Phase 9 — Quality Gates

## Goal

Before any tests run, audit the implementation against five fixed gates. A failure here means the test sprint will burn cycles on the wrong shape of code — fix the shape first.

## The five gates

| Gate | What it checks | Fail signal |
| ---- | -------------- | ----------- |
| **Intent fidelity** | Does what was built match `01-intent.md` + `04-answers.md`? | Feature exists that wasn't requested, or requested feature is missing. |
| **Scope discipline** | Anything outside the plan's TODO list? | Files touched that no TODO authorized. |
| **SOLID** | SRP / OCP / LSP / ISP / DIP per module. | A class with > 1 reason to change; concrete deps where ports were specified; interface fatness. |
| **Test coverage shape** | Every public surface has a unit test; every cross-module path has an integration test; happy-path E2E exists. | Public function with no test; module without a fake/mock; no E2E for the user-visible flow. |
| **FE/BE parity** | If the feature spans frontend and backend, both sides have equivalent test depth. | Backend has 80% coverage and frontend has snapshot-only tests. |

## Inputs

- `.theseus/$RUN_ID/01-intent.md`, `04-answers.md`, `06-plan.md`, `08-impl-log.md`
- The actual code on disk (the agent must `Read` files, not trust the log).

## Sub-agent

Spawn `Agent(subagent_type="general-purpose")` with [`../agents/quality-gate.md`](../agents/quality-gate.md).

## Output

`.theseus/$RUN_ID/09-quality-gate.md`:

- For each gate: `pass` | `fail` + evidence (file:line citations).
- For each fail: a remediation TODO that gets folded back into the plan as `T-NNN-fix`.
- An overall verdict: `proceed` | `remediate-then-proceed` | `halt`.

## Conductor next steps

- `proceed` → Phase 10.
- `remediate-then-proceed` → re-run Phase 8 for the fix-TODOs only, then re-run Phase 9.
- `halt` → ask the user. Something structural is wrong.

## Success criterion

Each gate's verdict is backed by at least one `path/to/file.ext:NN` citation. Verdicts without citations are not credible — re-run.
