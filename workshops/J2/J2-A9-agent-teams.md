# Atelier A9 — Orchestrer, puis mesurer

**Jour 2 · 15:05 – 16:00 · 50 min · binômes · orientation expert**

> **Dépôt de travail** : `todo-app-new-feature/workshop1` — 7 routes, 32 tests.
> **Outil** : Claude Code uniquement.

## Objectif

Produire une conclusion **argumentée et chiffrée** sur l'orchestration multi-agents,
fondée sur une mesure que vous avez faite — pas sur une intuition ni sur un billet de
blog.

Le résultat n'est pas connu d'avance. Sur une tâche couplée, l'agent unique gagne très
souvent. **Conclure « ça ne valait pas le coup » est une réussite de l'atelier.**

## Les trois mécanismes, et ce qui les distingue

C'est le point que presque tout le monde confond. Trois choses différentes :

| Mécanisme | Ce qu'il fait | Question à laquelle il répond |
|---|---|---|
| **Subagents** | L'agent principal lance des contextes isolés et récupère leurs rapports. **Ils ne se parlent pas.** | « Explore / analyse ces N choses indépendantes » |
| **Agent team** | Un lead et des teammates qui **s'échangent des messages** et se coordonnent | « Découpe cette tâche et coordonne les morceaux » |
| **`/batch`** | Applique la **même** transformation à N cibles, en parallèle | « Fais ce changement partout » |

Une équipe coûte des relais. Des subagents coûtent des lectures redondantes. `/batch`
ne coûte presque rien mais ne sait faire qu'une chose. **L'atelier consiste à mettre
un chiffre sur ces coûts.**

## Prérequis

```bash
cd todo-app-new-feature/workshop1
python -m pytest -q --ignore=tests/test_visuel.py        # doit être vert
git checkout main
```

Vérifiez ce que votre version expose :

```bash
claude --help | grep -i teammate
```

```
/list-agents
```

> Sur les versions plus anciennes, les équipes d'agents sont derrière un drapeau :
> `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (PowerShell :
> `$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"`).
> **Oublier ce drapeau et conclure « les équipes ne fonctionnent pas » est le piège
> n°1 de cet atelier.**

---

## Étape 1 — Le test d'indépendance (5 min)

**À faire à voix haute, avec votre binôme, avant de toucher au clavier.**

Une seule question : **les sous-tâches peuvent-elles avancer sans se parler ?**

Appliquez-la aux deux variantes de T6.

**T6-couplée** — « Uniformiser la gestion d'erreurs des 7 routes de `app.py` : créer
`errors.py` avec un format commun `{"error": ..., "code": ...}` et un helper, puis
l'appliquer partout. Adapter les tests existants. »

- Le format et le nom du helper doivent être décidés **avant** que les routes bougent.
- Tous les workers écrivent dans **le même fichier**, `app.py`.
- Verdict : *couplée*. Le découpage ajoute des relais pour zéro parallélisme réel.

**T6-disjointe** — « Créer un fichier de test par route : `tests/test_route_todos_get.py`,
`..._post.py`, `..._patch.py`, `..._delete.py`, `..._stats.py`, `..._categories.py`,
`..._index.py`. Chacun couvre le chemin nominal et au moins un chemin d'erreur de sa
route. Ne pas modifier `tests/test_app.py`. »

- Sept fichiers neufs, aucune décision partagée, aucun fichier commun.
- Verdict : *disjointe*. Le parallélisme est réel.

**Notez votre verdict par écrit avant de mesurer.** Vous le confronterez au résultat.

---

## Étape 2 — Exécution A : un seul agent bien outillé (12 min)

Prenez **T6-couplée** — c'est la variante qui produit le résultat contre-intuitif.

```bash
git checkout -B exp/a-agent-unique main
```

```bash
claude -p "Uniformise la gestion d'erreurs des 7 routes de app.py. Crée errors.py avec un format commun {error, code} et un helper, applique-le partout, adapte les tests. Termine par python -m pytest -q." \
  --permission-mode acceptEdits \
  --max-turns 60 \
  --output-format json > mesure-A.json
```

> **Pourquoi en non interactif ?** Parce que la sortie JSON contient le coût, le nombre
> de tours et la durée. C'est la seule façon d'avoir des chiffres comparables entre les
> trois exécutions. Une mesure au chronomètre avec des interventions humaines
> différentes ne compare rien.

Relevez :

```bash
python -c "import json;d=json.load(open('mesure-A.json'));print({k:d.get(k) for k in ('total_cost_usd','num_turns','duration_ms','is_error')})"
python -m pytest -q
git diff --stat main...HEAD
```

