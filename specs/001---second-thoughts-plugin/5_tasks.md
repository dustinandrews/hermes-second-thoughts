# Tasks

**Branch**: `001-second-thoughts-plugin`
**Date**: 2026-10-18

## Phase 1: Setup
- [x] T001 [P] Scaffold repo files per plan: `plugin.yaml`, `__init__.py`, `rules.py`, `second_thoughts.yaml`, `tests/test_second_thoughts.py`

## Phase 2: Rules engine (FR-004..007)
- [x] T002 [P] `rules.py`: load repo `second_thoughts.yaml` defaults; merge user override `~/.hermes/second-thoughts.yaml` (user wins per entry `name`); missing/malformed user file + missing both files fail open with warning; compile regexes once; invalid regex skip + warn
- [x] T003 [P] `rules.py` match API: `match(command) -> (name, message) | None` against compiled rules; non-terminal tools out of scope by design (checked in hook)

## Phase 3: User Story 1 — interception (FR-001..003, FR-009)
- [x] T004 [P] `__init__.py` `register(ctx)`: `pre_tool_call` hook; terminal-only; None for non-matches/other tools; `{"action": "block", "message"}` on match; no core patches (approval.py untouched)

## Phase 4: User Story 2 — defaults (FR-008)
- [x] T005 [P] Seed `second_thoughts.yaml`: pipe-to-interpreter (python/perl/ruby/node), inline `-c`, heredoc, `curl|bash`, `rm -rf`; each with tailored "On second thought..." redirect message

## Phase 5: Tests + validation (SC-001..003)
- [x] T006 [P] pytest suite mirroring security-guidance: block on match, pass on non-match, non-terminal untouched, override wins, malformed user file fails open, invalid regex skipped; `hermes plugins validate` + `hermes plugins doctor` clean; live install from path + real block check

## Review Result
STATUS: [PASS | FAIL]