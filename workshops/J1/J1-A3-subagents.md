# Atelier A3 — Le duo constructeur / critique

**Jour 1**

> **Dépôt de travail** : `todo-app/workshop1`, branche `atelier-agentique`,
> ateliers A1 et A2 committés.

## Objectif

Démontrer **par la mesure** que l'isolation de contexte est le bénéfice premier du
subagent, et qu'une contrainte d'outillage — pas une consigne — produit un vrai
critique.

Le résultat que vous devez obtenir : un test que vous auriez validé, et dont le
critique démontre qu'il ne teste rien.

## Prérequis

- A1 et A2 terminés, `python -m pytest -q` au vert
- Un binôme disponible pour l'étape de tri

---

## Étape 1 — Produire la tâche T2

### 1.1 — Passer en mode d'édition automatique

**Shift+Tab** jusqu'à `acceptEdits`, ou relancez la session :

```bash
claude --permission-mode acceptEdits
```

### 1.2 — Le prompt T2 — à coller tel quel

```text
Ajoute la route GET /api/stats à app.py.

Elle retourne un JSON avec quatre clés :
- total : nombre total de tâches
- completed : nombre de tâches terminées
- pending : nombre de tâches non terminées
- completion_rate : pourcentage de tâches terminées, arrondi à une décimale

Si la liste est vide, completion_rate vaut 0.0.

Ajoute les tests correspondants dans tests/test_app.py.
```

### 1.3 — Vérifier que ça passe

```bash
python -m pytest -q
```

---

## Étape 2 — Créer le subagent critique (10 min)

### 2.1 — Le dossier

**PowerShell**

```powershell
New-Item -ItemType Directory -Force .claude\agents | Out-Null
```

**bash**

```bash
mkdir -p .claude/agents
```

### 2.2 — Le fichier `.claude/agents/critique-tests.md`

```markdown
---
name: critique-tests
description: >
  Cherche activement les failles d'une suite de tests : cas non couverts,
  assertions faibles, tests qui passeraient même si le code de production
  était cassé. À invoquer après l'écriture de tests, avant la revue humaine.
tools: Read, Grep, Glob, Bash
disallowedTools: Edit, Write
model: sonnet
permissionMode: plan
maxTurns: 25
---

Tu es un relecteur adversarial. Ton objectif n'est pas de valider la suite
de tests : il est de démontrer qu'elle est insuffisante.

Pour chaque test, réponds à une question précise : **quelle mutation du code
de production laisserait ce test passer ?** Si tu en trouves une, le test est
faible — dis-le, et donne la mutation exacte sous forme de diff minimal.

Cherche systématiquement :

- les assertions qui vérifient l'absence d'erreur plutôt qu'un résultat
- les valeurs limites absentes : zéro, liste vide, seuil exact, 100 %
- les arrondis non testés, et le comportement de `round()` sur un demi exact
- les chemins d'erreur non couverts
- les tests dont le résultat dépend de l'état laissé par les tests précédents
- les tests qui dupliquent un cas déjà couvert sans rien ajouter

Termine par la liste des comportements du code qui ne sont couverts par
aucun test, classés par risque.

Ne propose aucun correctif : tu diagnostiques, tu ne répares pas.

Format de chaque constat, une ligne :

tests/test_app.py:92 — test_stats_returns_rate — mutation : remplacer
`round(x, 1)` par `round(x)` laisse ce test passer — sévérité : faible.

S'il n'y a rien à signaler, réponds exactement :
« Cette suite de tests résiste aux mutations que j'ai essayées. »
puis liste les mutations tentées.
```

### 2.3 — Les trois lignes qui font le comportement

- **`disallowedTools: Edit, Write`** — un critique qui peut corriger cesse de
  critiquer. La contrainte d'outillage crée le comportement plus fiablement que la
  consigne dans le prompt.
- **`permissionMode: plan`** — verrouillage supplémentaire en lecture seule.
- **`maxTurns: 25`** — un critique sans limite peut explorer indéfiniment.

> **`tools` prend des noms d'outils**, pas des motifs de permission :
> `tools: Read, Grep, Glob, Bash`. Les motifs (`Bash(pytest *)`) s'écrivent dans
> `.claude/settings.json`, et les restrictions du subagent **s'ajoutent** à celles du
> projet.

### 2.4 — Vérifier qu'il est reconnu

Dans la session, tapez le caractère `@` dans la barre de saisie.

**Vous devez voir** `critique-tests` proposé dans l'autocomplétion.
@
---


## Étape 3 — Invoquer le critique et trier

### 3.1 — Mesurer avant

```
/context
```

Notez le chiffre.

### 3.2 — Invoquer explicitement

Le `@` garantit que **ce** subagent tourne, au lieu de laisser l'agent choisir :

```text
@agent-critique-tests Analyse les tests de GET /api/stats qui viennent
d'être écrits, dans tests/test_app.py.
```