| Mesure | A · agent unique |
|---|---|
| Coût | |
| Tours | |
| Durée | |
| Tests passants | |
| Lignes de diff | |
| Tâche réussie (7 routes + suite verte) | |

---

## Étape 3 — Exécution B : subagents en parallèle (10 min)

```bash
git checkout -B exp/b-subagents main
claude --permission-mode acceptEdits
```

```
Uniformise la gestion d'erreurs des 7 routes de app.py.

Procède ainsi :
1. Lance en parallèle des subagents d'exploration, un par route, pour
   inventorier le format d'erreur actuel de chacune. Ils ne modifient rien.
2. À partir de leurs rapports, décide toi-même du format commun et écris
   errors.py.
3. Applique le format aux 7 routes et adapte les tests.

Termine par python -m pytest -q.
```

**Observez** : les subagents lisent tous `app.py` en entier. Sept lectures du même
fichier, sept contextes. C'est le coût de l'isolation quand la matière est petite —
l'inverse exact du bénéfice mesuré à l'atelier A3, où le fichier lu était gros et
la sortie petite.

```
/usage
```

---

## Étape 4 — Exécution C : équipe d'agents (13 min)

```bash
git checkout -B exp/c-equipe main
claude --teammate-mode in-process --permission-mode acceptEdits
```

```
Constitue une équipe pour cette tâche.

Un lead : il décide du format d'erreur commun, écrit errors.py, et le
documente en une ligne pour les autres.

Deux teammates : ils appliquent le format aux routes, quatre routes pour
l'un, trois pour l'autre. Ils attendent la décision du lead avant de
commencer.

Le lead valide le travail de chaque teammate avant de conclure, et lance
python -m pytest -q à la fin.
```

Surveillez pendant l'exécution, depuis un autre terminal :

```bash
claude agents
```

**Notez quatre choses que seule cette exécution montre :**

- Combien de messages ont été échangés entre agents ?
- Le lead a-t-il vraiment attendu, ou les teammates ont-ils démarré à vide ?
- Y a-t-il eu des **conflits d'écriture** sur `app.py` ? Les deux teammates y écrivent.
- Combien de fois une information a-t-elle dû être relayée d'un agent à l'autre ?

Relevez les mêmes mesures :

```
/usage
```

```bash
python -m pytest -q
git diff --stat main...HEAD
```

---

## Étape 5 — Le tableau, et la conclusion (10 min)

| | A · agent unique | B · subagents | C · équipe |
|---|---|---|---|
| Coût | | | |
| Tours | | | |
| Durée | | | |
| Tests passants | | | |
| Lignes de diff | | | |
| Interventions humaines | | | |
| Conflits / relais observés | — | | |

**Deux écarts à nommer explicitement :**

- **B − A** = le coût de l'isolation sur une tâche à petite matière. Généralement positif :
  vous payez sept lectures pour économiser zéro.
- **C − B** = le **coût de coordination pur**. Même découpage, mais avec messagerie.
  C'est le chiffre le plus intéressant de la journée, et presque personne ne le mesure.

Puis écrivez :

1. **Une phrase de conclusion**, chiffres à l'appui.
2. **Votre verdict de l'étape 1 était-il correct ?**
3. **Ce que vous recommanderez à votre équipe, et à quelle condition.**

Reportez sur la fiche de suivi.

```bash
git checkout main
```

---

## Résultat attendu

- [ ] Un verdict d'indépendance écrit **avant** la mesure
- [ ] Trois exécutions parties du **même** commit
- [ ] Le tableau rempli avec des chiffres réels, pas des impressions
- [ ] Les deux écarts B−A et C−B calculés et nommés
- [ ] Une conclusion en une phrase — y compris si elle est négative
- [ ] Une recommandation conditionnelle pour votre équipe

## Commandes vues dans cet atelier

| Commande | Rôle |
|---|---|
| `claude -p "…" --output-format json` | Exécution mesurable : coût, tours, durée dans la sortie |
| `--max-turns` · `--max-budget-usd` | Plafonner une exécution autonome |
| `--teammate-mode in-process\|auto\|tmux\|iterm2` | Activer et choisir le mode d'exécution des teammates |
| `claude agents` | Vue temps réel des agents en cours |
| `/list-agents` (alias `/peers`) | Les subagents et sessions joignables |
| `/batch <instruction>` | Appliquer la **même** transformation à N cibles en parallèle |
| `/tasks` | Travaux d'arrière-plan de la session |
| `--worktree <chemin>` | Isoler une exécution dans son propre arbre git |
| `/usage` | Coût et tokens de la session |
| `--effort low\|medium\|high\|xhigh\|max` | Régler l'effort — une variable de plus à contrôler entre exécutions |

