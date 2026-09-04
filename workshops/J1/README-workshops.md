# Guides d'atelier — développement agentique

Dix ateliers pas-à-pas, autonomes, réutilisables en interne module par module.
Chaque guide suit la même structure : objectif, durée, prérequis, étapes numérotées
**commande par commande**, prompts à coller tels quels, résultat attendu, pièges,
piste experte, dépannage.

## Index

| # | Atelier | Durée | Dépôt | Fichier |
|---|---|---|---|---|
| A1 | Baseline : instructions, permissions, plan mode, checkpoints | 50 min | todo-app | [J1-A1-baseline.md](J1-A1-baseline.md) |
| A2 | Écrire une skill qui se déclenche vraiment | 50 min | todo-app | [J1-A2-skill.md](J1-A2-skill.md) |
| A3 | Le duo constructeur / critique (subagents) | 55 min | todo-app | [J1-A3-subagents.md](J1-A3-subagents.md) |
| A4 | Brancher un MCP, et le tenir en laisse | 60 min | todo-app | [J1-A4-mcp.md](J1-A4-mcp.md) |
| A5 | Deux hooks qui changent la journée | 45 min | todo-app | [J1-A5-hooks.md](J1-A5-hooks.md) |
| A6 | Un binôme d'agents dans l'IDE (Copilot) | 55 min | — | [J2-A6-copilot-agents.md](J2-A6-copilot-agents.md) |
| A7 | Du ticket à la pull request, sans y toucher | 55 min | — | [J2-A7-delegation-pr.md](J2-A7-delegation-pr.md) |
| A8 | De la maquette au composant vérifié | 55 min | — | [J2-A8-design-browser.md](J2-A8-design-browser.md) |
| A9 | Orchestrer, puis mesurer (agent teams / fleet) | 50 min | — | [J2-A9-agent-teams.md](J2-A9-agent-teams.md) |
| — | Capstone : la chaîne complète | 55 min | — | [J2-CAPSTONE.md](J2-CAPSTONE.md) |

> **État de la mise à jour** : les cinq ateliers du **Jour 1** ont été réécrits sur le
> dépôt `todo-app`, avec toutes les commandes CLI et tous les prompts explicités. Les
> ateliers du Jour 2 sont encore écrits pour l'ancien dépôt de démonstration
> `billing-service` ; leurs tâches T4 à T6 ont un équivalent `todo-app` donné plus bas.

**Autre outillage** : pour animer avec Codex CLI ou Claude Desktop à la place de
Claude Code, voir [ANNEXE-Codex-Claude-Desktop.md](ANNEXE-Codex-Claude-Desktop.md) —
table d'équivalences, impact atelier par atelier, et répartition recommandée.

Prérequis d'installation : [../SETUP-PREREQUIS.md](../SETUP-PREREQUIS.md)
Gabarits à copier : [../starter-kit/](../starter-kit/)

---

## Le dépôt de travail

Les ateliers du Jour 1 sont écrits pour **`todo-app/workshop1`**, fourni avec la
formation :

- **Backend** Python 3.12 / Flask, données en mémoire, testé avec `pytest`
- **Frontend** HTML / CSS / JS vanilla, aucun build
- Une suite de sept tests dont **deux échouent au démarrage** — c'est volontaire, et
  c'est le matériau de l'atelier A1

### Démarrage

```bash
cd todo-app/workshop1
python -m venv .venv
source .venv/bin/activate          # Windows : .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q                # -> 2 failed, 5 passed
python app.py                      # -> http://localhost:5000
```

> **Toujours `python -m pytest`, jamais `pytest` seul** : `python -m` place le
> répertoire courant en tête de `sys.path`, sans quoi `from app import app` échoue.

