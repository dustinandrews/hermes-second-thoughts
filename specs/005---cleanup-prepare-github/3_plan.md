# Implementation Plan — Cleanup & Prepare for GitHub

**Branch**: `005-cleanup-prepare-github`
**Date**: 2026-10-18
**Status**: Draft

## Summary
Make the repo publish-ready as **`dustinandrews/hermes-second-thoughts`**: remove internal scaffold, rename the plugin to `hermes-second-thoughts`, rewrite public docs (README, LICENSE, CHANGELOG), bump manifest to 0.2.0, prove git-installability locally, reinstall the live plugin under the new name, and push to GitHub (tag v0.2.0) once the user creates the empty repo.

## Technical Context
- Owner `dustinandrews` (SSH identity); repo to be **`hermes-second-thoughts`**.
- Plugin lives at `plugin/` subdir; manifest `plugin/plugin.yaml` currently `name: second-thoughts`, version 0.1.0, homepage `dustin-andrews/...`.
- No gh CLI, no PAT → user creates empty repo; push over SSH (id_ed25519 already authorized).
- Live install currently `~/.hermes/plugins/second-thoughts` (manifest name mismatch risk if we keep dir name; reinstall under dir = manifest name).
- Config file names (`~/.hermes/second-thoughts.yaml`, `-overrides.yaml`, `-blocks.jsonl`) are UNCHANGED by the rename.

## Design Decisions
- **DD-1** Keep local working dir `~/projects/second-thoughts` (dir name decoupled from repo/remote name); only remote URL + manifest + live install use `hermes-second-thoughts`.
- **DD-2** Manifest `name: hermes-second-thoughts`; reinstall live plugin at `~/.hermes/plugins/hermes-second-thoughts/` (dir = manifest name); enable `hermes-second-thoughts`; disable/remove old `second-thoughts` install.
- **DD-3** Keep public: README, LICENSE, CHANGELOG, AGENTS, MISFIRE, WHAT_AND_WHY, TECH_STACK (constitution VIII), plugin/, tests/, scripts/, specs/001-004.
- **DD-4** Delete from tree (kept in history): specs/000---example-sprint/, HANDOFF_RESUME.md, PRODUCT_PLAN.md.
- **DD-5** Version 0.2.0 in manifest + CHANGELOG; git tag v0.2.0 at merge.
- **DD-6** Test package string in tests stays `hermes_plugins.second_thoughts` (arbitrary loader name in tests; independent of manifest name) — OR update for consistency. Decision: leave as-is (no functional coupling; avoids churn). [reviewer: verify this doesn't break live install identity]
- **DD-7** Install-verify via local git URL (owner/repo/plugin path) before pushing.

## Project Structure (target public tree)
```
README.md  LICENSE  CHANGELOG.md  AGENTS.md  MISFIRE.md  WHAT_AND_WHY.md  TECH_STACK.md  .gitignore
plugin/ (plugin.yaml hermes-second-thoughts, second_thoughts.yaml, __init__.py, rules.py, overrides.py, audit.py)
tests/  scripts/install.sh  specs/ (001..004; 005 in progress)
```

## Tasks
- **T1** rename manifest: `plugin/plugin.yaml` name→`hermes-second-thoughts`, version→0.2.0, homepage→dustinandrews/hermes-second-thoughts, author→dustinandrews, description refresh.
- **T2** delete scaffold: `git rm specs/000---example-sprint/` files, `HANDOFF_RESUME.md`, `PRODUCT_PLAN.md`; confirm `TECH_STACK.md` + AGENTS + MISFIRE + WHAT_AND_WHY retained; confirm no cache tracked (SC-001).
- **T3** write `LICENSE` (MIT).
- **T4** write `CHANGELOG.md` (0.2.0, sprints 001-004 incl. rename).
- **T5** rewrite `README.md` (install from git + local, config files, behaviour, misfire, tests).
- **T6** verify installability: local git URL `hermes plugins install <owner>/hermes-second-thoughts/plugin` → validate installed copy; `pytest tests/ -q` 45; `hermes plugins validate ./plugin` clean.
- **T7** reinstall live plugin: `~/.hermes/plugins/hermes-second-thoughts/` (sprint-004 code), enable, retire old `second-thoughts`.
- **T8** tag `v0.2.0` at merge; add remote `git@github.com:dustinandrews/hermes-second-thoughts.git`; push `main` + tags; verify `git ls-remote` (after user creates empty repo).

## Review Result
STATUS: [PASS | FAIL]