# Tasks — Cleanup & Prepare for GitHub

**Branch**: `005-cleanup-prepare-github`
**Date**: 2026-10-18

## TASK LIST (by plan; RED/GREEN/validation framing applies to install/validate gates, not code)

### Phase 1 — Packaging: manifest rename + cleanup (FR-003, FR-001, SC-001)
- [ ] **T001** [P1] `plugin/plugin.yaml`: `name: hermes-second-thoughts`, `version: "0.2.0"`, `homepage: https://github.com/dustinandrews/hermes-second-thoughts`, `author: dustinandrews`, refresh description (execute_code, overrides, audit, misfire).
- [ ] **T002** [P1] delete scaffold: `git rm -r specs/000---example-sprint/`, `git rm HANDOFF_RESUME.md PRODUCT_PLAN.md`; verify `TECH_STACK.md`/`AGENTS.md`/`MISFIRE.md`/`WHAT_AND_WHY.md` retained; confirm `.gitignore` covers `__pycache__/`, `*.pyc`, `.pytest_cache/` (edit if not) and verify none of those are tracked (SC-001, FR-002).

### Phase 2 — Docs (US2, FR-004/FR-005, SC-002)
- [ ] **T003** [P1] add `LICENSE` (MIT).
- [ ] **T004** [P1] add `CHANGELOG.md` (0.2.0: sprints 001–004 + rename).
- [ ] **T005** [P1] rewrite `README.md`: what it does, install from git (`hermes plugins install dustinandrews/hermes-second-thoughts/plugin`) + local copy, config (`second_thoughts.yaml` defaults, `~/.hermes/second-thoughts.yaml` override, `~/.hermes/second-thoughts-overrides.yaml`, `~/.hermes/second-thoughts-blocks.jsonl`), behaviour (hard-block, `[rule: …]` + misfire escalation, fail-closed overrides), tests.

### Phase 3 — Verify installability + regression (FR-006, FR-009, SC-003)
- [ ] **T006** [P1] local git-install verify: `hermes plugins install <owner>/hermes-second-thoughts/plugin` via local git URL → installed copy passes `hermes plugins validate`.
- [ ] **T007** [P1] `pytest tests/ -q` → 45 passed; `hermes plugins validate ./plugin` → clean (FR-009).

### Phase 4 — Reinstall live plugin (FR-010)
- [ ] **T008** [P1] install under new name: `~/.hermes/plugins/hermes-second-thoughts/` (sprint-004 code + new manifest), `hermes plugins enable hermes-second-thoughts`; retire old `~/.hermes/plugins/second-thoughts`.

### Phase 5 — Publish (FR-007, FR-008, SC-004) — blocked on Dustin creating empty repo
- [ ] **T009** [P1] after user creates `dustinandrews/hermes-second-thoughts`: add remote, tag `v0.2.0` at merge, push `main` + tags, verify `git ls-remote git@github.com:dustinandrews/hermes-second-thoughts.git`.

## Review Result
STATUS: [PASS | FAIL]