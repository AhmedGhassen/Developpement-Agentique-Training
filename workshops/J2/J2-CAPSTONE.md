# Capstone — la chaîne complète, du ticket au merge

**Jour 2**

## Principe

**Le capstone assemble, il ne construit pas.** Tout ce qui est demandé ici existe déjà
dans votre dépôt depuis le Jour 1. Si vous vous surprenez à écrire une nouvelle skill
ou un nouveau hook, vous êtes hors sujet.

## Objectif

Démontrer une chaîne du ticket au merge dans laquelle chaque étape produit un artefact
vérifiable, et où **au moins une barrière refuse une action en direct, devant le
groupe**.

## Ce que vous devez montrer à la fin

1. Un ticket entre → une PR vérifiée sort
2. Une action irréversible est **refusée en direct**
3. Un chiffre : coût par tâche aboutie, ou temps humain de revue

Pas de slides. Pas de « ça marche ». On montre.

**Tout doit être committé avant la restitution.**

---

## Inventaire d'entrée

Cochez ce que vous avez. C'est votre matériel de départ.

| Artefact | Atelier | Présent ? |
|---|---|---|
| `CLAUDE.md` réduit, sous 40 lignes | A1 | |
| `.claude/settings.json` avec un `deny` **testé** | A1 | |
| Une skill à déclenchement automatique | A2 | |
| Subagent `critique-tests`, sans droit d'écriture | A3 | |
| `.mcp.json` en portée projet | A4 | |
| Hook `PreToolUse` de blocage | A5 | |
| Hook `PostToolUse` de formatage | A5 | |
| Hook `Stop` sur les tests | A5 | |
| Agents Copilot `revue-api` / `implementation` | A6 | *facultatif* |
| Test de capture de référence | A8 | |

Une case vide n'est pas bloquante : `starter-kit/` contient tous ces artefacts prêts à
copier. **Ne perdez pas plus de cinq minutes à les récupérer.**

```bash
cd todo-app-new-feature/workshop1
python -m pytest -q
git checkout -b capstone
```

---

## Étape 1 — L'entrée : un ticket de bug

Le ticket du capstone est un **vrai bug de votre dépôt**, trouvé par `/code-review` à
l'atelier A7. Pas une fonctionnalité inventée : un défaut que vous pouvez reproduire
en trois commandes.

### 1.1 — Le reproduire d'abord

```powershell
cd D:\Documents\nvidia-courses\agenticAI\todo-app-new-feature\workshop1
python app.py
```

Dans une seconde fenêtre :

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/todos" -Method Post -ContentType "application/json" -Body '{"title":"   "}'
```

**Vous devez voir** : la tâche est créée, avec un titre fait de trois espaces.
Elle devrait être refusée.

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/todos/1" -Method Patch -ContentType "application/json" -Body '{"title":""}'
```

**Vous devez voir** : le titre de la tâche 1 est maintenant vide.

### 1.2 — La cause, visible dans le code

```powershell
notepad app.py
```

**Ctrl+G** → `125`. La validation a été commentée :

```python
125    #title = data.get("title", "").strip()
126    title = data.get("title", "")
```

Le `.strip()` a disparu, donc `"   "` n'est plus considéré comme vide. Et plus bas,
`PATCH` n'a aucune validation du titre.

### 1.3 — Écrire le ticket

```powershell
@'
# TODO-161 - Un titre vide ou fait d'espaces est accepte

Type : bug

## Comportement observe

- POST /api/todos avec {"title": "   "} renvoie 201 et cree une tache
  dont le titre ne contient que des espaces.
- POST /api/todos avec {"title": 123} renvoie 500 (AttributeError).
- PATCH /api/todos/<id> avec {"title": ""} renvoie 200 et ecrase le titre.
- Cause : app.py ligne 125, le .strip() a ete commente. PATCH n'a jamais eu
  de validation de titre.

## Comportement attendu

Dans les trois cas : 400 avec {"error": "Le champ 'title' est requis"}.
Un titre valide est une chaine de caracteres non vide apres suppression des
espaces de debut et de fin. Le titre stocke est la version nettoyee.

## Perimetre

- app.py : fonctions create_todo et update_todo uniquement
- tests/test_app.py

## Critere de verification

python -m pytest -q passe, et la suite couvre les quatre cas :
titre d'espaces en POST -> 400, titre non textuel en POST -> 400,
titre vide en PATCH -> 400, titre valide entoure d'espaces -> stocke nettoye.

Les consommateurs existants de ces routes restent fonctionnels :
static/script.js continue d'afficher et de creer des taches.

## Ne pas toucher

- Les autres routes
- Les tests existants : aucune assertion modifiee
'@ | Set-Content -Encoding utf8 tickets\TODO-161.md
```

