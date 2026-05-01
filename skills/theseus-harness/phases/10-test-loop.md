# Phase 10 — Test Sprint Loop

## Goal

Run the full test matrix, score it, and iterate until score ≥ 0.9. Every iteration is a *sprint* with its own report. No hand-tweaking the score — `scoring/score.py` is authoritative.

## Test matrix (per sprint)

1. **Backend unit tests** — every public function in the domain and application layers.
2. **Backend integration tests** — adapters wired against fakes.
3. **Frontend unit tests** — components in isolation.
4. **Frontend integration tests** — components wired against fake services.
5. **E2E tests** — the user-visible happy path + at least one error path.
6. **Property-based tests** (if the rubric flags shallow coverage).

## Sub-agent

Spawn `Agent(subagent_type="general-purpose")` with [`../agents/tester.md`](../agents/tester.md). The tester *runs* the suites and writes the raw results; it does not score. Scoring is mechanical.

## Output (per sprint)

`.theseus/$RUN_ID/sprints/NN-report.md`:

- Sprint number.
- Each suite: pass/fail counts, duration, coverage %.
- Score (from `scoring/score.py`) with sub-scores per rubric dimension.
- Delta vs. previous sprint (per dimension).
- Verdict: `pass` (score ≥ 0.9) | `iterate` (score < 0.9) | `regression` (score dropped > 0.05).

## The loop

```python
sprint = 1
prev_score = None
while True:
    results = run_test_matrix()
    score, sub_scores = score_py(rubric, results, prior=prev_score)
    write_sprint_report(sprint, results, score, sub_scores, prev_score)

    if score >= 0.9:
        return "pass"

    if prev_score is not None and score < prev_score - 0.05:
        run_phase_11_bisect(sprint)        # writes sprints/NN-bisect.md
        wait_for_human_ack()                # AskUserQuestion

    failing_dimensions = [d for d, s in sub_scores.items() if s < 0.9]
    spawn_implementer(failing_dimensions, results.failing_tests)

    prev_score = score
    sprint += 1
    if sprint > 8:
        halt_and_ask_user()                 # safety cap
```

## Success criterion

- `score ≥ 0.9` is achieved without disabling tests, lowering thresholds, or editing the rubric.
- All sprint reports are present in `sprints/`.
- If any sprint triggered Phase 11, a `bisect.md` exists alongside the report and the user has ack'd.

## Anti-patterns the tester is forbidden from

- Marking a flaky test as skipped to raise the score.
- Lowering coverage thresholds to pass a gate.
- "Adapting the rubric" — the rubric is read-only during a run.