### 3.3 — Mesurer après

```
/context
```

Notez le second chiffre.

### 3.4 — Trier les constats, en binôme

| Constat | Réel | Bruit | Bloquant ? |
|---|---|---|---|

Cherchez en particulier si le critique a trouvé les cinq pièges de T2 :

| Piège | Pourquoi il compte |
|---|---|
| **Liste vide** | `completed / total` lève `ZeroDivisionError`. Le test l'a-t-il couvert ? |
| **100 %** | Aucun test ne vérifie généralement le cas où tout est terminé |
| **Arrondi à un demi exact** | `round(6.25, 1)` vaut **6.2** en Python, pas 6.3. Arrondi « au pair le plus proche ». Un test sur 1 tâche terminée sur 16 le révèle |
| **Cohérence interne** | `pending == total - completed` n'est presque jamais asserté |
| **État partagé entre tests** | `todos` est une liste **globale mutable**. Les tests POST des tests précédents l'ont grossie. Un test qui code en dur `total == 4` passe seul et échoue dans la suite complète |

Le dernier est le plus intéressant : c'est un défaut de la suite **existante**, pas
du code que l'agent vient d'écrire. Vérifiez-le vous-mêmes :

```bash
python -m pytest -q tests/test_app.py::test_stats_totals
python -m pytest -q
```

Le risque existe dans l'application — la liste est bien partagée, c'est un fait. Mais les tests ne tombent pas dedans, parce que Claude ne code aucun chiffre en dur : il recalcule le total à chaque fois.


---

## Étape 4 — Itérer sur les constats bloquants

### 4.1 — Appliquer, et seulement les bloquants

Dans la session principale :

```text
Ajoute les tests manquants pour ces trois cas uniquement :
1. liste de tâches vide -> completion_rate vaut 0.0 et aucune exception
2. toutes les tâches terminées -> completion_rate vaut 100.0
3. 1 tâche terminée sur 16 -> vérifie la valeur exacte que produit
   round(6.25, 1) en Python, et documente-la dans le test

Ajoute aussi une fixture pytest qui restaure l'état de la liste todos
entre chaque test, pour que le résultat ne dépende plus de l'ordre.

N'ajoute rien d'autre. Ne modifie pas les assertions des tests existants.
```

### 4.2 — Vérifier

```bash
python -m pytest -q
python -m pytest -q -p no:randomly tests/test_app.py
```

### 4.3 — Relancer le critique

```text
@agent-critique-tests Reprends ton analyse de tests/test_app.py après
les corrections.
```

**Résultat attendu** : les constats bloquants ont disparu, et il en reste
probablement de nouveaux, moins graves. C'est normal et sain : le critique descend
en sévérité, il ne s'épuise pas.

---

## Étape 5 — La mesure qui compte

### 5.1 — La même critique, sans subagent

Dans la session principale, sans `@` :

```text
Pour chaque test de tests/test_app.py, dis-moi quelle mutation du code de
production le laisserait passer. Ne corrige rien.
```

### 5.2 — Troisième mesure

```
/context
```

### 5.3 — Le tableau

| Mesure | Valeur |
|---|---|
| Contexte avant critique | |
| Contexte après critique **avec** subagent | |
| Contexte après critique **sans** subagent | |

**L'écart entre les deux dernières lignes est le bénéfice de l'isolation, en
tokens.** Reportez-le sur la fiche de suivi.

Complétez avec le coût :

```
/usage
```

### 5.4 — Committer

```bash
git add .claude/agents/ app.py tests/
git commit -m "atelier A3 : subagent critique et tests renforces"
```

---

## Commandes vues dans cet atelier

| Commande | Rôle |
|---|---|
| `@` dans la barre de saisie | Voir les subagents disponibles dans l'autocomplétion |
| `@agent-<nom>` | **Forcer** l'exécution d'un subagent précis |
| `/list-agents` (alias `/peers`) | Lister les subagents et sessions joignables |
| `claude --agent critique-tests` | Ouvrir une session entière sous ce subagent |
| `/context` | Les trois mesures de l'atelier |
| `/usage` | Le coût correspondant |
| `/tasks` | Suivre les travaux lancés en arrière-plan |

## Frontmatter d'un subagent : les champs qui servent

| Champ | Effet |
|---|---|
| `name`, `description` | Requis. La description décide de la délégation automatique |
| `tools` | Noms d'outils autorisés. Hérite de tout si absent |
| `disallowedTools` | Outils retirés — **le vrai verrou** |
| `model` | `sonnet`, `opus`, `haiku`, ou `inherit` |
| `permissionMode` | `plan` pour un critique en lecture seule |
| `maxTurns` | Garde-fou contre l'exploration sans fin |
| `skills` | Skills préchargées dans son contexte au démarrage |
| `background: true` | Le laisse tourner en arrière-plan |
| `isolation: worktree` | Lui donne son propre worktree git |


