# WHAT_AND_WHY.md

## PURPOSE
- Why does this project exist? LLM agents persistently reach for banned shell patterns (`cmd | python3`, heredoc, inline `-c`, `curl|bash`, `rm -rf`) despite system-prompt bans. Existing enforcement blocks with a terse "Command blocked" that doesn't re-route the agent, so it retries or stalls. second-thoughts intercepts before the block and redirects the agent with a friendly, actionable alternative — "On second thought, use code_exec or a utility script."
- Who will use it? Hermes users who want configurable, shareable guardrails over their agent's terminal usage; open-source consumers via `hermes plugins install`.
- Is it an MVP or V2? MVP (terminal-only interception, hard-block only).

## Example End User Scenario
The agent emits `curl -s https://x | python3`. second-thoughts intercepts the terminal call, returns "On second thought, you can't pipe stdin to python3. Use the execute_code tool or write a .py script and run it." The agent re-plans and uses a compliant path. `approval.py`'s hardcoded DANGEROUS_PATTERNS remain as a backstop in case a pattern the user hasn't configured slips through.

## What Success Looks Like
- A standalone, installable Hermes plugin repo (plugin.yaml + register(ctx)) that never patches core.
- Pattern list fully user-configurable via YAML (repo defaults + `~/.hermes/second-thoughts.yaml` override; user file wins; malformed user file fails open to defaults).
- Every configured match hard-blocks with its per-pattern "On second thought" redirect message; non-matches pass through untouched.
- pytest suite mirroring the built-in security-guidance plugin's tests: block fires on match, passes on non-match, override wins, malformed file fails open.