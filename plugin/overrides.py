"""Human-authored allow-exceptions (overrides) for second-thoughts.

An override lets a *specific* payload through a matching rule when BOTH the
rule name AND a user-supplied regex match the payload. Overrides are
human-authored and narrow — never a global per-rule kill-switch.

FAILURE SEMANTICS (opposite of ``rules.py`` block-rules):

* Block rules (``RuleStore``) keep last-good on a malformed edit so a
  guardrail never goes dark.
* Overrides (this module) FAIL CLOSED: a missing, empty, or malformed
  override file yields NO grants, and a mid-run malformed/empty edit revokes
  ALL grants at once. Grants can silently disable a guard, so on any doubt we
  must not retain stale grants.
"""

from __future__ import annotations

import logging
import os
import re
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_FILE = "second-thoughts-overrides.yaml"


def _user_overrides_file() -> Path:
    home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    return home / _DEFAULT_FILE


def _compile_overrides(raw: Any) -> List[Dict[str, Any]]:
    """Turn validated raw entries into a list of compiled-override dicts.

    Each: ``{"rule": str, "pattern": compiled-regex, "reason": str}``.
    A regex that fails to compile is skipped with a warning (a bad override
    pattern must fail closed to "no grant", never crash the check).
    """
    compiled: List[Dict[str, Any]] = []
    if not isinstance(raw, list):
        return compiled
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        rule = entry.get("rule")
        pattern = entry.get("pattern")
        if not isinstance(rule, str) or not rule:
            continue
        if not isinstance(pattern, str) or not pattern:
            continue
        try:
            cre = re.compile(pattern)
        except re.error as exc:
            logger.warning(
                "second-thoughts: skipping override for rule '%s' (bad pattern: %s)", rule, exc
            )
            continue
        compiled.append(
            {
                "rule": rule,
                "pattern": cre,
                "reason": entry.get("reason", ""),
            }
        )
    return compiled


class OverrideStore:
    """mtime-stat cached store of compiled overrides; FAILS CLOSED on doubt.

    Mirrors the RuleStore reload shape (stat both on every check, reload under
    a lock when changed, atomic swap) but with OPPOSITE failure semantics: any
    missing/empty/malformed file OR malformed mid-run edit yields an EMPTY
    grant set (no keep-last-good). This is deliberate: overrides only disable
    a guard, so we must never retain a stale grant.
    """

    def __init__(self, path_provider=None) -> None:
        self._path_provider = path_provider or _user_overrides_file
        self._lock = threading.Lock()
        self._mtime_ns = 0.0
        self._size = -1
        self._overrides: List[Dict[str, Any]] = []

    def _stat(self) -> Optional[tuple]:
        try:
            st = self._path_provider().stat()
        except OSError:
            return None
        return (st.st_mtime_ns, st.st_size)

    def _reload(self) -> None:
        path = self._path_provider()
        raw: Any = None
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except OSError:
            raw = None        # missing/unreadable -> no grants (fail closed)
        except yaml.YAMLError:
            raw = None        # malformed -> no grants (fail closed)
            logger.warning(
                "second-thoughts: malformed overrides file %s; all grants revoked (fail closed)", path
            )
        # None from safe_load means empty doc -> [] is "; also malformed",
        # but an empty-but-valid list is also fine to treat as no grants.
        if raw is None:
            raw = []
        self._overrides = _compile_overrides(raw)

    def match(self, payload: str, rule_name: str) -> bool:
        """True iff a compiled override matches BOTH rule_name and payload."""
        path = self._path_provider()
        stat = self._stat()
        if stat is None:
            # file absent now -> drop grants (fail closed)
            with self._lock:
                if self._overrides:
                    self._overrides = []
            return False
        mtime, size = stat
        if mtime != self._mtime_ns or size != self._size:
            with self._lock:
                # re-check under lock to avoid double reload
                cur = self._stat()
                if cur and (cur[0] != self._mtime_ns or cur[1] != self._size):
                    self._mtime_ns, self._size = cur
                    self._reload()
        for ov in self._overrides:
            if ov["rule"] == rule_name and ov["pattern"].search(payload):
                return True
        return False


# module-level singleton used by the hook (mirrors rules.store)
store = OverrideStore()