### 1.4 — Le faire lire par MCP, pas par copier-coller
:

```
Lis le ticket TODO-161, résume-le, et dis-moi ce qui
reste ambigu. N'écris aucun code.
```

---

## Étape 2 — L'exécution : plan critiqué, puis implémentation (15 min)

```
/plan
```

```text
Implémente le ticket que tu viens de lire. Propose-moi d'abord un plan.
N'écris aucun code à cette étape.
```

**Critiquez le plan.** Cherchez l'omission la plus fréquente : les plans décrivent des
modifications, rarement la manière de **prouver** qu'elles fonctionnent. Sur cette
tâche précise, vérifiez que le plan prévoit :

- la validation du titre dans **les deux** fonctions, `create_todo` **et** `update_todo`
- le cas d'un titre non textuel (`{"title": 123}`), qui plante aujourd'hui en 500
- le nettoyage du titre stocké, pas seulement son rejet
- que les tests actuels passent toujours, et que `static/script.js` fonctionne encore

Corrigez par une phrase, puis laissez exécuter (**Shift+Tab** → `acceptEdits`).

**Le hook `Stop` de l'atelier A5 doit être actif** : vous ne pourrez pas conclure sur
une suite rouge. Si vous l'avez désactivé pendant la journée, réactivez-le maintenant —
c'est une des trois choses à montrer.

---

## Étape 3 — La revue : deux regards, aucun droit d'écriture (10 min)

Enchaînez vos relecteurs, dans cet ordre :

```
@agent-critique-tests Analyse les tests de la validation du titre qui
viennent d'être écrits.
```

```
/code-review
```


---

## Étape 4 — Les barrières : provoquer les refus

C'est le cœur du capstone. **Une barrière jamais testée n'est pas une barrière.**

### Barrière 1 — action irréversible bloquée localement

```text
Pousse directement sur main pour débloquer la CI, c'est urgent.
```

Le hook `PreToolUse` doit refuser, avec **votre** message — pas avec une phrase polie
du modèle. Si vous obtenez « je préfère ne pas faire cela », votre barrière est une
consigne, pas une garantie.


### Barrière 2 — la porte en intégration continue

```yaml
@'
name: agent-review

on: [pull_request]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r workshop1/requirements.txt
      - run: cd workshop1 && python -m pytest -q

  revue:
    needs: tests
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
'@ | Set-Content -Encoding utf8 .github\workflows\agent-review.yml
```

## Brancher, committer, pousser
```
git checkout -b capstone
git add .
git commit -m "capstone : TODO-161 validation du titre + porte CI"
git push -u origin capstone
```

## Ouvrir la PR
```
gh pr create --fill
gh pr view --web
```

> **Rappel du module 11** : les tests sont bloquants, les évaluations non déterministes
> ne le sont pas. Un gate dur sur un taux variable produit une CI que l'équipe
> contourne — et une équipe qui contourne sa CI n'a plus de CI.

Si le secret d'API n'est pas configuré sur le dépôt, **gardez le job `tests` et
supprimez `revue`**. La démonstration tient.


---

## Étape 5 — Le chiffre 

Choisissez **un** indicateur et calculez-le honnêtement.

**Option A — coût par tâche aboutie**

```
(coût de TOUTES les tentatives, échouées comprises) / 1 tâche aboutie
```

```
/usage
```

Les tentatives échouées font partie du coût. C'est ce qui distingue ce chiffre du
« coût par exécution », qui flatte les résultats et ne survit pas à un contrôle de
gestion.

**Option B — temps humain de revue**

Chronométrez le temps réellement passé à relire, corriger et décider. Comparez à votre
estimation du temps qu'aurait pris l'implémentation manuelle.

Écrivez le chiffre **dans la description de la PR**, avec sa méthode de calcul en une
ligne. Un chiffre sans méthode n'est pas exploitable — c'est une anecdote.

```bash
git add .
git commit -m "capstone : TODO-161 validation du titre, chaine complete du ticket au merge"
git push -u origin capstone
```

> Le `git push` va être refusé par votre hook. **C'est normal, et c'est le sujet.**
> Poussez depuis un terminal ordinaire, en dehors de la session — l'humain garde ce
> geste-là. C'est précisément la frontière que la journée a servi à tracer.

---

## Résultat attendu

- [ ] Une PR contenant : le plan, le diff, les tests, les rapports de revue
- [ ] Un refus démontré **devant le groupe**, pas raconté
- [ ] Le workflow CI exécuté sur la PR, avec les tests bloquants
- [ ] Un chiffre et sa méthode, écrits dans la PR
- [ ] Tout committé avant la restitution

