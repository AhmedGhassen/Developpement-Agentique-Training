#!/usr/bin/env bash
# Journalise une ligne d'audit à la fin de chaque session d'agent.
#
# Objectif pédagogique (module 11) : les blocages de garde-fous sont une
# production de valeur. Sans journal, ils restent invisibles — et la sécurité
# reste un coût qu'on finit par supprimer pour aller plus vite.
#
# Installation : chmod +x .claude/hooks/audit.sh
# Sortie : .agent-audit.jsonl (à ajouter au .gitignore)

set -euo pipefail

PAYLOAD=$(cat)
FICHIER=".agent-audit.jsonl"

HORODATAGE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION=$(jq -r '.session_id // "inconnue"' <<< "$PAYLOAD")
BRANCHE=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "hors-git")

jq -n -c \
  --arg horodatage "$HORODATAGE" \
  --arg session "$SESSION" \
  --arg branche "$BRANCHE" \
  --argjson charge "$PAYLOAD" \
  '{
     horodatage: $horodatage,
     session: $session,
     branche: $branche,
     duree_s: ($charge.duration_seconds // null),
     tours: ($charge.num_turns // null),
     cout_usd: ($charge.total_cost_usd // null),
     raison_fin: ($charge.reason // null)
   }' >> "$FICHIER"

exit 0
