# Tasks Review — Cleanup & Prepare for GitHub

**Branch**: `005-cleanup-prepare-github`
**Date**: 2026-10-18

## Findings
| Principle | Status | Issue | Fix |
|-----------|--------|-------|-----|
| 1:1 coverage | PASS | plan T1-T8 → T001-T009 (T6 split, no scope change) | — |
| FR/SC mapping | PASS | FR-001..010 + SC-001..004 all mapped | — |
| Concreteness | PASS | checkbox + [P1] + named files/commands | — |
| Ordering / external gate | PASS | publish (T009) gated on user-created repo | — |
| Deletions | PASS | only sanctioned scaffold (T002) | — |
| Regression guard | PASS | 45/45 + validate (T007) | — |
| .gitignore explicit | WARN | only a verify step in T002 | made explicit (FR-002) in T002 |
| Stale owner string | WARN | spec SC-003 still `second-thoughts/plugin` | updated to hermes-second-thoughts |

## Review Result
STATUS: PASS (two minor non-blocking notes applied inline)