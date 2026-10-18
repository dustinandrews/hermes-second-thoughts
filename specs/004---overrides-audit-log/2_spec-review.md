# Spec Review — Overrides + Audit Log + Misfire Escalation

**Branch**: `004-overrides-audit-log`
**Date**: 2026-10-18

## Round 1 (FAIL)
**Issue (high, blocking)**: FR-003 copy-pasted the block-rules' *keep-last-good* (fail-open) semantics onto OVERRIDES, which fail OPEN to stale grants on a mid-run malformed edit — exactly the "guard silently disabled" failure Dustin forbids. Secondary: override/log file paths unspecified; FR-009 had no matching SC.

**Prescribed fixes (all applied inline)**:
- FR-003 → overrides FAIL CLOSED: any malformed/empty mid-run override edit revokes ALL grants; never retain stale grants. Explicitly distinguished from block-rules' keep-last-good (fail-open-to-last-good).
- Added FR-003a (path `$HERMES_HOME/second-thoughts-overrides.yaml`), path on FR-004 (`…-blocks.jsonl`).
- Added SC-002 fail-closed-mid-run clause and SC-004a (docs declaration) and hardened SC-005 (hot-reload + fail-closed).

## Audit safety (axe 2–5)
FR-005/FR-007 correct (write-failure never converts block→pass); hot-reload reuse PASS; scope PASS (terminal+execute_code; write_file deferred); testability PASS.

## Review Result
Round 1: STATUS: FAIL — overrides fail direction wrong + missing paths/SC.
Round 2: STATUS: PASS — overrides fail closed, paths named, FR-009 mapped to SC-004a.