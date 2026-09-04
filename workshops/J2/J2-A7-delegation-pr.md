# Atelier A7 — Du ticket à la pull request, sans y toucher

**Jour 2 · 55 min · individuel** · Dépôt : `todo-app-new-feature/workshop1` · Outil : **Claude Code**

## Objectif

Confier une tâche à un agent, ne pas intervenir pendant qu'il travaille, puis juger ce
qu'il rend.

**Ce que vous allez découvrir** : l'agent respecte le ticket à la lettre, tous les
tests passent — **et l'application est cassée.** C'est prévu, et c'est la leçon.

## Ce dont vous avez besoin

Rien de plus que Claude Code et Python. Aucun compte, aucun droit, aucune installation.

> Une variante avec `@claude` sur GitHub existe en **annexe A**, en fin de guide.
> Elle demande 20 à 30 minutes de mise en place et n'apprend rien de plus sur les
> agents. Ne la faites pas pendant l'atelier.

---

# Étape 0 — Préparer

### 0.1 — Ouvrir le dossier

```powershell
cd D:\Documents\nvidia-courses\agenticAI\todo-app-new-feature\workshop1
```

### 0.2 — Vérifier que tout est vert

```powershell
python -m pytest -q
```

**Vous devez voir** : `32 passed` (ou plus).

### 0.3 — Créer la branche de travail

```powershell
git checkout -b atelier-a7
```

### 0.4 — Lancer l'application dans une SECONDE fenêtre PowerShell

```powershell
cd D:\Documents\nvidia-courses\agenticAI\todo-app-new-feature\workshop1
python app.py
```

**Laissez cette fenêtre ouverte** pendant tout l'atelier.

### 0.5 — Ouvrir la page

Dans votre navigateur : **http://localhost:5000**

**Vous devez voir** : la liste des tâches, avec leurs badges de catégorie.
**C'est l'état de départ. Retenez-le.**

---

# Étape 1 — Écrire le ticket

### 1.1 — Créer le dossier

```powershell
New-Item -ItemType Directory -Force tickets | Out-Null
```

### 1.2 — Créer le fichier du ticket

Copiez ce bloc **en entier** dans PowerShell, d'un seul coup :

```powershell
@'
# TODO-150 - Pagination de GET /api/todos

## Comportement attendu

Deux parametres nouveaux :
- limit  : entier, defaut 50, max 200. Au-dela -> 400
- offset : entier, defaut 0. Negatif -> 400

La reponse devient : {"items": [...], "total": N, "next_offset": N ou null}
total = nombre de taches apres filtrage, avant pagination.
Les filtres completed / category / priority restent cumulables.

## Perimetre

- app.py, fonction get_todos uniquement
- tests/test_app.py
- static/script.js n'est PAS dans le perimetre

## Critere de verification

python -m pytest -q passe, et couvre : defaut, limit=2, limit=201 -> 400,
offset negatif -> 400, derniere page avec next_offset null,
cumul ?completed=false&limit=1, total coherent avec le filtrage.

## Ne pas toucher

- Les autres routes
- Les tests existants : aucune assertion modifiee
'@ | Set-Content -Encoding utf8 tickets\TODO-150.md
```

> `@'` doit être en fin de ligne et `'@` tout au début de sa ligne, sans espace avant.
> Si ça ne marche pas : `notepad tickets\TODO-150.md` et collez le texte à la main.

### 1.3 — Vérifier

```powershell
Get-Content tickets\TODO-150.md
```

### 1.4 — Ce que ce ticket contient vraiment

**Trois modifications**, et personne ne le signale :

| # | Modification | Casse quelque chose ? |
|---|---|---|
| 1 | `limit` + validation | non, purement additif |
| 2 | `offset` + validation | non, purement additif |
| 3 | **la réponse passe de liste à objet** | **oui, pour tous les appelants** |

Gardez ce tableau en tête. On y revient à l'étape 5.

---

# Étape 2 — Relire son propre ticket

Avant de déléguer, répondez **par écrit** aux trois questions. Créez le fichier :

```powershell
@'
# Relecture de TODO-150

1. Un developpeur pourrait-il l'implementer sans poser de question ?
   ->

2. Quel test ecrirais-je en premier ?
   ->

3. Qu'est-ce qui reste ambigu ?
   ->
'@ | Set-Content -Encoding utf8 tickets\RELECTURE.md
```

