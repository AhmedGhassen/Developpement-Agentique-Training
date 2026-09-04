# Starter-kit — gabarits prêts à copier

Chaque fichier est un gabarit commenté. Les commentaires expliquent **pourquoi** le
fichier est écrit ainsi, pas seulement ce qu'il fait : ils sont là pour être lus une
fois, puis supprimés quand vous adaptez le gabarit à votre dépôt.

## Où copier quoi

```
votre-depot/
├── AGENTS.md                                  ← instructions partagées, source unique
├── CLAUDE.md                                  ← importe AGENTS.md + spécificités Claude Code
├── .mcp.json                                  ← serveurs MCP, portée projet, sans secret
├── .claude/
│   ├── settings.json                          ← permissions + hooks, versionné
│   ├── hooks/
│   │   ├── guard-bash.sh                      ← refuse les commandes interdites
│   │   └── audit.sh                           ← journalise la session
│   ├── skills/revue-securite/SKILL.md         ← skill à déclenchement automatique
│   └── agents/critique-tests.md               ← subagent critique, sans droit d'écriture
└── .github/
    ├── agents/
    │   ├── revue-api.agent.md                 ← agent Copilot de revue, avec handoff
    │   └── implementation.agent.md            ← cible du handoff
    └── workflows/agent-review.yml             ← CI : tests bloquants, revue informative
```

Fichiers hors dépôt, pour l'animation :

| Fichier | Usage |
|---|---|
| `ticket-hostile.md` | Démonstration d'injection de prompt (A4, A5, capstone) |
| `fiche-de-suivi.md` | À imprimer, un exemplaire par participant |
| `design/` | Maquette et spécification de secours pour l'atelier A8 |

## Après la copie, trois gestes obligatoires

```bash
chmod +x .claude/hooks/*.sh          # sinon les hooks échouent silencieusement
echo ".agent-audit.jsonl" >> .gitignore
```

Puis **testez vos garde-fous** :

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | .claude/hooks/guard-bash.sh
echo "code de sortie attendu : 2"
```

Une barrière jamais testée n'est pas une barrière. C'est la règle qui traverse les
deux jours.

## Adaptations à faire systématiquement

| Dans | Remplacer |
|---|---|
| `AGENTS.md` | Toutes les commandes, les chemins d'architecture, la section `Never` |
| `.claude/settings.json` | Les motifs `Bash(...)` selon votre gestionnaire de tâches |
| `hooks/guard-bash.sh` | La liste `INTERDITS` selon vos risques réels |
| `settings.json` → `Stop` | La commande de test : viser **moins de 30 secondes** |
| `.mcp.json` | Retirer les serveurs inutiles : chaque serveur coûte du contexte |
| `agent-review.yml` | L'axe unique de la revue, et le gestionnaire de dépendances |

## Ce qui ne doit jamais entrer dans ces fichiers

- Un jeton, un mot de passe, une chaîne de connexion — même de recette
- Un chemin absolu propre à votre poste
- Une règle qui n'a jamais été vérifiée sur le dépôt réel
