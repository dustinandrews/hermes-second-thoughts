# Tech Stack

- **Plugin:** Hermes plugin (manifest v2) — `plugin.yaml` + `__init__.py` `register(ctx)`, `pre_tool_call` hook only; standalone repo, no core patches
- **Language:** Python 3.10+ stdlib only (re, pathlib) + PyYAML (declared in `python_dependencies`)
- **Config:** YAML — repo-shipped `second_thoughts.yaml` defaults + user override `~/.hermes/second-thoughts.yaml` (user wins; malformed → fail open)
- **Testing:** pytest; mirror `plugins/security-guidance` tests from the hermes-agent repo (`tests/plugins/`)
- **Validation:** `hermes plugins validate`, `hermes plugins doctor`
- **Version control:** git, repo at `~/projects/second-thoughts`

## Install / share
- `hermes plugins install <owner>/second-thoughts` (published repo)
- Local dev: install from the repo path (`hermes plugins install ./second-thoughts`) — no symlinks