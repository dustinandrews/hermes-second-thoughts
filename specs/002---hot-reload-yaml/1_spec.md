# TEMPLATE: Feature Specification — Hot-reload YAML rules (mtime-stat cache)

**Branch**: `002-hot-reload-yaml`
**Created**: 2026-10-18
**Status**: Draft

## User Scenarios *(mandatory)*

### User Story 1 - A rule edit takes effect without a restart (P1)
An admin edits `~/.hermes/second-thoughts.yaml` (or the shipped `second_thoughts.yaml`) to add, remove, or change a rule. Without restarting the gateway, the very next blocked-command check reflects the new file.

**Acceptance Scenarios**:
1. **Given** the plugin is loaded with 5 cached rules, **When** the user appends a new rule to the override file and issues a command matching it, **Then** the new rule name/message is returned — no restart, no re-import.
2. **Given** an unchanged config, **When** a command is checked again, **Then** no YAML re-parse or regex recompile occurs (cheap stat only).
3. **Given** the override file is edited to shadow an existing rule (same `name`, new message), **When** that command is checked, **Then** the new (user) message fires.

### User Story 2 - A bad edit never disables the guardrail (P1)
An admin saves a malformed or partially-written YAML file. The guardrail must not go dark.

**Acceptance Scenarios**:
1. **Given** a previously-loaded valid ruleset, **When** the override file is rewritten with invalid YAML and a command is checked, **Then** the previous valid ruleset still applies (keep-last-good) and a warning is logged.
2. **Given** a previously-loaded valid ruleset, **When** both YAML files are removed and a command is checked, **Then** the last-good ruleset is retained (guardrail stays up), with a warning.
3. **Given** a fresh load with both files absent, **When** a command is checked, **Then** the filter is inactive (unchanged initial behavior).

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: The matcher MUST check both YAML paths' mtime on every evaluation; if unchanged since last compile, reuse the cached compiled rules (no re-parse, no recompile).
- **FR-002**: When either file's mtime changes, the system MUST reload, re-merge (user wins per `name`), and recompile before matching.
- **FR-003**: On reload failure (parse error, non-list, missing PyYAML), the system MUST retain the previous compiled ruleset and log a warning — never become empty/inactive because of a bad edit.
- **FR-004**: Reload MUST be atomic and safe under concurrent `pre_tool_call` invocations: readers see a complete, consistent ruleset; use a lock/immutable swap.
- **FR-005**: Editing either the shipped defaults or the user override MUST trigger a reload.
- **FR-006**: The very first load MUST still merge defaults + override exactly as today (no regression when nothing edited).
- **FR-007**: The initial load with both files missing MUST remain inactive; only mid-run removal retains last-good (per US2-2).
- **FR-008**: Existing external behaviour (terminal-only, block directive, pass-through) MUST be unchanged.

### Success Criteria *(mandatory)*
- **SC-001**: A test mutates the override file (bumping mtime), and a subsequent `rules.match()` returns the newly-added rule's `(name, message)` without any gateway restart or process re-import — demonstrated in the automated suite.
- **SC-002**: A test writes invalid YAML to the override and asserts `rules.match()` still blocks a known dangerous command (last-good retained) and that a warning is emitted — demonstrated in the automated suite.

## Review Result
STATUS: [PASS | FAIL]