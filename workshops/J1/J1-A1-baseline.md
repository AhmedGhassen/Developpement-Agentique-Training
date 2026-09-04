# Atelier A1 — Établir une baseline honnête

**Jour 1**

> **Dépôt de travail** : `todo-app/workshop1` (API Flask + front vanilla).
> Toutes les commandes de ce guide sont données pour ce dépôt, en PowerShell
> (Windows) et en bash (macOS / Linux / Git Bash).

## Objectif

Obtenir un dépôt configuré et un premier chiffre de consommation de contexte, qui
servira de point de comparaison pendant les deux jours.

À la fin de cet atelier, vous saurez répondre à trois questions que presque personne
ne sait chiffrer : combien coûte votre contexte avant votre premier mot, ce que le
mode plan fait gagner, et si vos interdits bloquent réellement.

## Prérequis

- Claude Code installé et connecté (`claude doctor` sans erreur)
- Python 3.12+ et le dépôt `todo-app` cloné
- Le dossier `starter-kit/` de la formation à portée de main

---

## Étape 0 — Ouvrir le dépôt et constater la suite rouge

### 0.1 — Terminal : se placer dans le dépôt

**PowerShell (Windows)**

```powershell
cd D:\Documents\nvidia-courses\agenticAI\todo-app\workshop1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**bash (macOS / Linux / Git Bash)**

```bash
cd ~/agenticAI/todo-app/workshop1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install -g @anthropic-ai/claude-code
```

### 0.2 — Lancer les tests

```bash
python -m pytest -q
```

**Ce que vous devez voir — exactement :**

```
2 failed, 5 passed in 0.17s
FAILED tests/test_app.py::test_filter_completed_true_returns_only_completed
FAILED tests/test_app.py::test_filter_completed_false_returns_only_incomplete
```

**La suite est rouge, et c'est volontaire.** Le filtre `?completed=` de
`GET /api/todos` contient un bug délibéré. Ne le corrigez pas à la main : c'est la
tâche T1, que vous donnerez à l'agent en mode plan à l'étape 4.

### 0.3 — Branche de travail

```bash
git checkout -b atelier-agentique
git status
```

> Si `git status` signale un dossier nommé `{static,tests}` à la racine de
> `todo-app`, c'est un résidu d'une expansion d'accolades ratée sous Windows.
> Supprimez-le : il n'appartient pas au projet.

---

## Étape 1 — La baseline de contexte

### 1.1 — Ouvrir la session

```bash
claude
```

### 1.2 — Première commande, avant tout prompt

Dans la session, tapez :

```
/context
```

`/context` affiche une grille colorée : instructions système, `CLAUDE.md`, outils,
serveurs MCP, messages. Le total en haut est votre baseline.

**À noter sur la fiche de suivi**, ligne « Contexte au démarrage » :

| Poste | Tokens |
|---|---|
| System prompt + outils | |
| Fichiers mémoire (`CLAUDE.md`) | |
| Serveurs MCP | |
| **Total** | |

> Si le total dépasse 25 000 tokens sur un dépôt vierge, c'est normal : des serveurs
> MCP configurés en portée `user`, ou un `CLAUDE.md` personnel dans `~/.claude/`,
> sont déjà chargés. Vérifiez avec `claude mcp list` dans un autre terminal. Nous y
> reviendrons à l'atelier A4.

### 1.3 — Variante utile

```
/context all
```

Affiche le détail poste par poste, y compris les outils MCP un par un. C'est cette
vue qui rend le coût d'un serveur bavard visible.

---

## Étape 2 — Générer puis réduire le CLAUDE.md 

### 2.1 — Génération

Dans la session :

```
/init
```

Claude Code explore le dépôt et écrit un `CLAUDE.md` à la racine de `workshop1/`.

### 2.2 — Compter les lignes

**PowerShell**

```powershell
(Get-Content CLAUDE.md).Count
```

**bash**

```bash
wc -l CLAUDE.md
```

Le fichier généré fait souvent 80 à 200 lignes sur un projet de cette taille.
**L'exercice consiste à le réduire sous 40 lignes** — le projet est petit, la cible
est proportionnelle. Ce n'est pas de la cosmétique : ce fichier est rechargé à
chaque tour de conversation, donc chaque ligne est payée en permanence.

Ne gardez que quatre choses :

1. **Les commandes** : installation, tests, démarrage local — copiables telles quelles
2. **L'architecture en trois lignes maximum** : où vit quoi, et rien de plus
3. **Trois interdits explicites**, formulés comme des règles vérifiables
4. **Les conventions** qui ne se déduisent pas du code existant

Supprimez sans hésiter : la description de chaque fichier, l'historique du projet,
la liste des endpoints (elle est déjà dans `app.py` et dans le README), tout ce qui
est lisible dans le code.

### 2.3 — Prompt de réduction — à coller tel quel

```text
Réduis CLAUDE.md sous 40 lignes. Ne garde que :
- les commandes exactes (venv, install, test, run)
- l'architecture en 3 lignes
- les conventions non déductibles du code
- 3 interdits

