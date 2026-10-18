"""second-thoughts plugin — intercept terminal tool calls and hard-block banned patterns.

Registers a ``pre_tool_call`` hook that scans only ``terminal`` calls. On a
pattern match against ``args.command`` it returns a block directive with the
per-pattern "On second thought..." redirect message, so the agent re-plans to
a compliant path (execute_code, utility script). The hook runs before
``approval.py``'s ``DANGEROUS_PATTERNS`` check, which stays untouched as a
backstop. Policy lives in YAML: shipped defaults in ``second_thoughts.yaml``
plus an optional user override at ``~/.hermes/second-thoughts.yaml`` (user
wins per entry). Always hard-blocks; nothing runs on a match.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from . import rules

logger = logging.getLogger(__name__)


def _on_pre_tool_call(tool_name: str = "", args: Any = None, **_: Any) -> Optional[Dict[str, str]]:
    """Block matching terminal/execute_code calls; None = pass through.

    `terminal` is scanned on `args.command`; `execute_code` on `args.code`.
    Both share the same compiled rule set (sprint 002 hot-reload applies to
    both). All other tools and non-matching payloads pass through untouched.
    """
    field = {"terminal": "command", "execute_code": "code"}.get(tool_name)
    if field is None:
        return None
    if not isinstance(args, dict):
        return None
    text = args.get(field)
    if not isinstance(text, str):
        return None
    hit = rules.match(text)
    if hit is None:
        return None
    name, message = hit
    logger.info("second-thoughts: blocked %s call matching rule '%s'", tool_name, name)
    return {"action": "block", "message": message}


def register(ctx) -> None:
    ctx.register_hook("pre_tool_call", _on_pre_tool_call)