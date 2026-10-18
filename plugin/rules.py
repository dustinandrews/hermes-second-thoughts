"""Rule loading and matching for the second-thoughts plugin.

Loads the shipped ``second_thoughts.yaml`` defaults plus an optional user
override at ``$HERMES_HOME/second-thoughts.yaml`` (default ``~/.hermes``),
merges per entry by ``name`` (user wins), compiles regexes once, and matches
terminal commands. Fail-open: a missing or malformed user file falls back to
defaults; missing defaults make the filter inactive (empty rule set).
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

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


RULES: List[CompiledRule] = compile_rules(load_rules())


def match(command: str) -> Optional[Tuple[str, str]]:
    """First matching rule -> (name, message); None if no rule fires."""
    if not isinstance(command, str):
        return None
    for rule in RULES:
        if rule.matches(command):
            return rule.name, rule.message
    return None