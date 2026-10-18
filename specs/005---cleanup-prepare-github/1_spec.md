# Feature Specification — Cleanup & Prepare for GitHub

**Branch**: `005-cleanup-prepare-github`
**Created**: 2026-10-18
**Status**: Draft

## User Scenarios *(mandatory)*

### User Story 1 - The repo is clean and publish-ready (P1)
The working repo is tidied: build/cache artifacts ignored, internal session-scaffold docs removed from the public tree (kept in git history), and a single obvious layout that a fresh `hermes plugins install <owner>/second-thoughts/plugin` can consume.

**Acceptance Scenarios**:
1. **Given** the repo, **When** examined, **Then** there is no committed build cruft (no `__pycache__`/`.pyc`/`.pytest_cache`) and `.gitignore` covers them.
2. **Given** the public tree, **When** listed, **Then** it contains only product + engineering docs (`README`, `LICENSE`, `CHANGELOG`, `AGENTS`, `MISFIRE`, `WHAT_AND_WHY`, `plugin/`, `tests/`, `scripts/`, `specs/001-…-004`), with session-scaffold files (`HANDOFF_RESUME.md`, `PRODUCT_PLAN.md`, `TECH_STACK.md`, `specs/000---example-sprint/`) removed from the tree (recoverable from git history).
3. **Given** the `plugin/` subdir, **When** the manifest is read, **Then** it reports a released version and correct owner.

### User Story 2 - Proper public-facing documentation (P1)
A reader can install, configure (rules, user-override, allow-overrides, audit log), understand behaviour (hard-block + misfire escalation), and run tests — from the README and companion docs.

**Acceptance Scenarios**:
1. **Given** `README.md`, **When** read, **Then** it documents: what the plugin does, install from git + local, configuration (default rules, `~/.hermes/second-thoughts.yaml`, `~/.hermes/second-thoughts-overrides.yaml`, `~/.hermes/second-thoughts-blocks.jsonl`), behaviour (hard-block, `[rule: …]` + misfire escalation), and how to run tests.
2. **Given** `LICENSE`, **When** read, **Then** it is MIT (matches the manifest).
3. **Given** `CHANGELOG.md`, **When** read, **Then** it summarises sprints 001-004 under version 0.2.0.

### User Story 3 - Installable from git and published (P1)
The layout is proven installable via the `hermes plugins install <owner>/<repo>/<subdir>` path (verified locally), and the code is pushed to GitHub under `dustinandrews/second-thoughts`, tagged `v0.2.0`.

**Acceptance Scenarios**:
1. **Given** a local git URL for this repo, **When** `hermes plugins install` is pointed at `<owner>/second-thoughts/plugin`, **Then** the plugin installs and `hermes plugins validate` passes on the installed copy (layout is publish-ready).
2. **Given** the GitHub empty repo `dustinandrews/second-thoughts` (user-created), **When** the branch is pushed, **Then** `main` and tag `v0.2.0` appear on the remote and `git ls-remote git@github.com:dustinandrews/second-thoughts.git` shows them.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Remove session-scaffold/internal files from the tree: `specs/000---example-sprint/`, `HANDOFF_RESUME.md`, `PRODUCT_PLAN.md`, `TECH_STACK.md` (committed as deletions; recoverable in history). `AGENTS.md`, `MISFIRE.md`, `WHAT_AND_WHY.md` remain.
- **FR-002**: `.gitignore` covers `__pycache__/`, `*.pyc`, `.pytest_cache/`; verify nothing cached is tracked.
- **FR-003**: Bump `plugin/plugin.yaml` version `0.1.0` → `0.2.0`; set `homepage` to `https://github.com/dustinandrews/second-thoughts` (owner confirmed `dustinandrews`); refresh `description` to reflect execute_code interception, allow-overrides, audit log, and misfire escalation.
- **FR-004**: Rewrite `README.md` per US2 (fresh install → config → behaviour → tests), accurate current surface (45 tests).
- **FR-005**: Add `LICENSE` (MIT, matches manifest) and `CHANGELOG.md` (0.2.0 covering sprints 001-004).
- **FR-006**: Prove the git-install layout: `hermes plugins install <owner>/second-thoughts/plugin` against a local git URL succeeds and the installed copy validates.
- **FR-007**: Tag `v0.2.0` at the merge commit.
- **FR-008**: Push `main` + tags to `git@github.com:dustinandrews/second-thoughts.git` once the empty repo exists; verify via `git ls-remote`.
- **FR-009**: No functional/behaviour change to the plugin (regression: full suite stays green 45/45; `hermes plugins validate ./plugin` clean). Pure packaging/pub.

### Success Criteria *(mandatory)*
- **SC-001**: `git clean`-style inspection shows no tracked cruft and a sane tree; deletions are staged as removals (not blobs of content).
- **SC-002**: `README.md`, `LICENSE`, `CHANGELOG.md`, and `plugin/plugin.yaml` all present with accurate, consistent content (version 0.2.0, owner dustinandrews); docs reference the three config files accurately.
- **SC-003**: A local `hermes plugins install <owner>/second-thoughts/plugin` (via a local git URL) installs and the installed copy passes `hermes plugins validate`; `pytest tests/ -q` = 45 passed.
- **SC-004**: After the user creates the empty remote repo, push succeeds and `git ls-remote` shows `main` + `v0.2.0`; `hermes plugins doctor` lists the installed plugin.

## Review Result
STATUS: [PASS | FAIL]