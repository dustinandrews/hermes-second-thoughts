# Product plan

This document contains the current direction for development. No more than five future items at a time.

## Important
Slice of bite-size items. If items are too complex, sub-divide rather than trying to do too much at once.

## 1. Scaffold plugin repo
- `plugin.yaml` (manifest v2: name/version/license/homepage/tags) + `__init__.py` with `register(ctx)`; layout that survives `hermes plugins install <owner>/second-thoughts`.
- git init + initial commit.

## 2. Config loading
- Ship `second_thoughts.yaml` defaults; load user override `~/.hermes/second-thoughts.yaml`. User file wins per-entry; malformed/missing file → fail open to defaults; missing both → filter inactive. Compile regexes once, not per call.

## 3. pre_tool_call interception
- Hook targets only `terminal`; scan `args.command`; on match return `{"action": "block", "message": "<per-pattern second thoughts>"}`. Non-matches and other tools pass through untouched.

## 4. Default pattern seed
- Pipe-to-interpreter (python/perl/ruby/node), inline `-c`, heredocs, `curl|bash`, `rm -rf` — each with a tailored "On second thought... use X instead" message mirroring the current DANGEROUS_PATTERNS + system-prompt bans.

## 5. Test suite + validation
- pytest mirroring security-guidance: block on match, pass on non-match, user override wins, malformed user file fails open, regex compile errors skipped with warning.
- `hermes plugins validate` + `hermes plugins doctor` clean; install via `hermes plugins install ./path` and confirm a live block.