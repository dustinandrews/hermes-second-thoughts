# TEMPLATE: Spec Review — Hot-reload YAML rules (mtime-stat cache)

**Branch**: `002-hot-reload-yaml`
**Date**: 2026-10-18

## Findings

| Principle | Status | Issue | Fix |
|-----------|--------|-------|-----|
| Testability | PASS (F1, Low) | SC-001 'bump mtime' test is flaky on 1s-granularity filesystems | Force distinct stat via os.utime (nanosecond, future-stamped) rather than relying on rewrite timing, or sleep >1s; assert keep-last-good on a bad write |
| Correctness | PASS (F2, Low) | Initial load with DEFAULT file malformed not explicitly specified | One line: initial load falls back to []/inactive like today (trusted shipped file) |
| Clarity | PASS (F3, Info) | match() contract not restated inline in 002 | Restate `(name, message) | None` once in the spec |

## Anti-patterns
| Pattern | Severity | Fix |
|---------|----------|-----|
| (none) | - | - |

## Review Result
STATUS: PASS — FR-003/FR-007 cleanly separate INITIAL load (both absent → inactive, matching sprint-001) from MID-RUN reload (bad edit → keep-last-good + warn); FR-004 thread-safety present; FR-008 preserves match()/hook/block/merge; no speculative scope (YAGNI-clean). F1–F3 are low/nit and fold into the plan + tests.