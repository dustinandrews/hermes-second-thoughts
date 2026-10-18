# Implementation Plan — Overrides + Audit Log + Misfire Escalation

**Branch**: `004-overrides-audit-log`
**Date**: 2026-10-18
**Status**: Draft

## Summary
Add (1) a human-authored overrides file (`$HERMES_HOME/second-thoughts-overrides.yaml`) consulted for every rule hit so a narrow, specific false-positive payload can pass; (2) a JSONL audit log (`$HERMES_HOME/second-thoughts-blocks.jsonl`) recording every block and override grant for detection; (3) a misfire-escalation suffix on every block message + a no-silent-workaround agent doc.

## Technical Context
- `plugin/rules.py` — `RuleStore` hot-reload engine (mtime-stat cache + atomic swap + keep-last-good for BLOCK rules). `match(payload) -> (name, message) | None`.
- `plugin/__init__.py::_on_pre_tool_call` — scans terminal(`command`) and execute_code(`code`); returns block directive or None.
- New: `plugin/overrides.py` — `OverrideStore` reusing the mtime-stat cache shape but with OPPOSITE failure semantics: good edit → reload; malformed/empty → drop ALL grants (fail closed), never keep-last-good.
- New: audit append helper — JSONL, lazily-opened append, bounded (trim when > cap). Write failures logged, never affect the decision.

## Design Decisions
- **DD-1** OverrideStore = mtime-stat cache + FAIL-CLOSED on malformed/empty (opposite of RuleStore keep-last-good). Good-state reload is atomic under lock.
- **DD-2** Override patch: `{rule, pattern, reason}` — match iff `re.search(pattern, payload)` AND `entry.rule == rule_name` on the hit from `rules.match`. Compile `pattern` once per reload.
- **DD-3** Audit entry `{ts, tool, rule, action: "block"|"override", payload, message}`; payload capped (e.g. 2000 chars) to bound size; `action` chosen by the actual decision.
- **DD-4** Order per call: `rules.match` → if None pass (no audit). If hit → check overrides → if granted: return None + audit `override`; else: return block + audit `block`. Block message = `f"{rule_message} [rule: {name}] {ESCALATION_MSG}"`.
- **DD-5** ESCALATION_MSG constant: "If you believe this is a misfire, stop and report it; do not work around it."
- **DD-6** Audit bounded: append until file > 1 MiB, then rewrite keeping the last 5000 entries (stdlib only). Store path via `_audit_log_file()` under HERMES_HOME.
- **DD-7** write_file/script-file interception remains out of scope (sprint 003 FR-008).

## Project Structure
- `plugin/overrides.py` (new) — `OverrideStore`, `load_overrides(path)`, `compile_overrides`, `matches(payload, rule_name)`.
- `plugin/audit.py` (new) — `AuditLog`, `append(entry)` (JSONL, lazy open, bounded trim, swallow errors).
- `plugin/__init__.py` — wire: import OverrideStore (+ its own mtime check), audit, escalation suffix; logic per DD-4.
- `plugin/rules.py` — unchanged (block-rule keep-last-good preserved).
- `tests/test_second_thoughts.py` — add overrides + audit tests (see tasks).
- `README.md` or new `MISFIRE.md` — no-silent-workaround declaration (FR-009 / SC-004a).

## Tasks
- **T1** (RED) overrides tests: matching override passes + audit `override` entry; same payload without override blocks + audit `block`; missing/empty/malformed overrides → block; mid-run malformed edit revokes all grants (fail closed).
- **T2** (RED) audit tests: block and override write JSONL `{ts,tool,rule,action,payload,message}`; non-matching/other-tool write nothing; forced write-failure still blocks (does not pass); bounded (trim keeps last N).
- **T3** (RED) message + docs tests (SC-004/SC-004a): block message contains rule name + escalation suffix; docs file contains no-silent-workaround declaration.
- **T4** (RED) hot-reload/SC-005: add override → next hook call passes (no restart); malformed edit → all revoked (blocks).
- **T5** (GREEN) `plugin/overrides.py` + `plugin/audit.py` + wire `__init__.py`.
- **T6** (GREEN) docs: README/MISFIRE.md no-silent-workaround declaration.
- **T7** (validation) `pytest tests/ -q` full suite green + `hermes plugins validate ./plugin`.

## Review Result
STATUS: [PASS | FAIL]