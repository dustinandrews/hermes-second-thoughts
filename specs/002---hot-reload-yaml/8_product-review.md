# TEMPLATE: Product Review — Hot-reload YAML rules (mtime-stat cache)

**Branch**: `002-hot-reload-yaml`
**Date**: 2026-10-18

## Golden Path Tested

**User Story**: US1 — edit the YAML override; next command check reflects the edit with NO gateway restart.
**Path**: isolated temp HERMES_HOME → load INSTALLED plugin via plugin-host python → block command → rewrite override (same name/regex, new message) → same module's next call → pytest → validate.

## Results

- [x] Entry point accessible: PASS — plugin loads + registers under the installed copy
- [x] Core process executes: PASS — hot reload triggered on mtime change; same-module second call returned the EDITED message
- [x] Expected output produced: PASS — `run grep_for_me --x` blocked "…no tmp." then (after edit) "…edited live." with no restart; `ls -la` → None; non-terminal → None
- [x] No critical errors: PASS — no exceptions in probe; isolated temp only, real override untouched

## Defects Found
| Step | Expected | Actual | Severity |
|------|----------|--------|----------|
| (none) | - | - | - |

Regression: pytest 27/27; `hermes plugins validate` clean. Product fit confirmed (WHAT_AND_WHY): guardrail never goes dark on bad edit (keep-last-good in unit suite), no core patch.

## Review Result
STATUS: PASS