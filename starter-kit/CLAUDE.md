@AGENTS.md

<!--
Une seule source de vérité : AGENTS.md, lu par Copilot, Codex, Cursor, Gemini CLI…
Ce fichier ne contient que ce qui est SPÉCIFIQUE à Claude Code.
Objectif : rester sous 30 lignes.
-->

## Spécifique à Claude Code

- Les hooks de ce dépôt refusent `git push`, `rm -rf` et les appels réseau depuis
  l'agent. C'est volontaire : ne cherchez pas à les contourner, signalez-le.
- Le hook `Stop` exécute un sous-ensemble rapide de tests. Une tâche ne peut pas
  être déclarée terminée sur une suite rouge.
- Après toute écriture de tests, invoquer le subagent `critique-tests`.
- Pour toute revue de sécurité, la skill `/revue-securite` s'applique.
- Sur une tâche ambiguë : produire un plan en mode `plan` avant tout diff.
