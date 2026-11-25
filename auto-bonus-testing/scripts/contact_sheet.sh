#!/bin/bash
# Runs contact_sheet.py in a private venv (created on first use) so Pillow never touches the system Python.
VENV="$HOME/.cache/auto-bonus-testing-venv"
[ -x "$VENV/bin/python" ] || { python3 -m venv "$VENV" && "$VENV/bin/pip" install --quiet pillow; } >/dev/null 2>&1
exec "$VENV/bin/python" "$(dirname "$0")/contact_sheet.py" "$@"
