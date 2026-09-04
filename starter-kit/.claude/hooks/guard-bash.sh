#!/usr/bin/env bash
# GABARIT — atelier A5. Hook PreToolUse sur Bash.
#
# Contrat des hooks : la charge utile arrive en JSON sur stdin.
#   - la commande se lit dans tool_input.command
#   - code de sortie 0 = autorisé, 2 = REFUSÉ (seul 2 bloque ; 1 ne bloque pas)
#   - le message doit partir sur stderr, pas sur stdout
#
# Installation : chmod +x .claude/hooks/guard-bash.sh
#
# Test manuel, AVANT de brancher le hook :
#   echo '{"tool_input":{"command":"git push origin main"}}' | .claude/hooks/guard-bash.sh
#   echo $?      # doit valoir 2

set -euo pipefail

CMD=$(jq -r '.tool_input.command // empty')
[[ -z "$CMD" ]] && exit 0

INTERDITS=(
  'git push'
  'git reset --hard'
  'rm -rf'
  'chmod 777'
  'curl '
  'wget '
  'pip uninstall'
  'docker system prune'
  'DROP TABLE'
  'TRUNCATE'
)

for BAD in "${INTERDITS[@]}"; do
  if [[ "$CMD" == *"$BAD"* ]]; then
    echo "Refusé par la politique du dépôt : « $BAD » n'est pas autorisé depuis l'agent." >&2
    echo "Si cette action est réellement nécessaire, elle doit être faite par un humain." >&2
    exit 2
  fi
done

exit 0
