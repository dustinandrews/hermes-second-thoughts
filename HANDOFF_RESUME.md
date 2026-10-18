# HANDOFF_RESUME

Last update: 2026-10-18 — Sprint 003 merged to main (all 8 gates PASS).

## State
- second-thoughts v0.1.x: standalone Hermes plugin (plugin/ subdir). pre_tool_call hook scans BOTH `terminal` (args.command) and `execute_code` (args.code) against one shared YAML rule set; hard-blocks banned patterns with per-pattern "On second thought…" redirects; config = defaults (`plugin/second_thoughts.yaml`) + user override (`~/.hermes/second-thoughts.yaml`, user wins, fail-open).
- Hot-reload (sprint 002): rules re-read by mtime on every check — YAML edits take effect with NO restart. Hook CODE changes still need a gateway restart to load.
- INSTALLED AND ENABLED on this machine: ~/.hermes/plugins/second-thoughts (untracked copy — re-copy from repo when iterating). Deployed up to sprint 003; a gateway restart is required for execute_code scanning to go live.
- Tests: 33/33 green (`pytest tests/ -q`). `hermes plugins validate ./plugin` clean.
- Branches 001/002/003 retained in depot. Defaults seeded: pipe-interpreter, inline-c, heredoc, execute-code-heredoc, curl-bash, rm-rf, tmp(stay out of /tmp).
- Deploy rule: ALWAYS run an e2e after deploy.

## Next candidates (not started)
- v2+: script-file-WRITE interception (`write_file` producing .py/.sh) — deferred in sprint 003 (FR-008).
- Publish repo (GitHub) so `hermes plugins install owner/second-thoughts/plugin` works.
- Optionally per-tool rule sets IF shared-set false positives bite real execute_code usage (deliberately NOT built yet — YAGNI).

## Gotchas
- YAML rule edits hot-reload (no restart); hook/rule CODE changes require a gateway restart. Keep this distinct.
- execute_code is now scanned with the SAME terminal-oriented rules (FR-006 accepted tradeoff): a Dustin execute_code script that merely CONTAINS e.g. "rm -rf" or "curl ... | bash" in a string/docstring will be hard-blocked. Configurable via the shared YAML — do not "fix" by weakening unless he asks.
- Repo root must stay a NON-package (no __init__.py): a root __init__.py breaks pytest collection (basename collision). Plugin code lives in plugin/.
- plugin.yaml description must NOT contain literal "rm -rf" — trips hermes plugins validate security scan.
- delegate_task payloads: long or quote/em-dash-heavy JSON fails to parse ("Expecting ',' delimiter"); keep context short and put full instructions in a scratch file the sub-agent reads.
- Docs/tests under specs/<NNN>---*.md are canonical; branches retained per sprint method.