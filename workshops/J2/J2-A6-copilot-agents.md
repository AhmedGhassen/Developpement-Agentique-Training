# Atelier A6 — Un binôme d'agents dans l'IDE

**Jour 2**

## Objectif

Reproduire dans GitHub Copilot le duo produire / juger construit au Jour 1, et
n'avoir qu'**une seule source de vérité** pour les instructions, partagée par
Claude Code et Copilot.

## Prérequis

- VS Code 1.109+, extensions GitHub Copilot et Copilot Chat connectées
- Le sélecteur d'agents du panneau Chat propose un mode agent et l'agent **Plan**
- Les artefacts du Jour 1 committés

---

## Étape 1 — Une seule source de vérité (15 min)

Créez `AGENTS.md` à la racine. Copiez `starter-kit/AGENTS.md` et adaptez-le.

La structure qui compte :

```markdown
Service de facturation. Python 3.12, FastAPI, PostgreSQL.

## Setup
uv sync --all-extras
docker compose up -d db

## Tests
pytest -q                     # unitaires — doivent passer avant tout commit
pytest -q -m integration      # nécessite la base locale

## Style
ruff format . && ruff check --fix .
Typage strict obligatoire sur src/.

## Boundaries
### Always
- Ajouter un test pour tout changement de comportement
- Mettre à jour CHANGELOG.md pour tout changement d'API publique
### Ask first
- Migration de schéma, ajout de dépendance, changement de contrat public
### Never
- Modifier src/billing/ledger.py sans validation d'un mainteneur
- Committer un secret, un .env, ou un dump de données
- Pousser directement sur main
```

Deux exigences de qualité :

- **Les commandes doivent être copiables-collables.** Un agent qui doit deviner entre
  `pytest` et `make test` perd des tours et échoue en CI.
- **La section `Never` nomme des chemins précis**, pas des principes. « Ne casse rien »
  n'est pas une limite ; « ne modifie pas `src/billing/ledger.py` » en est une.

Visez moins de 300 lignes.

### Faire converger avec Claude Code

Claude Code lit `CLAUDE.md`. Pour éviter deux vérités divergentes, réduisez votre
`CLAUDE.md` à une importation :

```markdown
@AGENTS.md

## Spécifique à Claude Code
- Les hooks de ce dépôt bloquent `git push` : c'est volontaire.
- Utiliser le subagent `critique-tests` après toute écriture de tests.
```

Vérifiez que ça fonctionne : ouvrez une session Claude Code et demandez
« quelle est la commande pour lancer les tests d'intégration ? ». La réponse doit
venir d'`AGENTS.md`.

---

## Étape 2 — L'agent de revue (15 min)

Créez `.github/agents/revue-api.agent.md` :

```markdown
---
name: revue-api
description: Revue des changements d'API publique et de compatibilité
model: GPT-5.2 (copilot)
tools: [search, codebase, fetch, problems, testFailure]
agents: []
handoffs:
  - label: Corriger les ruptures détectées
    agent: implementation
    prompt: Corrige uniquement les ruptures de compatibilité listées ci-dessus.
    send: false
---

Tu analyses les changements d'API publique de cette branche.

Pour chaque symbole exporté modifié, produis : signature avant, signature après,
verdict (compatible / rupture / ambigu), et impact sur les appelants.

Aucun avis de style, de nommage ou de lisibilité.

Si le diff ne touche aucune API publique, réponds exactement :
« Aucun changement d'API publique. » et arrête-toi.
```

Puis `.github/agents/implementation.agent.md` :

```markdown
---
name: implementation
description: Implémente un plan validé, avec les tests correspondants
tools: [search, codebase, editFiles, runCommands, problems, testFailure]
---

Tu implémentes un plan déjà validé. Tu ne redéfinis pas le périmètre.

Règles : un test pour tout changement de comportement ; respect strict des
conventions d'AGENTS.md ; aucune modification hors du périmètre du plan.

Si le plan te paraît incorrect, arrête-toi et dis pourquoi. Ne l'improvise pas.
```

Trois points à comprendre :

- **`agents: []`** ferme le périmètre : l'agent de revue ne peut pas déléguer.
- **`tools` sans `editFiles`** : c'est l'équivalent Copilot du `disallowedTools` du
  Jour 1. Un relecteur qui peut éditer cesse de relire.
- **`handoffs`** rend le relais explicite, avec `send: false` pour que vous gardiez
  la main sur le déclenchement.

Rechargez la fenêtre VS Code. Les deux agents doivent apparaître dans le sélecteur
du panneau Chat.

