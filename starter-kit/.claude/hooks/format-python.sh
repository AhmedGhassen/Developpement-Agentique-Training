#!/usr/bin/env bash
# GABARIT — atelier A5. Hook PostToolUse sur Edit|Write.
#
# Le chemin du fichier édité se lit dans tool_input.file_path, sur stdin.
# La variable $CLAUDE_FILE_PATHS n'existe pas : ne l'utilisez pas.
#
# Prérequis : jq et ruff. Installation : chmod +x .claude/hooks/format-python.sh
#
# Test manuel :
#   echo '{"tool_input":{"file_path":"app.py"}}' | .claude/hooks/format-python.sh

set -euo pipefail

FILE=$(jq -r '.tool_input.file_path // empty')
[[ -z "$FILE" ]] && exit 0
[[ "$FILE" == *.py ]] || exit 0
[[ -f "$FILE" ]] || exit 0

ruff format -- "$FILE"      >/dev/null 2>&1 || true
ruff check --fix -- "$FILE" >/dev/null 2>&1 || true

# On sort toujours en 0 : un formatage raté ne doit pas bloquer l'édition.
exit 0