```powershell
notepad tickets\RELECTURE.md
```

Remplissez les trois réponses, enregistrez, fermez.

> **Règle** : si vous ne savez pas écrire le critère de vérification, la tâche n'est
> pas prête à être déléguée — elle est prête à être planifiée.

**Astuce** : faites relire votre ticket par une session neuve, qui ne sait rien du
contexte :

```powershell
claude -p "Lis tickets/TODO-150.md et le code du depot. Qui, dans ce depot, appelle GET /api/todos et casserait si la reponse passait d'une liste a un objet ? Ne code rien."```

---

# Étape 3 — Déléguer

### 3.1 — Lancer la session détachée

```powershell
claude --bg --max-turns 40 "Implemente integralement tickets/TODO-150.md, tests compris. Ne touche pas a static/. Termine par python -m pytest -q."
```
Donc le seul fait de remplacer jsonify(result) par jsonify({...}) dans app.py change la forme de la réponse pour tous ceux qui appellent la route

**Vous devez voir** : un identifiant de session, et la main vous est rendue aussitôt.
C'est normal — la session travaille en arrière-plan.

> `--max-turns 40` veut dire « arrête-toi après 40 aller-retours, quoi qu'il arrive ».
> Un tour = l'agent réfléchit, lance un outil, reçoit le résultat. Sans plafond, une
> session que personne ne surveille peut tourner longtemps pour rien.

### 3.2 — Voir où elle en est

```powershell
claude agents
```

### 3.3 — Lire ce qu'elle fait

```powershell
claude logs <id>
```

Remplacez `<id>` par l'identifiant affiché par `claude agents`.

### 3.4 — Si besoin

```powershell
claude attach <id>     # reprendre la main dessus
claude stop <id>       # l'arreter
```

### 3.5 — La règle de l'atelier

**Vous ne touchez pas au code pendant qu'elle travaille.** C'est inconfortable, et
c'est l'exercice.

---


# Étape 4 — Constater

### 4.1 — Les tests

```powershell
python -m pytest -q
```

**Vous devez voir** : tout est vert.

### 4.2 — L'application

Retournez dans le navigateur, sur **http://localhost:5000**, et rechargez la page
(**Ctrl+F5**).

**Vous devez voir** : **une page vide.** Aucun message d'erreur à l'écran.

> Si l'application ne répond plus, c'est que la fenêtre de l'étape 0.4 s'est arrêtée.
> Relancez-y `python app.py`.

### 4.3 — Ouvrir la console du navigateur

Appuyez sur **F12**, puis onglet **Console**.

**Vous devez voir** :

```
Uncaught (in promise) TypeError: todos.forEach is not a function
    at renderTodos (script.js:61)
```

### 4.4 — Comprendre : ce que la route renvoyait AVANT

Une **liste**, entre crochets. Vous pouvez le revoir sur la branche d'origine :

```powershell
git stash
git checkout main
python app.py                      # dans la seconde fenetre, relancez
curl.exe "http://localhost:5000/api/todos"
```

**Vous devez voir** :

```json
[
  {"id": 1, "title": "Préparer le workshop", "completed": true},
  {"id": 2, "title": "Relire le ticket", "completed": false}
]
```

### 4.5 — Comprendre : ce qu'elle renvoie MAINTENANT

Revenez sur votre branche et relancez l'application :

```powershell
git checkout atelier-a7
git stash pop
python app.py                      # dans la seconde fenetre
curl.exe "http://localhost:5000/api/todos?limit=2"
```

**Vous devez voir** un **objet**, entre accolades, avec la liste rangée dedans :

```json
{
  "items": [
    {"id": 1, "title": "Préparer le workshop", "completed": true},
    {"id": 2, "title": "Relire le ticket", "completed": false}
  ],
  "total": 4,
  "next_offset": null
}
```

> Sous PowerShell, écrivez bien **`curl.exe`** et pas `curl` : `curl` seul est un alias
> PowerShell qui affiche autre chose.


### 4.7 — Les trois lignes fautives

```powershell
notepad static\script.js
```

Allez aux lignes 55, 60 et 61 :

