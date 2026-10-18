#!/usr/bin/env bash
# second-thoughts installer — installs PyYAML where the Hermes gateway can actually import it,
# and (optionally) drops the plugin into the Hermes plugins dir.
#
# WHY THIS EXISTS: `hermes plugins enable` and `hermes pm repair` install a plugin's
# python_dependencies into a per-install venv, but the gateway process runs plugins in an
# ISOLATED interpreter (-I) whose site-packages are separate. The plugin's rules engine needs
# PyYAML in THAT interpreter, or it logs "PyYAML is not installed; failing open" and the filter
# stays inactive. This script installs PyYAML directly into the gateway's interpreter.
#
# USAGE:
#   ./scripts/install.sh                         # ensure PyYAML in the gateway interpreter
#   ./scripts/install.sh --plugin                # also copy plugin/ into the Hermes plugins dir
#   HERMES_HOME=/custom/path ./scripts/install.sh
#
# Idempotent. Safe to re-run.
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- locate the gateway's interpreter under the Hermes tools dir ----------------------------
find_tools_python() {
    local d py
    for d in "$HERMES_HOME"/tools/python-*/bin; do
        if [[ -x "$d/python3" ]]; then
            py="$d/python3"
            # prefer a real venv-less interpreter that ships site-packages of its own
            if "$py" -c 'import sys; exit(0 if sys.prefix == sys.base_prefix else 1)' >/dev/null 2>&1; then
                printf '%s\n' "$py"
                return 0
            fi
        fi
    done
    return 1
}

TOOLS_PY="$(find_tools_python || true)"
if [[ -z "$TOOLS_PY" ]]; then
    echo "ERROR: could not find a Hermes tools python under $HERMES_HOME/tools (expected python-*/bin/python3)." >&2
    echo "Set HERMES_HOME if your install lives elsewhere, or install PyYAML into the python that runs 'hermes gateway'." >&2
    exit 1
fi
echo "Gateway interpreter: $TOOLS_PY"

# --- install / verify PyYAML ----------------------------------------------------------------
echo "Installing PyYAML (>=6.0,<7) into the gateway interpreter..."
"$TOOLS_PY" -m pip install --quiet 'PyYAML>=6.0,<7'

# Verify in the same isolated mode the gateway uses (-I).
if "$TOOLS_PY" -I -c 'import yaml, sys; sys.exit(0 if yaml.__version__.split(".")[0] == "6" else 1)'; then
    echo "OK: PyYAML importable in isolated mode ($("$TOOLS_PY" -I -c 'import yaml; print(yaml.__version__)'))."
else
    echo "ERROR: PyYAML failed to import in isolated mode after install." >&2
    exit 1
fi

# --- optional: copy the plugin into the Hermes plugins dir -----------------------------------
if [[ "${1:-}" == "--plugin" ]]; then
    DEST="$HERMES_HOME/plugins/second-thoughts"
    mkdir -p "$DEST"
    cp "$REPO_ROOT/plugin/plugin.yaml" "$REPO_ROOT/plugin/__init__.py" \
       "$REPO_ROOT/plugin/rules.py" "$REPO_ROOT/plugin/second_thoughts.yaml" "$DEST/"
    echo "Plugin files copied to $DEST"
fi

echo
echo "Done. Next: enable the plugin and restart the gateway so it re-imports with PyYAML available:"
echo "  hermes plugins enable second-thoughts    # if not already enabled"
echo "  hermes gateway restart                   # run outside the gateway (from a normal shell)"