> Ces fichiers vivent dans `.github/agents/` pour l'équipe. Pour un usage personnel :
> `~/.copilot/agents`. Pour la compatibilité Claude Code : `.claude/agents`.
> Si vous avez d'anciens `.chatmode.md`, renommez-les en `.agent.md`.

---

## Étape 3 — Plan, critique, implémentation (20 min)

Dans le panneau Chat, tapez `/plan` puis la tâche T4 :

```
/plan Renomme le champ `amount` en `amount_cents` dans la réponse de l'API
publique des factures, et adapte les appelants internes.
```

**Critiquez le plan avant d'implémenter.** Cherchez :

- Le plan mentionne-t-il la **rupture de compatibilité** pour les consommateurs externes ?
- Prévoit-il une étape de vérification, ou seulement des étapes de modification ?
- Propose-t-il une transition (garder l'ancien champ en doublon) ou une rupture sèche ?
  Laquelle est adaptée ici — et le plan pose-t-il la question ?

Itérez sur le plan par une phrase, puis lancez **Start Implementation** en choisissant
l'agent `implementation`.

Une fois le diff produit, sélectionnez l'agent `revue-api` :

```
Analyse les changements d'API publique de cette branche.
```

**Résultat attendu** : le rapport nomme explicitement la rupture sur `amount`, avec
l'impact appelant. Utilisez ensuite le **handoff** « Corriger les ruptures détectées ».

### Le test de la sortie de secours

Créez une branche sans changement d'API (par exemple une correction de commentaire)
et relancez `revue-api`. Il doit répondre exactement « Aucun changement d'API publique. »

C'est le test qui révèle si l'agent respecte ses instructions ou s'il invente pour
ne pas rendre une réponse vide.

```bash
git add AGENTS.md CLAUDE.md .github/agents/ src/ tests/
git commit -m "atelier A6 : AGENTS.md unifié, agents revue-api et implementation"
```

---

## Résultat attendu

- [ ] Un `AGENTS.md` avec une section `Boundaries` en trois niveaux
- [ ] Un `CLAUDE.md` réduit à une importation d'`AGENTS.md`
- [ ] Les deux agents visibles dans le sélecteur du Chat
- [ ] `revue-api` nomme la rupture de compatibilité sur T4
- [ ] `revue-api` répond la phrase de secours sur un diff sans API
- [ ] Le handoff transmet le contexte sans copier-coller

## Pièges classiques

| Symptôme | Cause | Correction |
|---|---|---|
| L'agent de revue édite des fichiers | `editFiles` dans `tools` | Le retirer |
| Les agents n'apparaissent pas | Mauvais dossier, ou fenêtre non rechargée | `.github/agents/`, puis recharger la fenêtre |
| Instructions contradictoires | `AGENTS.md` et `CLAUDE.md` divergents | Un seul fichier de fond, l'autre l'importe |
| La revue produit du bruit de style | Pas d'interdiction explicite | « Aucun avis de style, de nommage ou de lisibilité » |
| Rapport inventé sur un diff propre | Pas de sortie de secours | Imposer la phrase exacte à répondre |
| Le handoff ne transmet rien | `send: false` mal comprise | `send: false` attend votre validation ; c'est voulu |

## Piste experte

**Comparaison croisée des deux outils.** Exécutez la **même** tâche T4 deux fois,
sur deux branches, dans les mêmes conditions de départ :

- Branche A : Claude Code (avec vos skills, subagents et hooks du Jour 1)
- Branche B : Copilot agent mode (avec vos deux agents et le plan agent)

Remplissez le tableau :

| | Claude Code | Copilot |
|---|---|---|
| Nombre de tours | | |
| Lignes de diff | | |
| Tests ajoutés | | |
| Rupture de compat. détectée | | |
| Temps humain de revue | | |
| Interventions correctives | | |

Puis répondez à une seule question : **sur quel type de tâche recommanderiez-vous
chacun, et pourquoi ?** Une phrase par outil, chiffres à l'appui.

Deuxième piste : définissez un **custom agent de planification** qui impose votre
gabarit de plan maison (par exemple : toujours une section « risques » et une section
« critères de vérification »). Comparez la qualité des plans avec l'agent Plan par défaut.

## Dépannage

**Le modèle indiqué dans le frontmatter n'est pas disponible** — retirez la ligne
`model` : l'agent utilisera le modèle courant. Les identifiants de modèles évoluent.

**Les agents de l'organisation n'apparaissent pas** — le réglage
`github.copilot.chat.organizationCustomAgents.enabled` doit être à `true`.

**Emplacements supplémentaires** — le réglage `chat.agentFilesLocations` permet
d'ajouter des dossiers de recherche, utile pour partager des agents entre plusieurs
dépôts sans les dupliquer.
