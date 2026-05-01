# Plan — `<short title>`

> Run id: `<RUN_ID>` · Generated: `<ISO timestamp>` · Source: `01-intent.md` + `04-answers.md` + `05-decisions.md`

## Architectural overview
<One paragraph: which modules will exist, which talk to which, where the ports are.>

## Module map
| Module | Layer | Responsibility | Port |
| ------ | ----- | -------------- | ---- |
| `backend/auth` | application | Authn + session | `AuthService` |
| `backend/auth/adapter/jwt` | adapter | JWT impl of `AuthService` | — |
| `frontend/login` | ui | Login form + flow | — |
| `…` | … | … | … |

## TODOs

### § 1. Scaffolding
- **T-001 — Create `backend/auth/` module skeleton**
  - module: `backend/auth`
  - layer: domain
  - depends_on: []
  - done_when: package exists, exports empty `AuthService` port
  - tests: `backend/auth/test_module_loads.py`
  - mock_surface: `FakeAuthService` (returns canned values)

### § 2. Test infrastructure
- **T-010 — Set up unit + integration harness**
  - module: `tests/`
  - layer: test
  - depends_on: []
  - done_when: `pytest` runs, `npm test` runs, both green on empty suite
  - tests: meta-test that asserts both runners exit 0
  - mock_surface: n/a

- **T-011 — Set up E2E harness (Playwright)**
  - module: `tests/e2e/`
  - layer: test
  - depends_on: []
  - done_when: smoke test loads the app and asserts title
  - tests: `tests/e2e/smoke.spec.ts`
  - mock_surface: n/a

### § 3. Backend feature TODOs
- **T-020 — …**

### § 4. Frontend feature TODOs
- **T-040 — …**

### § 5. Wiring TODOs
- **T-060 — …**

### § 6. Hardening TODOs
- **T-080 — Add error-path E2E for login failure**
  - …

## Dependency DAG (summary)
```
T-001 ─┬─ T-020 ─┬─ T-022 ── T-060 ─┐
       └─ T-021 ─┘                  ├─ T-080
T-010 ── (gates all T-0NN tests)    │
T-011 ───────────────────────────── ┘
T-040 ── T-041 ── T-060
```

## Rationale notes
- <Why this split? Why these ports?>
- <Trade-offs deliberately accepted (link to `05-critique.md`).>

## Open follow-ups (deferred, not in this plan)
- <Item the critic flagged as out-of-scope but worth doing later.>
