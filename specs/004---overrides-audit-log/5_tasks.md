# Tasks — Overrides + Audit Log + Misfire Escalation

**Branch**: `004-overrides-audit-log`
**Date**: 2026-10-18

## Phase 1 — RED tests: overrides (US1)
- [ ] **T001** [P1] `tests`: matching override passes (None) + audit `override` entry; same payload with override removed → block + audit `block`.
- [ ] **T002** [P1] `tests`: both-must-match gate — override with rule-name match but pattern mismatch, and pattern match but rule-name mismatch, both still hard-block.
- [ ] **T003** [P1] `tests`: overrides missing / empty / overrides file present but malformed → still block (no grant).
- [ ] **T004** [P1] `tests`: mid-run edit makes a previously-loaded override file malformed/empty → ALL grants revoked at once (fail closed), subsequent rule hits block.

## Phase 2 — RED tests: audit log (US2)
- [ ] **T005** [P1] `tests`: block and override both append JSONL `{ts,tool,rule,action,payload,message}` to `$HERMES_HOME/second-thoughts-blocks.jsonl`; non-matching and other-tool calls write nothing.
- [ ] **T006** [P1] `tests`: forced audit write-failure still blocks (never converts block→pass) and never raises.
- [ ] **T007** [P1] `tests`: audit bounded — over-cap appends trim to keep last N entries.

## Phase 3 — RED tests: block message + docs (US3)
- [ ] **T008** [P1] `tests`: block message contains the rule name and the misfire-escalation suffix.
- [ ] **T009** [P1] `tests`: repo contains an agent-facing doc asserting the no-silent-workaround rule and misfire report flow (SC-004a).

## Phase 4 — RED tests: hot-reload / fail-closed (SC-005)
- [ ] **T010** [P1] `tests`: add an override mid-run → next hook call passes with no restart; malformed edit → all revoked (blocks).

## Phase 5 — GREEN implement
- [ ] **T011** [P1] `plugin/overrides.py`: `OverrideStore` (mtime-stat + fail-closed), `load_overrides`, `matches(payload, rule_name)` (both-must-match).
- [ ] **T012** [P1] `plugin/audit.py`: `AuditLog` JSONL append, lazy open, bounded trim, errors swallowed (never affect decision).
- [ ] **T013** [P1] `plugin/__init__.py`: wire order DD-4 (match→override→audit→block/None), escalation suffix on block messages.
- [ ] **T014** [P1] `docs`: README/MISFIRE.md no-silent-workaround declaration.

## Phase 6 — Validation
- [ ] **T015** [P1] `pytest tests/ -q` full suite green; `hermes plugins validate ./plugin` passes.

## Review Result
STATUS: [PASS | FAIL]