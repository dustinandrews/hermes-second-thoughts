"""Append-only JSONL audit log of second-thoughts decisions.

Records every block and every override grant so bad detections can be found
by reading back what was blocked. Deliberately safe by construction:

* The audit NEVER influences the block decision. `append` swallows all
  write/trim errors (logs a warning) so a logging failure can never convert a
  block into a pass.
* The file stays bounded: when it exceeds a size cap it is trimmed to the
  newest N lines.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

_DEFAULT_FILE = "second-thoughts-blocks.jsonl"
_MAX_LOG_BYTES = 1_048_576  # 1 MiB
_KEEP_LINES = 5000
_PAYLOAD_CAP = 2000


def _audit_file() -> Path:
    home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    return home / _DEFAULT_FILE


def trim(path: Path) -> None:
    """If ``path`` exceeds the cap, rewrite it keeping the newest ``_KEEP_LINES``."""
    try:
        if path.stat().st_size <= _MAX_LOG_BYTES:
            return
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) <= _KEEP_LINES:
            return
        path.write_text("\n".join(lines[-_KEEP_LINES:]) + "\n", encoding="utf-8")
    except OSError:
        logger.warning("second-thoughts: could not trim audit log %s", path, exc_info=True)


def append(entry: Dict[str, Any], path: "Path | None" = None) -> None:
    """Append one entry. Never raises; never affects the caller's decision."""
    if path is None:
        path = _audit_file()
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        trim(path)
    except OSError:
        logger.warning(
            "second-thoughts: audit append failed; decision unaffected (%s)", path,
            exc_info=True,
        )