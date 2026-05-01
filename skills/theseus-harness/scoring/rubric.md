# Scoring Rubric

The harness exits when the **overall score ≥ 0.9**. Score is a weighted average of six sub-scores, each in `[0, 1]`. Weights sum to 1.0.

| Dimension | Weight | What it measures |
| --------- | -----: | ---------------- |
| `correctness` | 0.25 | Test pass rate × intent fidelity. Failing tests dominate. |
| `scope_fit` | 0.10 | Fraction of changed files mapped to a TODO. |
| `solid` | 0.15 | Fraction of modules passing all 5 SOLID checks in Phase 9. |
| `coverage` | 0.20 | Branch coverage, weighted: BE 0.5 + FE 0.5. Floors at the lower of the two — punishes parity failures. |
| `fe_be_parity` | 0.10 | 1.0 if both sides have unit + integration + E2E; lower otherwise. n/a → weight redistributed to `correctness`. |
| `e2e_pass` | 0.20 | Pass rate of E2E suite specifically. Multiplicatively penalizes happy-path regressions. |

## Sub-score formulas

```
correctness   = test_pass_rate × intent_fidelity
                where intent_fidelity ∈ {1.0 if Gate 1 passed, 0.7 if remediable, 0.0 if halt}

scope_fit     = files_mapped_to_todos / files_touched

solid         = modules_passing_solid / modules_total

coverage      = min(be_coverage, fe_coverage)
                # using min, not avg, by design — see PHILOSOPHY.md

fe_be_parity  = 1.0 if both sides have {unit, integration, e2e}
              = 0.7 if one side missing one tier
              = 0.4 if one side missing two tiers
              = 0.0 if one side has only smoke tests
              = "n/a" if feature is single-side

e2e_pass      = e2e_passing / e2e_total
```

## Overall score

```
score = Σ (weight_i × sub_score_i) for i in dimensions where sub_score_i is not "n/a"
        with weights renormalized over the active dimensions
```

## Hard exits regardless of score

- Any test marked `.only` or `.skip` (unless the skip has a justification comment) → score capped at 0.5.
- Any `console.log` / `print` debugging left in production code → score capped at 0.85.
- Lint errors → score capped at 0.85.
- Type errors → score capped at 0.7.

## Regression threshold

`score(sprint_n) < score(sprint_n-1) - 0.05` triggers Phase 11 (regression bisect). The constant 0.05 is a tunable in `score.py`'s CLI.

## What the rubric is not

- It is not a measure of code beauty.
- It is not adjustable mid-run.
- It is not a substitute for human judgment on architectural direction — a 0.95 score with a bad architecture choice is still a bad outcome. The rubric catches *executional* failure; Phase 5 (critique) catches *directional* failure.
