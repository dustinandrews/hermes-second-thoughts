# TEMPLATE: Tasks — Hot-reload YAML rules (mtime-stat cache)

**Branch**: `002-hot-reload-yaml`
**Date**: 2026-10-18

## Task List

### Phase 1 — RED tests: US1 hot-reload (mtime cache)
- [ ] **T001** [P1] `tests`: append a rule to a temp override; `os.utime(ns=future)` stamp it; assert `match()` returns new rule without restart (SC-001).

### Phase 2 — RED tests: US2 keep-last-good
- [ ] **T002** [P1] `tests`: after a good load, write invalid YAML to override; assert `match()` still blocks pipe-interpreter and a warning is emitted (SC-002).
- [ ] **T003** [P1] `tests`: mid-run removal of BOTH files retains last-good + warning (US2-2); initial both-absent is inactive (US2-3); unchanged-config returns cached (no reload).

### Phase 3 — RED tests: FR-004 concurrency
- [ ] **T004** [P2] `tests`: many threads `match()`/reload concurrently under tmp isolation; no errors, no torn reads.

### Phase 4 — GREEN implement
- [ ] **T005** [P1] `rules.py`: guarded store — mtime cache + atomic swap + reload-on-change; keep `match()` signature.
- [ ] **T006** [P1] `rules.py`: reload failure logs warning and retains last-good; empty-first-load path unchanged.

### Phase 5 — Validation
- [ ] **T007** [P1] `pytest tests/ -q` all green incl. sprint-001 suite; `hermes plugins validate ./plugin` passes (regression only; no doctor requirement).

## Review Result
STATUS: [PASS | FAIL]