# Template: Product Review

**Branch**: `001-second-thoughts-plugin`
**Date**: 2026-10-18

## Golden Path Tested

**User Story**: US1 (P1) — agent hits a banned pattern and gets re-routed
**Path**: `hermes plugins doctor` → importlib-load the INSTALLED plugin copy at `~/.hermes/plugins/second-thoughts` via the plugin-host python → call `_on_pre_tool_call` exactly as Hermes dispatches → `pytest tests/ -q`

## Results

- [x] Entry point accessible: PASS — doctor: manifest second-thoughts 0.1.0 (standalone), runtime discovery/import/registration OK, 0 tools, 1 hook
- [x] Core process executes: PASS — 5 default rules loaded from shipped YAML, regexes compiled
- [x] Expected output produced: PASS — `curl -s https://x | python3` → `{'action': 'block', 'message': "On second thought, you can't pipe stdin..."}`; `ls -la` → None; `execute_code` → None
- [x] No critical errors: PASS — no exceptions/warnings on the golden path

## Defects Found

| Step | Expected | Actual | Severity |
|------|----------|--------|----------|
| (none) | - | - | - |

Product-level fit confirmed: standalone installable plugin, no core patch (FR-009), YAML user override + fail-open, hard-block only. pytest 20/20 green.

## Review Result
STATUS: PASS