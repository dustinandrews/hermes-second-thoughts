# Feature Specification — Overrides + Audit Log + Misfire Escalation

**Branch**: `004-overrides-audit-log`
**Created**: 2026-10-18
**Status**: Draft

## User Scenarios *(mandatory)*

### User Story 1 - Human override for a false positive (P1)
A legitimate command/code that matches a rule gets hard-blocked (a false positive). Dustin approves a **narrow, specific** exception and the payload runs; everything else still hard-blocks.

**Acceptance Scenarios**:
1. **Given** a rule hit whose payload matches an approved override entry (`rule` name AND a regex matched against the payload), **When** the pre_tool_call hook runs, **Then** it returns `None` (payload passes) and writes an `override` audit entry.
2. **Given** the same payload but NO matching override (removed/mismatched) **or** a missing/malformed overrides file, **When** the hook runs, **Then** it hard-blocks with the rule's message and writes a `block` audit entry. The guard rail is never silently disabled.

### User Story 2 - Audit trail of every block (P2)
Every hard-block (and every override grant) is recorded so bad detections can be found by reading back what was blocked.

**Acceptance Scenarios**:
1. **Given** a block or an override grant, **When** it happens, **Then** an entry `{ts, tool, rule, action, payload, message}` is appended to the audit log.
2. **Given** the audit log, **When** it is read externally (cat/aggregator), **Then** the fields are structured (JSONL, one per line) and the file stays bounded (rotation/trim).
3. **Given** an audit-log WRITE failure, **When** the hook runs, **Then** the block still fires (a logging failure must never convert a block into a pass).

### User Story 3 - Agent escalates misfires instead of working around them (P1)
The agent is told, and the block message reminds it, to STOP and report a suspected misfire rather than silently rewording to dodge the guard.

**Acceptance Scenarios**:
1. **Given** any block, **When** the message is delivered, **Then** it carries the rule name AND a misfire-escalation suffix ("If you believe this is a misfire, stop and report it; do not work around it.").
2. **Given** the project docs, **When** an agent reads them, **Then** there is an explicit declaration that the agent must not silently reword/re-route around a second-thoughts block, and must surface suspected misfires to the user.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: A human-authored overrides file is consulted for EVERY rule hit BEFORE the block fires; a matching override lets that specific payload through.
- **FR-002**: An override entry names the `rule` AND a `pattern` (regex); BOTH must match the blocked payload to grant an override. Overrides are user-authored (never agent-authored) and specific (not a per-rule kill-switch, no global allowlist).
- **FR-003**: Missing, empty, or malformed overrides → NO overrides granted; all rules still hard-block (fail toward block/safety). Overrides FAIL CLOSED: a mid-run malformed/empty override file revokes ALL grants (never retain stale grants). This is the opposite of the block-rules' keep-last-good (fail-open-to-last-good) semantics: block rules preserve their last-good rule set on a bad rule edit; OVERRIDES, being grants that can silently disable a guard, revoke everything on any bad edit. An override that is being revoked is revoked at once.
- **FR-003a**: The overrides file is `$HERMES_HOME/second-thoughts-overrides.yaml` (`~/.hermes/second-thoughts-overrides.yaml` by default). No shipped defaults; purely user-authored.
- **FR-004**: Every block AND every override grant appended to an audit log as JSONL entries `{ts, tool, rule, action, payload, message}` at `$HERMES_HOME/second-thoughts-blocks.jsonl`.
- **FR-005**: An audit-log write failure NEVER changes the block decision (log the error, still block or still grant-override per the override decision); the hook never raises on log failure.
- **FR-006**: Overrides hot-reload by mtime like the rules (sprint 002); the audit log is opened lazily append-only.
- **FR-007**: Audit log is bounded (append cap / trim) to avoid unbounded growth; does not depend on external tools (stdlib only).
- **FR-008**: Every block message is suffixed with the rule name and the misfire-escalation directive.
- **FR-009**: Docs (AGENTS-style) declare the no-silent-workaround rule and the misfire report flow.
- **FR-010**: Both `terminal` and `execute_code` are covered; existing block/pass behaviour unchanged except logging (which now also writes audit entries). Non-matching payloads and other tools remain `None` with no audit write.

### Success Criteria *(mandatory)*
- **SC-001**: A rule hit with a matching override passes (`None`) and writes an `override` entry; the same payload with the override gone writes a `block` entry. Verified by the automated suite inspecting the audit log.
- **SC-002**: Missing / empty / malformed overrides still hard-block (no grant) — INCLUDING a mid-run edit that makes a previously-loaded override file malformed/empty (all grants revoked at once) — and the full suite stays green.
- **SC-003**: Audit log grows only on real block/override events; it is JSONL-parsable, bounded after trimming, and a forced write-failure does not pass a would-block (unit-forced).
- **SC-004**: A sample block message contains the rule name and the escalation suffix.
- **SC-004a**: The repo contains an agent-facing doc (e.g. README "Agent behaviour" or a dedicated MISFIRE doc) asserting the no-silent-workaround rule and the misfire report flow (FR-009); verified by reading the file(s).
- **SC-005**: Editing the override file (add/remove an entry) is picked up by the live hook with no restart (hot-reload), demonstrated in an isolated HERMES_HOME; a mid-run malformed edit revokes all grants (fail closed).

## Review Result
STATUS: [PASS | FAIL]