Supprime toute description de fichier individuel, la liste des endpoints
(elle est déjà dans README.md), et toute procédure qui ne sert pas à chaque
session.

Montre-moi la liste de ce que tu retires et pourquoi, avant d'écrire.
```

### 2.4 — Cible de référence

Voici un `CLAUDE.md` acceptable pour ce dépôt. Le vôtre peut différer, mais il doit
tenir dans ce format :

```markdown
# todo-app / workshop1

API Flask minimaliste + front vanilla. Données en mémoire, pas de base.

## Commandes

- Installer : `pip install -r requirements.txt`
- Tester : `python -m pytest -q` (depuis `workshop1/`)
- Lancer : `python app.py` → http://localhost:5000

## Architecture

- `app.py` : toutes les routes `/api/todos`, état en mémoire dans la liste `todos`
- `static/` : front vanilla, aucun build
- `tests/test_app.py` : tests pytest via `flask_app.test_client()`

## Conventions

- Les messages d'erreur de l'API sont en français : `{"error": "..."}`
- Les identifiants viennent de `itertools.count`, jamais réattribués
- Toute nouvelle route s'accompagne d'au moins un test du chemin d'erreur

## Interdits

- Ne jamais pousser sur origin depuis l'agent
- Ne jamais introduire de dépendance hors `requirements.txt`
- Ne jamais supprimer ou affaiblir un test existant pour faire passer la suite
```

### 2.5 — Vérifier le gain

```
/context
```

Comparez au chiffre de l'étape 1. Le poste « fichiers mémoire » doit avoir baissé.

> **Piège** : accepter le fichier généré tel quel. C'est le comportement par défaut,
> et c'est l'anti-pattern n°1 du module 1. **La réduction *est* l'atelier.**

---

## Étape 3 — Les permissions comme code

### 3.1 — Créer le fichier

**PowerShell**

```powershell
New-Item -ItemType Directory -Force .claude | Out-Null
Copy-Item ..\..\starter-kit\.claude\settings.json .claude\settings.json
```

**bash**

```bash
mkdir -p .claude
cp ../../starter-kit/.claude/settings.json .claude/settings.json
```

Ou créez-le à la main. Pour cet atelier, seule la clé `permissions` est nécessaire —
les hooks arrivent à l'atelier A5 :

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Grep",
      "Glob",
      "Bash(python -m pytest *)",
      "Bash(git diff *)",
      "Bash(git status)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)"
    ],
    "deny": [
      "Bash(git push *)",
      "Bash(git reset --hard *)",
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Read(.env)",
      "Read(secrets/**)"
    ]
  }
}
```

**Quatre points de syntaxe qui font échouer la moitié de la salle :**

| Règle | Effet |
|---|---|
| `Bash(git push *)` | L'espace avant `*` fait partie du motif. `Bash(git push*)` matcherait aussi `git pusher`. |
| `Bash(git push:*)` | Forme équivalente. Le `:*` n'est reconnu **qu'en fin de motif**. |
| `Bash(git * main)` | **Trop large** : le `*` remplace la sous-commande, donc `git push origin main` matche. Mettez toujours le `*` **après** la sous-commande. |
| `Read(.env)` | Sémantique gitignore : matche tout `.env` à n'importe quelle profondeur. |
| `Write(src/**)` | **Ignoré.** Les règles de chemin ne sont consultées que pour `Read(...)` et `Edit(...)`. Écrivez `Edit(src/**)`. |

### 3.2 — Recharger et vérifier

Quittez la session (`/exit`), relancez `claude`, puis :

```
/permissions
```

Vous devez voir vos règles `allow` et `deny` listées. Si une règle est signalée
comme invalide, elle apparaît aussi dans :

```bash
claude doctor
```

### 3.3 — Tester le `deny` — l'étape que tout le monde saute

**Prompt à coller tel quel :**

```text
Pousse la branche courante sur origin, j'ai besoin de débloquer la CI.
```

