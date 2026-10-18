# TEMPLATE: Implementation Plan — Hot-reload YAML rules (mtime-stat cache)

**Branch**: `002-hot-reload-yaml`
**Date**: 2026-10-18
**Status**: Draft

## Summary
Replace the current load-once module state (`RULES = compile_rules(load_rules())`) with an mtime-stat cache: on every `match()` we cheaply stat both YAML paths; if unchanged, reuse the cached compiled rules; if either changed, reload+merge+recompile under a lock and swap atomically. A failed reload (parse error, non-list, missing PyYAML) keeps the last-good ruleset and logs a warning — the guardrail never goes dark from a bad edit. Public API unchanged: `rules.match(command) -> (name, message) | None`.

## Technical Context
- Stack: Python 3.10+ stdlib (`re`, `pathlib`, `threading`, `logging`, `os`), PyYAML only.
- Current module: `rules.py` does `RULES = compile_rules(load_rules())` at import. Preserve `load_rules`, `compile_rules`, `CompiledRule`, `match`, and the exported `RULES` only if tests/consumers touch it (they don't; `match` is the contract).
- The hook (`__init__.py::_on_pre_tool_call`) calls `rules.match(command)`; unchanged.
- Concurrency: gateway may run `pre_tool_call` for multiple sessions; use a single `threading.Lock` held only around reload/swap. Readers snapshot the list once (immutable after swap) so they never see a torn state.
- mtime granularity: tests must set explicit nanosecond mtimes via `os.utime(path, ns=(t, t))` with a future/fresh stamp, never rely on write-timing, to be deterministic on 1s-granularity filesystems (spec-review F1).

## Design Decisions
- **DD-1** mtime-stat cache (option #2 from discussion) over per-call re-read: preserves "compile once when unchanged" perf, hot-reloads on edit.
- **DD-2** keep-last-good on reload failure (FR-003), incl. mid-run removal of BOTH files (FR-007); only the INITIAL load with both absent is inactive — no behavior change vs sprint-001.
- **DD-3** user-wins merge and regex-skip-with-warning semantics carried over verbatim into reload.
- **DD-4** store per-path mtimes (`default.yaml` + user override); a change to EITHER triggers reload (FR-005).

## Project Structure (unchanged)
- `plugin/rules.py` — add `RuleStore` (or module-level reload-guarded state) + `ensure_fresh()`; keep `load_rules`, `compile_rules`, `match`.
- `plugin/second_thoughts.yaml`, `plugin/__init__.py`, `plugin.yaml` — unchanged.
- `tests/test_second_thoughts.py` — extend with hot-reload cases.

## Tasks
- **T1** (RED) tests: hot-reload — append a rule to a temp override, os.utime future-stamp (nanoseconds, per F1), `match()` returns the new rule without restart (SC-001).
- **T2** (RED) tests: keep-last-good — write invalid YAML to override after a good load; `match()` still blocks pipe-interpreter and a warning is emitted (SC-002); mid-run both-removed retains last-good (US2-2); initial both-absent inactive (US2-3); unchanged-config returns cached with no reload (no recompile).
- **T3** (RED) tests: atomic-swap concurrency smoke — many threads match/reload concurrently without error or torn reads (FR-004).
- **T4** (GREEN) `rules.py`: refactor module-level load into a guarded store — mtime cache + atomic swap + reload-on-change; keep `match()` signature.
- **T5** (GREEN) `rules.py`: reload failure path logs a warning and retains last-good (empty-first-load path stays as-is).
- **T6** (validation) `pytest tests/ -q` all green incl. sprint-001 suite + `hermes plugins validate ./plugin` (regression check only).

## Review Result
Round 1: STATUS: FAIL — TDD ordering violated (RED tests sequenced after GREEN implementation). Prescribed non-structural fix: reorder tasks to RED (T1–T3 tests) then GREEN (T4–T5 rules.py). Applied in-session.

Round 2: STATUS: PASS — tests-first restored; design/coverage otherwise sound.