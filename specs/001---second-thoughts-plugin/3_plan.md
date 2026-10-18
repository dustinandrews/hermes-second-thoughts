# Implementation Plan

**Branch**: `001-second-thoughts-plugin`
**Date**: 2026-10-18
**Spec**: `specs/001---second-thoughts-plugin/1_spec.md`

## Summary
Build a standalone Hermes plugin that registers a `pre_tool_call` hook; on a `terminal` call whose `command` matches a YAML-configured banned pattern, it hard-blocks with the pattern's "On second thought..." redirect message — before approval.py runs (which stays untouched as backstop).

## Technical Context
- **Language**: Python 3.10+ (stdlib: re, pathlib, logging) + PyYAML
- **Dependencies**: PyYAML declared in plugin.yaml `python_dependencies` (`PyYAML>=6.0,<7`)
- **Storage**: none (config only — repo-shipped `second_thoughts.yaml` + optional `~/.hermes/second-thoughts.yaml`)
- **Project Type**: standalone plugin repo (no core patches)

## Project Structure
```
second-thoughts/            (repo root = plugin root, per security-guidance precedent)
├── plugin.yaml             manifest v2: name/version/license/homepage/tags,
│                           api_version, python_dependencies
├── __init__.py             register(ctx): pre_tool_call hook handler → rules API
├── rules.py                load YAML (defaults + user override), compile regexes once,
│                           match command → (name, message) | None
├── second_thoughts.yaml    shipped default patterns (pipe-to-interpreter incl.
│                           perl/ruby/node, -c inline, heredoc, curl|bash, rm -rf)
└── tests/
    └── test_second_thoughts.py   pytest; mirrors security-guidance test approach
```

## Task List
1. Scaffold repo files (`plugin.yaml`, `__init__.py`, `rules.py`, `second_thoughts.yaml`) — P1
2. Implement `rules.py`: YAML load/merge (user wins per entry), regex compile once, invalid regex skip+warn, missing/malformed user file fail open, match API — P1
3. Implement `__init__.py`: `register(ctx)` + `pre_tool_call` handler (terminal only, block directive on match, None otherwise) — P1
4. Seed `second_thoughts.yaml` defaults with per-pattern redirect messages — P1
5. Write pytest suite: block on match, pass on non-match, non-terminal untouched, override wins, malformed user file fails open, invalid regex skipped — P1
6. Validate + live-block checkout: `hermes plugins validate`, `hermes plugins doctor`, install from path, trigger a real block — P1

## Review Result
STATUS: [PASS | FAIL]