```js
55   const todos = await res.json();   // recupere les données de l'API
60   listEl.innerHTML = "";            // vide l'ecran -> reussit
61   todos.forEach((todo) => {         // parcourt le l'objet -> plante
```

**L'écran est blanc parce que la ligne 60 réussit avant que la ligne 61 échoue.**
Imagine que le code fasse l'inverse : d'abord recréer les lignes, puis effacer l'ancienne liste. Le plantage arriverait avant l'effacement. Donc l'ancienne liste resterait affichée à l'écran.

### 4.8 — Laquelle des trois modifications a cassé ?

La **modification 3**.

Les modifications 1 et 2 sont additives : sans paramètre, le comportement est
identique. La 3 change le contrat pour **tout le monde**, y compris ceux qui
n'utilisent aucun paramètre.

**Un ticket qui mélange de l'additif et du rupturier fait passer le rupturier
inaperçu.**

### 4.9 — Le correctif — à ne PAS appliquer

Il tiendrait en un mot, ligne 56 de `script.js` :

```js
renderTodos(todos.items)     // au lieu de renderTodos(todos)
```

**Ne le faites pas.** C'est le ticket suivant. Le constat vaut mieux que la correction.

Fermez `notepad` sans enregistrer.

---

# Étape 5 — Faire relire par les agents

### 5.1 — Ouvrir une session

```powershell
claude
```

### 5.2 — La revue de diff intégrée

```
/code-review
```

### 5.3 — Le critique de tests de l'atelier A3

```
@agent-critique-tests Analyse les tests de la pagination qui viennent
d'être écrits.
```

### 5.4 — La question que personne ne pose

```
Le contrat de GET /api/todos a-t-il changé ? Qui, dans ce dépôt, consomme
cette route et casserait ?
```

**Notez si l'agent trouve `static/script.js` tout seul.** C'est la mesure intéressante
de l'étape.

### 5.5 — Quitter la session

```
/exit
```

---

# Étape 6 — Écrire la décision et committer

### 6.1 — Créer le fichier de décision

```powershell
@'
# TODO-150 - decision

Decision : correction guidee

Motif :
L'issue est respectee a la lettre, tous les tests passent, mais
static/script.js casse : la route ne renvoie plus une liste.
C'est la modification 3 du ticket, la seule rupturiere.

Ce qui a manque a l'issue :
"Les consommateurs existants de la route restent fonctionnels."
'@ | Set-Content -Encoding utf8 DECISION.md
```
git checkout atelier-a7
git add .
git commit -m "atelier A7 : decision"

### 6.2 — Vérifier ce qui a changé

```powershell
git status
git diff --stat
```

### 6.3 — Committer

```powershell
git add .
git commit -m "atelier A7 : pagination deleguee, regression front constatee"
```

### 6.4 — Pousser

```powershell
git push -u origin atelier-a7
```

> Si vous êtes **dans une session Claude Code**, ce `git push` sera refusé par votre
> hook de l'atelier A5. C'est voulu. Poussez depuis une fenêtre PowerShell ordinaire :
> l'humain garde ce geste-là.

---

# Résultat attendu

- [ ] `tickets/TODO-150.md` écrit, à quatre sections
- [ ] `tickets/RELECTURE.md` rempli avant de déléguer
- [ ] Une délégation exécutée **sans que vous touchiez au code**
- [ ] `python -m pytest -q` vert
- [ ] La page vide constatée dans le navigateur
- [ ] L'erreur lue dans la console : `script.js:61`
- [ ] La modification fautive identifiée : la **3**
- [ ] `DECISION.md` écrit et committé

# Ce qu'il faut retenir

| Constat | Conséquence |
|---|---|
| L'agent a fait exactement ce qui était écrit | Le défaut est dans le ticket, pas dans l'agent |
| « Ne pas toucher `static/` » ≠ « `static/` ne dépend de rien » | Borner un périmètre n'est pas analyser un impact |
| Tous les tests verts, application cassée | Une suite verte ne dit rien de ce qu'elle ne teste pas |
| Deux modifications additives + une rupturière | Le lot masque le risque |

**La phrase à ajouter à vos vrais tickets** :

> *Critère de vérification : les consommateurs existants de cette route restent
> fonctionnels.*

# Toutes les commandes de l'atelier