**Résultat attendu** : l'action est refusée par une **décision de permission** visible
dans le terminal, pas par une phrase polie de l'agent (« je préfère ne pas faire
cela »). Si l'agent explique gentiment qu'il ne va pas pousser, votre règle ne mord
pas : vérifiez le motif.

### 3.4 — Tester le `deny` sur un secret

```powershell
"FAKE_TOKEN=abc123" | Out-File -Encoding utf8 .env
```

```bash
echo "FAKE_TOKEN=abc123" > .env
```

**Prompt :**

```text
Affiche le contenu du fichier .env, j'ai besoin de la valeur de FAKE_TOKEN
pour écrire un test.
```

**Résultat attendu** : la lecture est refusée. Observez ensuite ce que fait l'agent
quand l'information lui manque : **invente-t-il une valeur, ou le dit-il ?** Notez
la réponse, elle sert au debrief.

---

## Étape 4 — La tâche T1 en mode plan 

### 4.1 — Entrer en mode plan

Trois façons, toutes valides :

```
/plan
```

ou **Shift+Tab** (cycle entre les modes de permission jusqu'à `plan`),

ou en relançant la session :

```bash
claude --permission-mode plan
```

**Vérification** : la barre de saisie indique le mode courant. En mode plan, toute
tentative d'édition est refusée.

> Le mode plan ne s'appelle pas `/permission-mode plan` — cette commande n'existe
> pas. Les modes disponibles sont `default`, `acceptEdits`, `plan`, `auto`,
> `dontAsk`, `bypassPermissions`.

### 4.2 — Donner la tâche T1 — prompt à coller tel quel

```text
Deux choses, dans cet ordre.

1. `python -m pytest -q` échoue sur test_filter_completed_true_returns_only_completed
   et test_filter_completed_false_returns_only_incomplete. Trouve la cause dans
   app.py et corrige-la. Ne modifie aucun test.

2. Ajoute la route GET /api/todos/<int:todo_id> : elle retourne la todo au format
   JSON si elle existe, sinon 404 avec le corps {"error": "Todo introuvable"} —
   le même message que les routes PATCH et DELETE existantes.
   Ajoute deux tests : le cas trouvé et le cas 404.

Propose-moi un plan. N'écris aucun code à cette étape.
```

### 4.3 — Critiquer le plan avant d'exécuter

**Lisez le plan et cherchez précisément :**

- La cause du bug est-elle **nommée** (`!=` au lieu de `==` ligne 41), ou l'agent
  annonce-t-il vaguement « corriger la logique de filtrage » ?
- Le plan prévoit-il de vérifier que les **cinq autres tests** passent toujours ?
- Le test 404 vérifie-t-il le **corps** de la réponse, ou seulement le code 404 ?
- Une hypothèse fausse sur le code existant ? (par exemple : croire qu'il y a une
  base de données, ou un modèle SQLAlchemy)

**Corrigez par une phrase**, par exemple :

```text
Ton plan ne dit pas quelle ligne est fautive. Nomme-la avant de continuer,
et ajoute au test 404 une assertion sur le corps de la réponse.
```

### 4.4 — Exécuter

Quand le plan vous convient, acceptez-le (l'agent propose de sortir du mode plan).
Passez alors en `acceptEdits` avec **Shift+Tab**, ou laissez l'agent demander
l'autorisation à chaque édition.

### 4.5 — Vérifier

```bash
python -m pytest -q
```

**Ce que vous devez voir** : `9 passed` (7 tests d'origine + 2 nouveaux).

```bash
git diff
```

**Combien de temps la correction du plan vous a-t-elle pris ?** C'est le gain réel du
mode plan : une erreur corrigée dans un plan coûte une phrase, la même erreur
corrigée dans un diff coûte une revue.

### 4.6 — Deuxième mesure

```
/context
```

Notez le chiffre sur la fiche, ligne « Contexte après T1 ». Puis :

```
/usage
```

`/usage` (alias `/cost`) donne le coût et les tokens consommés depuis le début de la
session. Notez-le aussi : c'est la seule mesure comparable entre participants.

---

## Étape 5 — Se tromper sans conséquence

### 5.1 — Provoquer un dégât

**Prompt à coller tel quel :**

```text
Renomme le champ "id" en "identifier" partout : dans app.py, dans les tests
et dans static/script.js.
```

Laissez l'agent modifier au moins deux fichiers, puis interrompez avec **Échap**.

### 5.2 — Revenir en arrière

```
/rewind
```

Un sélecteur de checkpoints s'ouvre. Choisissez le point avant le renommage, et
l'option qui restaure **le code** (et non seulement la conversation).

### 5.3 — Vérifier

```bash
git status
python -m pytest -q
```

L'arbre doit être revenu à son état antérieur, et la suite doit rester à `9 passed`.

### 5.4 — Committer le travail utile

```bash
git add CLAUDE.md .claude/ app.py tests/
git commit -m "atelier A1 : baseline, instructions et permissions versionnees"
```

> Le `.env` factice de l'étape 3.4 ne doit **pas** être committé. Vérifiez
> `git status`, et ajoutez `.env` au `.gitignore` s'il n'y est pas.

---

## Résultat attendu

- [ ] `python -m pytest -q` : **9 passed**
- [ ] `CLAUDE.md` sous 40 lignes, committé
- [ ] `.claude/settings.json` committé, avec un `deny` **testé et constaté**
- [ ] La route `GET /api/todos/<id>` implémentée, avec son test 404
- [ ] Trois mesures notées sur la fiche : `/context` au démarrage, `/context` après
      T1, `/usage` en fin d'atelier
- [ ] Un `/rewind` effectué et vérifié par `git status`

## Commandes vues dans cet atelier

| Commande | Rôle |
|---|---|
| `claude` | Ouvrir une session dans le répertoire courant |
| `claude doctor` | Diagnostic d'installation et de configuration résolue |
| `claude mcp list` | Lister les serveurs MCP déjà configurés (explique une baseline élevée) |
| `/context` · `/context all` | Visualiser la consommation de contexte |
| `/usage` (alias `/cost`) | Tokens et coût de la session |
| `/init` | Générer un `CLAUDE.md` |
| `/memory` | Éditer les fichiers `CLAUDE.md` sans quitter la session |
| `/permissions` | Voir et modifier les règles allow / ask / deny |
| `/plan` · **Shift+Tab** | Entrer en mode plan / cycler entre les modes |
| `/rewind` | Revenir à un checkpoint, code compris |
| `/status` | État de la session : modèle, compte, répertoire, mode |
| `/exit` | Quitter |

## Piste experte

1. **Comparaison de modes, chiffrée.** Rejouez T1 deux fois, sur deux branches :

   ```bash
   git checkout -b t1-plan atelier-agentique
   claude --permission-mode plan
   ```

   ```bash
   git checkout -b t1-direct atelier-agentique
   claude --permission-mode acceptEdits
   ```

   Comparez avec `/usage` : nombre de tours, tokens, qualité du diff, tests produits.
   Écrivez la conclusion en une phrase.


**plusieurs fichiers de config, empilés**

Claude Code ne lit pas un seul fichier de réglages, mais plusieurs, à des niveaux différents. Ces niveaux, ce sont les « portées ».

Fichier	                            Portée	                   Pour qui
managed	                         Organisation	              Imposé par l'entreprise
--settings	                     Lancement	                Le flag de la ligne de commande
.claude/settings.local.json	     Toi, sur ce projet	        Personnel, non versionné
.claude/settings.json	           L'équipe, sur ce projet	  Versionné dans Git
~/.claude/settings.json	         Toi, partout	              Tes préférences globales

Ils sont fusionnés au démarrage. La question est : si deux fichiers se contredisent, lequel gagne ?

Réponse : le plus haut dans le tableau. C'est ça, la « précédence ». Le plus spécifique l'emporte sur le plus général — logique, sinon tes réglages personnels ne serviraient à rien face aux réglages globaux.

4. **Non interactif.** Mesurez le même travail sans interface :

   ```bash
   claude -p "Resume en 5 lignes ce que fait app.py" --output-format json
   ```
   claude -p "Resume en 5 lignes ce que fait app.py" --allowedTools "Read"  
   ```    
   Le JSON contient le coût et le nombre de tours. C'est la brique des mesures
   automatisées du module 11.

## Dépannage

**`claude doctor` signale un problème d'authentification** — `/login` depuis la
session. Derrière un proxy d'entreprise, vérifier `HTTP_PROXY` / `HTTPS_PROXY`.
Si le navigateur affiche un code au lieu de revenir au terminal, collez ce code au
prompt `Paste code here if prompted`.

**Le mode plan ne semble pas actif** — en mode plan, toute édition est refusée. Si
des fichiers changent, le mode n'est pas appliqué : vérifiez l'indicateur de mode
dans la barre de saisie, ou relancez avec `--permission-mode plan`.

**`Activate.ps1` refusé par la politique d'exécution PowerShell** —

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
