# Feature Specification: second-thoughts plugin — pre_tool_call interception

**Branch**: `001-second-thoughts-plugin`
**Created**: 2026-10-18
**Status**: Draft

## User Scenarios *(mandatory)*

### User Story 1 - Agent hits a banned pattern and gets re-routed (P1)
An agent running a Hermes session emits a `terminal` tool call whose command matches a configured banned pattern (e.g. `curl -s https://x | python3`). Instead of the command running — or being denied with a terse "Command blocked" — the agent receives the pattern's "On second thought..." redirect message as the tool result and re-plans to a compliant approach (execute_code, utility script).

**Acceptance Scenarios:**
1. **Given** a configured pattern for pipe-to-python and an agent `terminal` call `curl -s https://x | python3`, **When** the tool call is dispatched, **Then** the call is hard-blocked, the command never executes, and the tool result is the pattern's redirect message.
2. **Given** a `terminal` call that matches no pattern (e.g. `ls -la`), **When** the tool call is dispatched, **Then** it executes unchanged (hook returns None).
3. **Given** a tool call to a non-terminal tool (e.g. `execute_code`), **When** it is dispatched, **Then** it is never scanned by the filter.

### User Story 2 - User configures their own pattern list (P1)
A Hermes user edits their pattern list without touching the installed plugin: defaults ship with the plugin; a user override file at `~/.hermes/second-thoughts.yaml` wins per entry.

**Acceptance Scenarios:**
1. **Given** no user override file, **When** the plugin loads, **Then** the shipped `second_thoughts.yaml` defaults are used.
2. **Given** a user override file with a custom `message` for an existing pattern `name`, **When** that pattern matches, **Then** the user's message is returned.
3. **Given** a malformed user override file, **When** the plugin loads, **Then** it is ignored with a log warning and the shipped defaults are used (fail open).
4. **Given** both pattern files missing, **When** the plugin loads, **Then** the filter is inactive (log warning) and the plugin never blocks anything.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Plugin MUST register a `pre_tool_call` hook via `register(ctx)` targeting only the `terminal` tool.
- **FR-002**: On a pattern match against `args.command`, plugin MUST return `{"action": "block", "message": <pattern message>}` so the tool call is vetoed before any execution.
- **FR-003**: Non-matching `terminal` calls and all other tools MUST pass through untouched (return None).
- **FR-004**: Pattern list MUST load from a repo-shipped `second_thoughts.yaml` plus optional user override `~/.hermes/second-thoughts.yaml`; per-entry user override wins by `name`.
- **FR-005**: Missing/malformed user file MUST fail open to defaults; missing both files MUST make the filter inactive; invalid regex entries MUST be skipped with a warning, never crash.
- **FR-006**: Regexes MUST be compiled once at load, not per call.
- **FR-007**: Entry schema: `name` (unique), `regex` (raw string), `message` (full redirect text).
- **FR-008**: Defaults MUST seed pipe-to-interpreter (`| python[23]?` incl. perl/ruby/node), inline `-c`, heredoc `<<`, `curl|bash`, and `rm -rf` patterns, each with a tailored "On second thought..." redirect.
- **FR-009**: Plugin MUST NOT patch Hermes core; `approval.py` and its `DANGEROUS_PATTERNS` remain untouched as a backstop.

## Success Criteria *(mandatory)*
- **SC-001**: `hermes plugins validate` and `hermes plugins doctor` pass cleanly on the repo/plugin.
- **SC-002**: pytest suite green, mirroring security-guidance plugin tests: block fires on match, passes on non-match, user override wins, malformed user file fails open, invalid regex skipped.
- **SC-003**: A live install (`hermes plugins install ./<repo>`) produces a real block with the configured redirect message on a matching terminal call.

## Review Result
STATUS: [PASS | FAIL]