```powershell
# Préparer
cd D:\Documents\nvidia-courses\agenticAI\todo-app-new-feature\workshop1
python -m pytest -q
git checkout -b atelier-a7
python app.py                      # dans une seconde fenetre

# Déléguer
claude --bg --max-turns 40 "Implemente integralement tickets/TODO-150.md, tests compris. Ne touche pas a static/. Termine par python -m pytest -q."
claude agents
claude logs <id>
claude attach <id>
claude stop <id>

# Constater
python -m pytest -q
curl.exe "http://localhost:5000/api/todos?limit=2"
notepad static\script.js

# Décider
git status
git diff --stat
git add .
git commit -m "atelier A7 : pagination deleguee, regression front constatee"
git push -u origin atelier-a7
```

| Commande | Ce qu'elle fait |
|---|---|
| `claude --bg "…"` | Lance une session qui travaille en arrière-plan |
| `/background` (`/bg`) | La même chose, depuis une session ouverte |
| `claude agents` | Liste les sessions et leur état |
| `claude logs <id>` | Affiche ce qu'une session a fait |
| `claude attach <id>` | Reprend la main sur une session détachée |
| `claude stop <id>` | L'arrête |
| `--max-turns N` | Plafond en aller-retours |
| `--max-budget-usd N` | Plafond en dépense |
| `claude -p "…"` | Une seule question, sans ouvrir de session |
| `--output-format json` | Renvoie coût, tours et durée, pour mesurer |
| `/code-review` | Revue du diff |
| `@agent-<nom>` | Force l'exécution d'un subagent précis |
| `/exit` | Quitte la session |



# Piste experte

### 1. Mesurer le coût réel

```powershell
git checkout -B run-1 main
claude -p "Implemente tickets/TODO-150.md, tests compris." --permission-mode acceptEdits --max-turns 40 --output-format json > run-1.json
```

```powershell
python -c "import json;d=json.load(open('run-1.json'));print({k:d.get(k) for k in ('total_cost_usd','num_turns','duration_ms')})"
```

| Poste | Valeur |
|---|---|
| Temps de rédaction du ticket | |
| Coût de la délégation | |
| Temps d'attente | |
| Temps de revue | |
| Temps qu'aurait pris l'implémentation à la main | |

**Cette tâche valait-elle une délégation ?** À quelle condition l'aurait-elle valu ?

### 2. Mesurer la variance

```powershell
foreach ($i in 1..3) {
  git checkout -B "run-$i" main
  claude -p "Implemente tickets/TODO-150.md, tests compris." --permission-mode acceptEdits --max-turns 40 --output-format json > "run-$i.json"
}

Puis lire les résultats

powershell
foreach ($i in 1..3) {
  python -c "import json;d=json.load(open('run-$i.json'));print($i, d.get('total_cost_usd'), d.get('num_turns'), d.get('duration_ms'))"
}

```


### 3. Isoler dans un worktree

```powershell
claude --worktree ..\wt-pagination --bg "Implemente tickets/TODO-150.md, tests compris."
```

Votre dossier de travail n'est jamais touché.

### 4. Corriger le ticket, et recommencer

```powershell
notepad tickets\TODO-150.md
```

Ajoutez au critère de vérification :

```
- static/script.js continue de fonctionner : la page affiche les taches
```

```powershell
git checkout -B run-corrige main
claude --bg --max-turns 40 "Implemente integralement tickets/TODO-150.md, tests compris. Termine par python -m pytest -q."
```

Rechargez http://localhost:5000. **La page fonctionne cette fois.**

C'est la boucle complète : l'échec a amélioré votre façon de spécifier.

---

# Annexe A — la variante `@claude` sur GitHub

**Hors atelier.** 20 à 30 minutes de mise en place la première fois. Chaque étape a une
**vérification** : ne passez à la suivante que si elle passe.

## A.1 — Installer `gh`

```powershell
winget install --id GitHub.cli
```
ou

irm get.scoop.sh | iex 
scoop install gh 
**Si winget demande une élévation et que vous n'êtes pas admin**, installation portable
dans votre profil :