### Ce que contient l'API

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/todos` | Liste, filtre `?completed=true|false` — **contient le bug** |
| POST | `/api/todos` | Créer (`{"title": "..."}`), 400 si titre vide |
| PATCH | `/api/todos/<id>` | Modifier `title` et/ou `completed`, 404 sinon |
| DELETE | `/api/todos/<id>` | Supprimer, 204 / 404 |

Trois choses à savoir, parce qu'elles reviennent dans plusieurs ateliers :

1. `todos` est une **liste globale mutable** — les tests se contaminent entre eux.
   C'est le constat que le critique de l'atelier A3 doit trouver.
2. Il n'y a **aucune authentification** — matériau de la skill de l'atelier A2.
3. `app.run(debug=True)` — autre constat de sécurité, gratuit et réel.

### Utiliser votre propre dépôt

**C'est possible, et même préférable pour l'ancrage.** Il doit alors satisfaire cinq
critères :

1. Une commande de test qui tourne en moins de 2 minutes
2. Un linter et un formateur configurés
3. Au moins une API publique (module exporté, endpoint HTTP) — nécessaire pour A6
4. Un composant d'interface, pour A8 (sinon utiliser la maquette fournie)
5. Aucune donnée de production, aucun secret réel

Remplacez alors les tâches T1–T6 par des tâches équivalentes de votre backlog. Les
critères de chaque tâche sont donnés ci-dessous pour vous permettre de choisir un
équivalent pertinent.

---

## Les tâches T1 à T6

Ces six tâches servent de support aux ateliers. Elles sont calibrées pour être
faisables dans le temps imparti, et pour révéler un comportement précis de l'agent.

### T1 — Correction guidée par un test + lecture simple (atelier A1)

> 1. `GET /api/todos?completed=true` renvoie l'inverse de ce qui est demandé.
>    Deux tests le prouvent déjà. Corriger `app.py` sans toucher aux tests.
> 2. Ajouter `GET /api/todos/<int:todo_id>` : la todo en JSON, ou 404 avec
>    `{"error": "Todo introuvable"}`. Deux tests.

*Ce que la tâche révèle* : la qualité du plan quand un test échoue déjà — l'agent
nomme-t-il la ligne fautive, ou annonce-t-il « corriger la logique » ? Et la
consommation de contexte d'une tâche de référence.

**Équivalent acceptable** : un bug prouvé par un test rouge, plus une route de
lecture sans effet de bord, le tout en 15 minutes.

### T2 — Logique métier testable (atelier A3)

> Ajouter `GET /api/stats` qui retourne `{total, completed, pending,
> completion_rate}`. `completion_rate` est un pourcentage arrondi à une décimale,
> et vaut `0.0` sur une liste vide. Ajouter les tests.

*Ce que la tâche révèle* : la faiblesse des tests générés. Cinq cas limites sont
presque toujours manquants :

| Cas | Piège |
|---|---|
| Liste vide | `ZeroDivisionError` |
| Toutes terminées | `100.0` jamais vérifié |
| Demi exact | `round(6.25, 1)` vaut **6.2** en Python, pas 6.3 |
| Cohérence | `pending == total - completed` jamais asserté |
| Ordre des tests | `todos` est global : un test qui code en dur `total == 4` passe seul et échoue dans la suite |

C'est le matériau du subagent critique.
**Équivalent acceptable** : toute règle de calcul avec division, arrondi et cas vide.

### T3 — Implémentation depuis un ticket externe (atelier A4)

> Le ticket `TODO-142` demande l'ajout d'un champ `priority` (`low` / `normal` /
> `high`, défaut `normal`), validé en POST et en PATCH, et filtrable via
> `GET /api/todos?priority=high`.
> L'agent doit lire le ticket **via MCP**, pas via un copier-coller.

*Ce que la tâche révèle* : l'utilité réelle de MCP, et le fait que les données issues
d'un système externe entrent dans le contexte **sans distinction de confiance** — ce
que le ticket piégé `TODO-207` démontre ensuite.

**Équivalent acceptable** : toute tâche dont la spécification vit dans Jira, GitLab,
Confluence, ou simplement dans un dossier lu par un serveur MCP `filesystem`.

### T4 — Rupture de compatibilité (atelier A6)

> Renommer le champ `title` en `label` dans les réponses de l'API `/api/todos`,
> et adapter `static/script.js`.

*Ce que la tâche révèle* : la valeur d'un agent de revue spécialisé. Une revue
générique ne verra pas que le front casse ; l'agent `revue-api` doit le nommer.

*Équivalent `billing-service`* : renommer `amount` en `amount_cents`.
**Équivalent acceptable** : tout changement de signature d'une API consommée ailleurs.

### T5 — Tâche déléguable (atelier A7)

> Ajouter la pagination sur `GET /api/todos` : paramètres `limit` (défaut 50,
> max 200) et `offset`. Réponse : `{items, total, next_offset}`. Comportement
> inchangé sans paramètre.

*Ce que la tâche révèle* : la relation directe entre la qualité de l'issue et la
qualité de la PR. C'est la tâche la plus spécifiable des six.

**Équivalent acceptable** : toute tâche que vous pourriez confier par écrit à un
stagiaire compétent, sans réunion.

### T6 — Orchestration (atelier A9)

Deux variantes, à choisir **après** le test d'indépendance :

- **T6-couplée** : « Uniformiser la gestion d'erreurs sur les 6 routes de `app.py`,
  avec un format d'erreur commun défini dans un nouveau module `errors.py`. »
- **T6-disjointe** : « Ajouter une docstring conforme et un test de chemin d'erreur
  pour chacune des 6 routes — chaque route est indépendante. »

*Ce que la tâche révèle* : le découpage multi-agents gagne sur T6-disjointe et perd
généralement sur T6-couplée. Le but de l'atelier est de le **mesurer**, pas de le croire.

---

## Fiche de suivi

Chaque participant remplit cette fiche au fil des ateliers. Elle est la matière
première des debriefs et de la restitution finale.

| Mesure | Atelier | Commande | Valeur |
|---|---|---|---|
| Contexte au démarrage | A1 | `/context` | |
| Contexte après réduction du CLAUDE.md | A1 | `/context` | |
| Contexte après T1 | A1 | `/context` | |
| Coût de la session A1 | A1 | `/usage` | |
| Impression spontanée sur les tests de T2 | A3 | — | |
| Contexte avant critique | A3 | `/context` | |
| Contexte après critique **avec** subagent | A3 | `/context` | |
| Contexte après critique **sans** subagent | A3 | `/context` | |
| Tests faibles trouvés par le critique | A3 | — | dont réels / bruit |
| Contexte avec serveurs MCP | A4 | `/context all` | delta vs A1 |
| Outils MCP exposés / utilisés | A4 | `/mcp` | |
| Le ticket piégé a-t-il été signalé ? tenté ? bloqué par quoi ? | A4 | — | |
| Blocages de hooks observés | A5 | — | |
| Tours & tokens — agent unique | A9 | `/usage` | |
| Tours & tokens — orchestration | A9 | `/usage` | |
| Coût par tâche aboutie | Capstone | `/usage` | tentatives échouées incluses |
| Temps humain de revue | Capstone | — | |

> Les chiffres n'ont pas besoin d'être précis. Ils ont besoin d'être **comparables
> entre eux**, mesurés dans les mêmes conditions.

---

## Aide-mémoire des commandes du Jour 1

### Terminal

```bash
claude                                   # ouvrir une session
claude --permission-mode plan            # ouvrir directement en mode plan
claude --agent critique-tests            # session entière sous un subagent
claude -p "..." --output-format json     # non interactif, avec coût et tours
claude doctor                            # configuration résolue, entrées invalides
claude --debug='hooks'                   # tracer les hooks
claude mcp list | get <n> | remove <n>   # gérer les serveurs MCP
claude mcp add --scope project <n> -- <cmd>
claude mcp add --transport http <n> <url>
```

### Dans la session

| Commande | Atelier |
|---|---|
| `/context`, `/context all` | A1, A3, A4 |
| `/usage` (alias `/cost`) | A1, A3, A5 |
| `/init`, `/memory` | A1 |
| `/permissions` | A1 |
| `/plan`, **Shift+Tab** | A1 |
| `/rewind` | A1 |
| `/status`, `/exit` | A1 |
| `/<nom-de-skill>`, `/security-review`, `/code-review` | A2 |
| `/agents`, `@agent-<nom>`, `/list-agents` | A3 |
| `/mcp`, `/mcp reconnect|enable|disable <nom>` | A4 |
| `/hooks`, `/config` | A5 |
| **Échap** | interrompre |

---

## Conseils d'animation

- **Faire échanger les binômes** à mi-atelier sur A2, A6 et A9 : c'est le seul test
  honnête d'une description de skill ou d'une issue déléguable.
- **Ne jamais sauver un participant bloqué** sur un piège documenté : le piège est
  l'exercice. Guider avec une question, pas avec la solution.
- **Faire committer** à chaque fin d'atelier. Le Jour 2 réutilise les artefacts du Jour 1.
- **Accueillir les résultats négatifs** : « l'orchestration n'a rien apporté » est
  une conclusion réussie si elle est chiffrée.
- **Faire tester les scripts de hook à la main** avant de les brancher (A5). Cinq
  minutes ici en font gagner vingt.
- **Prévoir les plans B** : accès Figma refusé (A8), quotas d'agents épuisés (A7),
  OAuth bloqué par le proxy (A4 — l'option `filesystem` ne demande aucun réseau).
  Chaque guide propose une porte de sortie.
