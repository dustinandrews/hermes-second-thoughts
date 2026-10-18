# MISFIRE.md — When second-thoughts blocks something legitimately

second-thoughts hard-blocks commands/code that match its YAML rule set
(pipe-to-interpreter, inline `-c`, heredoc, `curl | bash`, `rm -rf`, and the
stay-out-of-/tmp rule), for both the `terminal` and `execute_code` tools. It
is a guardrail: it fires BEFORE the normal approval gate and nothing runs on a
match.

## The no-silent-workaround rule

If you hit a second-thoughts block, **do not quietly reword, re-route, or
work around the blocked command** (e.g. by splitting the string, wrapping it
in `sh -c`, or moving the offending text into a variable to dodge the regex).
That is exactly how a guard gets bypassed and how an unsafe action slips
through.

Instead: **stop, and report the misfire to the user.** Give them:

1. the rule that fired (it's in every block message: `[rule: <name>]`),
2. the full command/code that was blocked,
3. why you believe it is a false positive,
4. and the compliant path you intended.

Every block is written to the audit log at
`~/.hermes/second-thoughts-blocks.jsonl` (`action: "block"`), so the misfire
is already recorded.

## Making a legitimate action run: overrides

second-thoughts supports **narrow, human-authored overrides**. If Dustin
approves a specific payload, they (not the agent) add an entry to
`~/.hermes/second-thoughts-overrides.yaml`:

```yaml
- rule: rm-rf
  pattern: 'my_sandbox_cleanup'   # regex, matched against the blocked payload
  reason: "cleanup inside my own sandbox is safe"
```

Both the `rule` name AND the `pattern` regex must match the payload for the
override to grant. Overrides are consulted on every rule hit (hot-reloaded —
no restart), and each grant is written to the audit log
(`action: "override"`). Overrides FAIL CLOSED: a missing, empty, or malformed
override file means no grants — nothing is silently allowed.