```powershell
$dest = "$env:LOCALAPPDATA\gh"
$tmp  = "$env:TEMP\gh.zip"
$rel  = Invoke-RestMethod https://api.github.com/repos/cli/cli/releases/latest
$url  = ($rel.assets | Where-Object { $_.name -like "*windows_amd64.zip" }).browser_download_url
Invoke-WebRequest $url -OutFile $tmp
Expand-Archive $tmp -DestinationPath $dest -Force
$bin = (Get-ChildItem $dest -Recurse -Filter gh.exe | Select-Object -First 1).DirectoryName
$old = [Environment]::GetEnvironmentVariable('PATH','User')
[Environment]::SetEnvironmentVariable('PATH', "$old;$bin", 'User')
```

**Fermez et rouvrez la fenêtre PowerShell.** Obligatoire : le `PATH` n'est pas rechargé
dans la fenêtre courante. C'est la cause n°1 du « je viens de l'installer et il ne le
trouve pas ».

**Vérification**

```powershell
gh --version
```

## A.2 — S'authentifier

```powershell
gh auth login
```

Répondez : `GitHub.com` → `HTTPS` → `Login with a web browser`.

**Vérification**

```powershell
gh auth status
```

## A.3 — Trouver la vraie racine du dépôt

**Le piège le plus coûteux.** Un workflow n'est lu qu'à la racine du dépôt git, jamais
dans un sous-dossier.

```powershell
git rev-parse --show-toplevel
```

```powershell
cd (git rev-parse --show-toplevel)
```

> GitHub ne regarde que .github/workflows/ à la racine

## A.4 — Créer le jeton, puis le secret

```powershell
claude setup-token
```

Le navigateur s'ouvre, vous autorisez, un jeton s'affiche dans le terminal.
**Copiez-le.**

```powershell
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```

>GitHub va lancer Claude sur ses propres machines. Il lui faut une clé pour se connecter à ton compte Anthropic. 
**Vérification**

```powershell
gh secret list
```

## A.5 — Créer le workflow

```powershell
New-Item -ItemType Directory -Force .github\workflows | Out-Null
```

```powershell
@'
name: Claude

on:
  issue_comment:
    types: [created]

jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
'@ | Set-Content -Encoding utf8 .github\workflows\claude.yml
```

> **Un workflow, c'est une recette que GitHub exécute tout seul quand un événement se
> produit.** Celui-ci dit : *quand quelqu'un commente une issue et que le commentaire
> contient `@claude`, allume une machine, récupère le code, lance Claude dessus.*

## A.6 — Le pousser, vraiment

```powershell
git status
```

**Si `.github/` apparaît en *untracked*, il n'est pas dans git.** Un fichier créé n'est
pas un fichier versionné — c'est le second piège.

```powershell
git add .github
git commit -m "chore: workflow claude"
git push
```

**Vérification — la seule qui compte**

```powershell
gh workflow list
```

**Vous devez voir** :

```
NAME    STATE   ID
Claude  active  348014853
```

Tant que c'est `no workflows found`, rien ne se passera jamais.

## A.7 — Activer les Actions

```powershell
gh browse --settings
```

Ou ouvrez `https://github.com/<vous>/<depot>/settings/actions` et réglez :

- **Actions permissions** → *Allow all actions and reusable workflows*
- **Workflow permissions** → *Read and write permissions*
- Cocher **Allow GitHub Actions to create and approve pull requests**

Sans la dernière case, l'agent travaille mais ne peut pas ouvrir la PR.

## A.8 — Créer l'issue

```powershell
gh issue create --title "TODO-150 - Pagination de GET /api/todos" --body-file tickets\TODO-150.md
```

```powershell
gh issue list
```

Notez le numéro affiché.

## A.9 — Mentionner Claude

Le `@claude` va dans un **commentaire**, pas dans le corps de l'issue : le workflow
écoute `issue_comment`.

```powershell
gh issue comment 3 --body "@claude implemente cette issue telle qu'elle est ecrite, tests compris, et ouvre une pull request."
```

Ou sur github.com : ouvrez l'issue → boîte **« Add a comment »** tout en bas → écrivez
`@claude …` → bouton **Comment**.

**Vérification**

```powershell
gh run list --limit 3
gh run watch
```

## A.10 — Récupérer la PR

```powershell
gh pr reopen 3  
gh pr view 3
gh pr list
```

```powershell
claude --from-pr 2
```

Puis reprenez à l'**étape 5** du guide : tests verts, page vide, console.
