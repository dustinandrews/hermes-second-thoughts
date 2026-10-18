"""Rule loading, hot-reload, and matching for the second-thoughts plugin.

Loads the shipped ``second_thoughts.yaml`` defaults plus an optional user
override at ``$HERMES_HOME/second-thoughts.yaml`` (default ``~/.hermes``),
merges per entry by ``name`` (user wins), compiles regexes once, and matches
terminal commands against that compiled set.

Hot-reload (sprint 002): rules are cached by mtime. On every match we stat both
YAML paths; if unchanged we reuse the cached compiled rules (no re-parse, no
recompile); if either changed we reload+merge+recompile under a lock and swap
atomically. A failed reload (malformed/empty/removed config) never sends the
guardrail dark:

  * malformed override -> fail open to defaults (sprint-001 semantic), warning.
  * reload now empty (both removed/blank) after a prior good load -> retain the
    last-good ruleset, warning (a guardrail silently going inactive is the worst
    failure). The FIRST load with both absent remains inactive.

Public contract unchanged: ``match(command) -> (name, message) | None``.
"""

from __future__ import annotations

import logging
import os
import re
import threading
from pathlib import Path
from typing import Callable, List, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover - surfaced as a warning at read time
    yaml = None

logger = logging.getLogger(__name__)

_DEFAULT_RULES_FILE = Path(__file__).resolve().parent / "second_thoughts.yaml"


def _user_rules_file() -> Path:
    home = Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
    return home / "second-thoughts.yaml"


def _read_rules(path) -> List[dict]:
    """Read a rule list from a YAML file; missing/malformed yields []."""
    if path is None or not Path(path).exists():
        return []
    try:
        if yaml is None:
            raise RuntimeError("PyYAML is not installed")
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("second-thoughts: failed to read rules file %s (%s); failing open", path, exc)
        return []
    if not isinstance(data, list):
        logger.warning("second-thoughts: rules file %s is not a list; failing open", path)
        return []
    return [dict(item) for item in data if isinstance(item, dict)]


def load_rules(default_path=None, override_path=None) -> List[dict]:
    """Merge defaults + user override per entry by name; user wins."""
    defaults = _read_rules(default_path or _DEFAULT_RULES_FILE)
    override = _read_rules(override_path or _user_rules_file())
    if not defaults and not override:
        logger.warning("second-thoughts: no rules files found; filter inactive")
        return []
    by_name: dict = {r["name"]: r for r in defaults if r.get("name")}
    for r in override:
        if r.get("name"):
            by_name[r["name"]] = r
    return list(by_name.values())


class CompiledRule:
    """One compiled rule: name, compiled regex, redirect message."""

    def __init__(self, name: str, regex: "re.Pattern[str]", message: str) -> None:
        self.name = name
        self.regex = regex
        self.message = message

    def matches(self, command: str) -> bool:
        return bool(self.regex.search(command))


def compile_rules(raw: List[dict]) -> List[CompiledRule]:
    """Compile raw rule dicts; invalid regex is skipped with a warning."""
    compiled: List[CompiledRule] = []
    for r in raw:
        try:
            rx = re.compile(r["regex"])
        except (re.error, KeyError, TypeError) as exc:
            logger.warning(
                "second-thoughts: skipping rule %s — invalid regex %r: %s",
                r.get("name"), r.get("regex"), exc,
            )
            continue
        compiled.append(CompiledRule(r["name"], rx, r.get("message", "")))
    return compiled


class RuleStore:
    """mtime-stat cached rule set with keep-last-good and atomic swap.

    Thread-safe: reload runs under a lock and swaps an immutable tuple; readers
    snapshot the tuple once, so they never observe a torn/partial ruleset.
    """

    def __init__(
        self,
        default_path: Optional[Path] = None,
        override_path_provider: Optional[Callable[[], Path]] = None,
    ) -> None:
        self._default_path = Path(default_path) if default_path else _DEFAULT_RULES_FILE
        self._override_provider = override_path_provider or _user_rules_file
        self._lock = threading.Lock()
        self._rules: Tuple[CompiledRule, ...] = ()
        # (default_mtime_ns_or_None, override_mtime_ns_or_None); None = file absent
        self._mtimes: Optional[Tuple[Optional[int], Optional[int]]] = None
        self.reload_count = 0  # testability: number of actual reloads performed

    def _current_mtimes(self) -> Tuple[Optional[int], Optional[int]]:
        def get(path: Path) -> Optional[int]:
            try:
                return path.stat().st_mtime_ns
            except OSError:
                return None
        return (get(self._default_path), get(self._override_provider()))

    def _reload_if_changed(self) -> bool:
        """Reload when a file changed; returns True if a reload ran.

        On reload failure or an empty result after a prior good load, keep the
        last-good ruleset (guardrail never goes dark) and keep the aligned mtimes
        so we don't burn cycles retrying until the file actually changes again.
        """
        new = self._current_mtimes()
        if self._mtimes == new:
            return False
        self._mtimes = new
        try:
            raw = load_rules(default_path=self._default_path,
                             override_path=self._override_provider())
            compiled = compile_rules(raw)
        except Exception as exc:  # pragma: no cover - e.g. PyYAML truly missing
            if self._rules:
                logger.warning(
                    "second-thoughts: reload failed (%s); retaining last-good rule set", exc)
                return False
            self._rules = ()
            self.reload_count += 1
            return True
        if not compiled and self._rules:
            logger.warning(
                "second-thoughts: config is now empty after reload; retaining last-good rule set")
            return False
        self._rules = tuple(compiled)
        self.reload_count += 1
        return True

    def match(self, command: str) -> Optional[Tuple[str, str]]:
        """First matching rule -> (name, message); None if no rule fires."""
        if not isinstance(command, str):
            return None
        with self._lock:
            self._reload_if_changed()
            rules = self._rules  # immutable snapshot; safe to scan after the lock
        for rule in rules:
            if rule.matches(command):
                return rule.name, rule.message
        return None


# Module-level singleton used by the hook; created fresh per import.
store = RuleStore()


def match(command: str) -> Optional[Tuple[str, str]]:
    return store.match(command)