## Pièges classiques

| Symptôme | Cause | Correction |
|---|---|---|
| « Les équipes ne marchent pas » | `--teammate-mode` absent, ou drapeau expérimental non posé | Vérifier avec `claude --help \| grep teammate` |
| Mesures incomparables | Points de départ différents, ou effort différent | `git checkout -B exp/... main` à chaque fois, et fixer `--effort` |
| Conflits d'écriture entre teammates | Deux workers sur `app.py` | **C'est un résultat, pas un bug.** Notez-le : c'est l'argument le plus solide contre le découpage d'une tâche couplée |
| L'orchestration « gagne » sans raison claire | Exécution A mal outillée | Refaire A avec vos hooks et subagents du Jour 1 |
| Confusion subagents / équipe / `/batch` | Trois mécanismes, trois questions | Relire le tableau du haut avant de mesurer |
| Le lead ne délègue pas | Prompt vague | Nommer explicitement le découpage **et** l'affectation, sinon vous obtenez un agent unique déguisé en équipe |
| Les teammates s'arrêtent sans rien produire | `maxTurns` trop bas, ou pas de droit `Edit` | Les restrictions du teammate s'ajoutent à `settings.json` |
| Aucune conclusion possible | Tâche trop petite | Élargir, ou passer à T6-disjointe |

## Piste experte

1. **L'inversion.** Refaites les trois mesures sur **T6-disjointe** — sept fichiers de
   test neufs, aucun fichier partagé.

   ```
   /batch Crée un fichier de test par route de app.py, nommé
   tests/test_route_<nom>.py, couvrant le chemin nominal et au moins un
   chemin d'erreur. Ne modifie pas tests/test_app.py.
   ```

   **La conclusion s'inverse-t-elle ?** Formulez ensuite la règle de décision qui
   découle de vos deux séries. Elle devrait ressembler à :

   > *Découper quand les sous-tâches ne partagent aucune décision et n'écrivent pas
   > dans les mêmes fichiers. Sinon, un agent unique bien outillé.*

2. **Worktrees : l'orchestration du pauvre.** Trois arbres, trois sessions
   indépendantes, fusion à la main :

   ```bash
   claude --worktree ../wt-1 --bg "Crée tests/test_route_todos_get.py et test_route_todos_post.py"
   claude --worktree ../wt-2 --bg "Crée tests/test_route_todos_patch.py et test_route_todos_delete.py"
   claude --worktree ../wt-3 --bg "Crée tests/test_route_stats.py, test_route_categories.py et test_route_index.py"
   ```

   Aucune messagerie, aucun lead, aucun conflit possible. **C'est souvent plus rapide
   et plus prévisible que l'orchestration automatique** — et cela mérite d'être su avant
   d'investir dans un système complexe.

3. **La chaîne d'agents spécialisés.** Le guide
   `todo-app-new-feature/workshop1/GUIDE-agents-team.md` décrit une chaîne de cinq
   subagents — `reviewer` → `ticket-creator` → `fixer` → `validator` → `committer` —
   où vous orchestrez à la main, une étape à la fois, en vérifiant chaque sortie.

   C'est le contre-modèle intéressant : **pas d'autonomie, mais un contrôle à chaque
   jonction.** Mesurez-le comme une quatrième exécution et comparez. La question à
   trancher : ce que vous perdez en vitesse, le gagnez-vous en fiabilité ?

4. **La variance, encore.** Refaites l'exécution qui a gagné, trois fois. L'écart entre
   les trois runs est-il plus grand que l'écart entre les trois stratégies ? Si oui,
   votre comparaison ne prouve rien, et c'est une conclusion honnête et importante.

## Dépannage

**`--teammate-mode` inconnu** — version trop ancienne : `claude update`. En attendant,
faites l'exécution C avec des subagents auxquels vous relayez vous-même les
informations : c'est le même découpage, avec vous en guise de messagerie.

**Impossible de comparer les coûts** — passez les trois exécutions en
`claude -p --output-format json`. `/usage` en interactif inclut vos propres messages,
ce qui fausse la comparaison.

**Une exécution part en boucle** — `--max-turns` et `--max-budget-usd` sont là pour ça.
Une exécution non plafonnée n'est pas une mesure, c'est un pari.

**Le mécanisme a changé de nom ou de statut** — c'est probable, il évolue vite. Le
raisonnement de l'atelier — test d'indépendance, puis mesure comparée depuis le même
commit — reste valable quel que soit le mécanisme disponible. C'est la méthode qu'il
faut emporter, pas la commande.
