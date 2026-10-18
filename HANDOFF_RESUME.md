# HANDOFF_RESUME

Last update: 2026-10-18 — Sprint 004 merged to main (all 8 gates PASS).

## State
- second-thoughts v0.1.x: standalone Hermes plugin (plugin/ subdir). pre_tool_call hook scans BOTH `terminal` (args.command) and `execute_code` (args.code) against one shared YAML rule set; hard-blocks banned patterns with per-pattern "On second thought…" redirects PLUS a `[rule: <name>]` + misfire-escalation suffix ("If you believe this is a misfire, stop and report it; do not work around it."). config = defaults (`plugin/second_thoughts.yaml`) + user override (`~/.hermes/second-thoughts.yaml`, user wins, fail-open).
- **Sprint 004 (live):** human-authored allow-overrides `~/.hermes/second-thoughts-overrides.yaml` (rule+pattern must BOTH match; FAILS CLOSED on missing/empty/malformed, revoked at once on a bad mid-run edit) + JSONL audit log `~/.hermes/second-thoughts-blocks.jsonl` (every block and override grant `{ts,tool,rule,action,payload,message}`, capped payload, 1 MiB/5000-line bounded, write-failure NEVER flips block→pass). MISFIRE.md documents the no-silent-workaround rule.
- Hot-reload: rules AND overrides re-read by mtime on every check — YAML edits take effect with NO restart. Hook CODE changes still need a gateway restart to load.
- INSTALLED AND ENABLED on this machine: ~/.hermes/plugins/second-thoughts (untracked copy — re-copy from repo when iterating). Deployed up to sprint 004; a gateway restart is required for the new overrides/audit/misfire code to go live.
- Tests: 45/45 green (`pytest tests/ -q`). `hermes plugins validate ./plugin` clean.
- Branches 001/002/003/004 retained in depot. Defaults seeded: pipe-interpreter, inline-c, heredoc, execute-code-heredoc, curl-bash, rm-rf, tmp(stay out of /tmp).
- Deploy rule: ALWAYS run an e2e after deploy.

## Next candidates (not started)
- Publication to GitHub so `hermes plugins install owner/second-thoughts/plugin` works.
- Script-file-WRITE interception (`write_file` producing .py/.sh) — deferred since sprint 003 (FR-008).
- Per-tool rule sets IF shared-set false positives bite real execute_code usage (deliberately NOT built yet — YAGNI).
- Maybe a small aggregator/CLI over the audit log to surface misfire candidates (the log is ground truth; a reader beats grepping).

## Gotchas
- YAML rule edits hot-reload (no restart); hook/rule CODE changes require a gateway restart. Keep this distinct.
- execute_code is now scanned with the SAME terminal-oriented rules (FR-006 accepted tradeoff): a Dustin execute_code script that merely CONTAINS e.g. "rm -rf" or "curl ... | bash" in a string/docstring will be hard-blocked. Configurable via the shared YAML — do not "fix" by weakening unless he asks.
- Repo root must stay a NON-package (no __init__.py): a root __init__.py breaks pytest collection (basename collision). Plugin code lives in plugin/.
- plugin.yaml description must NOT contain literal "rm -rf" — trips hermes plugins validate security scan.
- delegate_task payloads: long or quote/em-dash-heavy JSON fails to parse ("Expecting ',' delimiter"); keep context short and put full instructions in a scratch file the sub-agent reads.
- Docs/tests under specs/<NNN>---*.md are canonical; branches retained per sprint method.