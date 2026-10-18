# second-thoughts

A [Hermes](https://hermes-agent.nousresearch.com) plugin that intercepts `terminal` tool calls and **hard-blocks banned patterns** with a per-pattern "On second thought..." redirect message — so the agent re-plans to a compliant path (execute_code, utility script) instead of retrying a terse denial.

- Runs via the `pre_tool_call` hook, **before** `approval.py`'s `DANGEROUS_PATTERNS` (which stays untouched as a backstop).
- **Always hard-blocks** on a match; non-matching commands and all non-terminal tools pass through untouched.
- Pattern list is **YAML-configurable**: shipped defaults + `~/.hermes/second-thoughts.yaml` user override (user wins per entry; malformed user file fails open to defaults).

## Install

From git (plugin lives in the `plugin/` subdir):

```
hermes plugins install <owner>/second-thoughts/plugin
hermes plugins enable second-thoughts
```

Local copy:

```
cp -r plugin ~/.hermes/plugins/second-thoughts
hermes plugins enable second-thoughts
```

Takes effect on the next session (or hot-reloads into a running gateway).

## Config

Copy `plugin/second_thoughts.yaml` to `~/.hermes/second-thoughts.yaml` and edit. Entry schema:

```yaml
- name: pipe-interpreter      # unique
  regex: '\|\s*(python[23]?)' # matched against the command text
  message: "On second thought, ..."  # redirect the agent receives
```

## Defaults seeded

- Pipe-to-interpreter (`| python`, `| perl`, `| ruby`, `| node`)
- Inline `-c` / `-e`
- Heredoc into an interpreter
- `curl|bash` / `wget|sh`
- `rm -rf` (force-recursive deletes)

## Dev

```
pytest tests/ -q            # 20 tests
hermes plugins validate ./plugin
hermes plugins doctor
```

## Project docs

- `WHAT_AND_WHY.md` — purpose and definition of success
- `PRODUCT_PLAN.md` — roadmap
- `specs/` — sprint artifacts (spec, plan, tasks, reviews) per the short-sprint method