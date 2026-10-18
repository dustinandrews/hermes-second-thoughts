# HANDOFF_RESUME

Last update: 2026-10-18 — Sprint 001 merged to main (all 8 gates PASS).

## State
- second-thoughts v0.1.0: standalone Hermes plugin (plugin/ subdir) — pre_tool_call hook, terminal-only, YAML pattern list (defaults + ~/.hermes/second-thoughts.yaml override, user wins, fail-open).
- INSTALLED AND ENABLED on this machine: ~/.hermes/plugins/second-thoughts (untracked copy — re-copy from repo when iterating). Gateway hot-reloaded; hook is LIVE.
- Tests: 20/20 green (`pytest tests/ -q`).
- Branch `001-second-thoughts-plugin` retained in depot (merged with --no-ff into main).
- Defaults seeded: pipe-interpreter, inline-c, heredoc, curl-bash, rm-rf.

## Next candidates (not started)
- v2+: execute_code / script-file-write interception (holding per spec).
- Publish repo (GitHub) so `hermes plugins install owner/second-thoughts/plugin` works.

## Gotchas
- Rules compile ONCE at plugin import. Editing second_thoughts.yaml (repo or installed) requires a gateway restart to take effect (no hot reload yet).
- Repo root must stay a NON-package (no __init__.py): a root __init__.py breaks pytest collection (basename collision). Plugin code lives in plugin/.
- plugin.yaml description must NOT contain literal "rm -rf" — trips hermes plugins validate security scan.
- delegate_task payloads: long or quote/em-dash-heavy JSON fails to parse ("Expecting ',' delimiter"); keep context short and put full instructions in a scratch file the sub-agent reads.