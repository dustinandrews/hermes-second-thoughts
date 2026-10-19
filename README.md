# hermes-second-thoughts

A [Hermes](https://hermes-agent.nousresearch.com) guardrail plugin that intercepts
`terminal` commands **and** `execute_code` payloads and **hard-blocks banned
patterns** with a per-pattern *"On second thought…"* redirect — so the agent
re-plans to a compliant path (a utility script, `read_file`, etc.) instead of
retrying a terse denial or sneaking around it.

- Runs via the `pre_tool_call` hook, **before** `approval.py`'s
  `DANGEROUS_PATTERNS`, which is retained untouched as a backstop.
- **Two tiers of guardrail:**
  - **Hard rules** (deterministic matches) always block; nothing runs.
  - A **misfire-escalation directive** is appended to every block message so
    the agent stops and *reports* a suspected false positive instead of
    working around the guard.
- **Human-authored allow-overrides** let a specific, false-positive payload
  through — narrow (rule *and* pattern must match) and **fail-closed**.
- **Audit log**: every block and override grant is recorded for detection.

## Install

The plugin lives in the `plugin/` subdirectory. From the published repo:

```sh
hermes plugins install dustinandrews/hermes-second-thoughts/plugin
hermes plugins enable hermes-second-thoughts
```

Local copy (no remote):

```sh
cp -r plugin ~/.hermes/plugins/hermes-second-thoughts
hermes plugins enable hermes-second-thoughts
```

> **Runtime dependency**: the plugin needs PyYAML in the gateway's isolated
> Python. `hermes plugins enable` normally handles plugin deps; if the hook
> reports itself inactive with "PyYAML is not installed", run
> `scripts/install.sh` (see below).
>
> A plugin **code** change takes effect after a gateway restart; YAML **rule
> and override** edits hot-reload with no restart.

## Configuration

Rule text is YAML: shipped defaults in `plugin/second_thoughts.yaml`, with an
optional user override at `~/.hermes/second-thoughts.yaml` (user wins per
entry by `name`). Both hot-reload by mtime.

Entry schema:

```yaml
- name: pipe-interpreter       # unique
  regex: '\|\s*(python[23]?)'  # matched against the command/code text
  message: "On second thought, ..."  # the redirect the agent receives
```

### Overrides (allow a false positive)

Human-authored at `~/.hermes/second-thoughts-overrides.yaml`:

```yaml
- rule: rm-rf                      # must match the rule that fired
  pattern: 'my_sandbox_cleanup'    # regex matched against the payload
  reason: "cleanup inside my own sandbox is safe"
```

Both `rule` and `pattern` must match the blocked payload for the override to
grant. Overrides are **fail-closed**: a missing, empty, or malformed file (or
a bad mid-run edit) revokes **all** grants.

### Audit log

Every block and every override grant is appended to
`~/.hermes/second-thoughts-blocks.jsonl` (one JSON object per line:
`{ts, tool, rule, action, payload, message}`). The `action` is `block` or
`override`. The log is bounded (1 MiB / 5000 newest entries) and a write
failure never changes the block decision.

## Behaviour & etiquette for agents

- On a match the hook returns a block directive; nothing executes.
- The block message ends with `[rule: <name>]` and the directive *"If you
  believe this is a misfire, stop and report it; do not work around it."* — do
  not silently reword or re-route around a guard. See [`MISFIRE.md`](./MISFIRE.md).

## Default rules seeded

- `pipe-interpreter` — `| python`, `| perl`, `| ruby`, `| node`
- `inline-c` — `python -c`, `perl -e`, …
- `heredoc` — heredoc into an interpreter (`python <<…`)
- `execute-code-heredoc` — `execute_code <<…`
- `curl-bash` — `curl|wget` piped into a shell
- `rm-rf` — force-recursive deletes
- `tmp` — stay out of `/tmp` (redirects to `~/.hermes/cache/scratch`)

## Develop

```sh
pytest tests/ -q              # full suite (45 tests)
hermes plugins validate ./plugin
hermes plugins doctor
```

`scripts/install.sh` installs PyYAML into the gateway's isolated interpreter
(its `-I` site-packages, not the plugin-host venv) and can copy the plugin
into place:

```sh
./scripts/install.sh --plugin
```

## Docs

- [`MISFIRE.md`](./MISFIRE.md) — no-silent-workaround rule + override flow
- [`WHAT_AND_WHY.md`](./WHAT_AND_WHY.md) — purpose and definition of success
- [`TECH_STACK.md`](./TECH_STACK.md) — dependencies and layout
- [`CHANGELOG.md`](./CHANGELOG.md) — release history
- [`AGENTS.md`](./AGENTS.md) — instructions for agent contributors
- `specs/` — sprint artifacts (spec, plan, tasks, reviews) per the short-sprint
  method