# Changelog

All notable changes to **second-thoughts** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-10-18

### Added
- **Allow-overrides** (`~/.hermes/second-thoughts-overrides.yaml`): a
  human-authored, narrow exception that lets a *specific* payload through a
  rule (both the rule name and a regex pattern must match). Overrides **fail
  closed** — a missing, empty, or malformed file revokes all grants at once.
- **Audit log** (`~/.hermes/second-thoughts-blocks.jsonl`): a JSONL record of
  every block and every override grant (`ts`, `tool`, `rule`, `action`,
  `payload`, `message`). Bounded (1 MiB / 5000 entries); a write failure never
  changes the block decision.
- **Misfire escalation**: every block message now carries `[rule: <name>]`
  and the directive *"If you believe this is a misfire, stop and report it; do
  not work around it."*
- **`MISFIRE.md`** documenting the no-silent-workaround rule and the override
  flow.

### Changed
- The `pre_tool_call` hook now scans **`execute_code` `code` payloads** in
  addition to `terminal` commands.
- **PLUGIN RENAMED from `second-thoughts` to `hermes-second-thoughts`** for
  publication under `dustinandrews/hermes-second-thoughts`.

## [0.1.x] - 2026-10-18

### Added
- Standalone Hermes plugin that intercepts `terminal` calls and hard-blocks
  banned patterns with a per-pattern "On second thought…" redirect.
- YAML-configurable rule set (`plugin/second_thoughts.yaml` defaults + user
  override `~/.hermes/second-thoughts.yaml`, user wins per entry, fail open to
  defaults).
- Rules: `pipe-interpreter`, `inline-c`, `heredoc`, `curl-bash`, `rm-rf`.
- **Hot-reload** of the YAML rule set by mtime — rule edits take effect with
  no gateway restart (keep-last-good on a bad edit).
- Default rules extended with `execute-code-heredoc` and `tmp` (stay out of
  `/tmp`).
- Runs via the `pre_tool_call` hook before `approval.py`, which is retained as
  a backstop.