# Atelier A5 — Deux hooks qui changent la journée

**Jour 1**

> **Dépôt de travail** : `todo-app/workshop1`, branche `atelier-agentique`,
> ateliers A1 à A4 committés.

## Objectif

Constater la différence de **nature** entre une consigne (négociable, oubliable) et
un hook (déterministe, auditable). À la fin, votre agent ne pourra plus déclarer une
tâche terminée sur une suite de tests rouge — et personne n'aura eu besoin de le lui
demander.

## Prérequis

- Ateliers A1 à A4 terminés, `python -m pytest -q` au vert
- L'outillage du hook :

**Windows** — PowerShell suffit, rien à installer. Si vous préférez les scripts
`.sh`, il vous faut Git Bash ou WSL, plus `jq` :

```powershell
winget install jqlang.jq
```

**macOS / Linux**

```bash
brew install jq        # ou : sudo apt install jq
```

**Dans tous les cas**, le formateur de l'étape 2 :

```bash
pip install ruff
```

---

## Étape 0 — Le contrat des hooks

Trois choses à comprendre avant d'écrire une ligne :

1. **La charge utile arrive en JSON sur `stdin`.** Il n'y a **pas** de variable
   d'environnement `$CLAUDE_FILE_PATHS`. 
   Le chemin du fichier édité se lit dans
   `tool_input.file_path`, la commande dans `tool_input.command`.

2. **Le code de sortie décide** :

   | Code | Effet |
   |---|---|
   | `0` | Autorisé. Si `stdout` est un objet JSON, il est interprété |
   | `2` | **Refusé**, sans discussion. `stderr` est renvoyé au modèle, qui s'adapte |
   | autre | Erreur non bloquante : l'action passe quand même |

   **`exit 1` ne bloque rien.** C'est l'erreur la plus fréquente.

3. **Le message doit partir sur `stderr`**, pas sur `stdout`.

Voyez ce qui est déjà configuré :

```
/hooks
```

---

## Étape 1 — Le hook de blocage

### 1.1 — Créer le dossier

**PowerShell**

```powershell
New-Item -ItemType Directory -Force .claude\hooks | Out-Null
```

**bash**

```bash
mkdir -p .claude/hooks
```

### 1.2a — Version PowerShell : `.claude/hooks/guard-bash.ps1`

```powershell
# Refuse les commandes interdites par la politique du depot.
# Contrat : la charge utile arrive en JSON sur stdin.
# Sortie 0 = autorise, 2 = refuse (stderr est renvoye au modele).

$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$cmd = $payload.tool_input.command
if (-not $cmd) { exit 0 }

$interdits = @(
  'git push',
  'git reset --hard',
  'rm -rf',
  'chmod 777',
  'curl ',
  'wget ',
  'pip uninstall'
)

foreach ($bad in $interdits) {
  if ($cmd -like "*$bad*") {
    [Console]::Error.WriteLine("Refuse par la politique du depot : '$bad' n'est pas autorise depuis l'agent.")
    [Console]::Error.WriteLine("Si cette action est reellement necessaire, elle doit etre faite par un humain.")
    exit 2
  }
}

exit 0
```

### 1.2b — Version bash : `.claude/hooks/guard-bash.sh`

```bash
#!/usr/bin/env bash
# Refuse les commandes interdites par la politique du dépôt.
# Contrat : la charge utile arrive en JSON sur stdin.
# Sortie 0 = autorisé, 2 = refusé (stderr est renvoyé au modèle).
set -euo pipefail

CMD=$(jq -r '.tool_input.command // empty')
[[ -z "$CMD" ]] && exit 0

INTERDITS=('git push' 'git reset --hard' 'rm -rf' 'chmod 777' 'curl ' 'wget ' 'pip uninstall')

for BAD in "${INTERDITS[@]}"; do
  if [[ "$CMD" == *"$BAD"* ]]; then
    echo "Refusé par la politique du dépôt : « $BAD » n'est pas autorisé depuis l'agent." >&2
    echo "Si cette action est réellement nécessaire, elle doit être faite par un humain." >&2
    exit 2
  fi
done

exit 0
```

**Rendre exécutable — l'oubli le plus fréquent de l'atelier :**

```bash
chmod +x .claude/hooks/guard-bash.sh
```

### 1.3 — Tester le script AVANT de le brancher

**PowerShell**

```powershell
'{"tool_input":{"command":"git push origin main"}}' | powershell -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\guard-bash.ps1
$LASTEXITCODE
```

**bash**

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | .claude/hooks/guard-bash.sh
echo $?
```

**Ce que vous devez voir** : le message de refus, et le code `2`.
Refaites avec `{"tool_input":{"command":"git status"}}` : rien, et le code `0`.



### 1.4 — Déclarer le hook

Dans `.claude/settings.json`, à côté de la clé `permissions` :

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/guard-bash.ps1",
            "timeout": 15,
            "statusMessage": "Verification de la politique du depot..."
          }
        ]
      }
    ]
  }
}
```

**macOS / Linux / Git Bash** — remplacez la ligne `command` par :

```json
"command": ".claude/hooks/guard-bash.sh",
```

### 1.5 — Relancer et tester

```
/exit
```

```bash
claude
```

```
/hooks
```

Le hook doit apparaître sous `PreToolUse`. Puis :

```text
Pousse la branche courante sur origin, j'ai besoin de debloquer la CI.
```

**Résultat attendu** : **votre** message apparaît dans le terminal, et l'agent
s'adapte — il propose autre chose, ou explique qu'il ne peut pas.

**La différence avec l'atelier A1** : là, le refus venait du moteur de permissions.
Ici, c'est **votre code**, avec votre message, votre liste, votre journalisation
possible.

---

## Étape 2 — Le hook de formatage

### 2.1a — PowerShell : `.claude/hooks/format-python.ps1`

```powershell
# Formate le fichier Python qui vient d'etre edite.
# Le chemin se lit dans tool_input.file_path : il n'existe pas de $CLAUDE_FILE_PATHS.

$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$file = $payload.tool_input.file_path
if (-not $file) { exit 0 }
if ($file -notlike '*.py') { exit 0 }

ruff format -- "$file"      2>&1 | Out-Null
ruff check --fix -- "$file" 2>&1 | Out-Null
exit 0
```

### 2.1b — bash : `.claude/hooks/format-python.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

FILE=$(jq -r '.tool_input.file_path // empty')
[[ -z "$FILE" ]] && exit 0
[[ "$FILE" == *.py ]] || exit 0

ruff format -- "$FILE"      >/dev/null 2>&1 || true
ruff check --fix -- "$FILE" >/dev/null 2>&1 || true
exit 0
```

```bash
chmod +x .claude/hooks/format-python.sh
```

### 2.2 — Déclarer

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/format-python.ps1",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```


### 2.3 — Tester

```text
Ajoute dans app.py une fonction utilitaire count_by_status(todos) qui
retourne un dict {"completed": n, "pending": n}.

Ecris-la volontairement mal formatee : espaces incoherents, imports non
tries, lignes trop longues. Je veux voir ce qui se passe.
```

Puis :

```bash
git diff app.py
```

**Résultat attendu** : le fichier est reformaté automatiquement après l'édition.
**Vous venez de supprimer une catégorie entière de commentaires de revue de code.**

---

## Étape 3 — Le hook qui interdit de conclure 


### 3.1 — Déclarer

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python -m pytest -q -x",
            "timeout": 90
          }
        ]
      }
    ]
  }
}
```


### 3.2 — Casser volontairement un test

Ouvrez `tests/test_app.py` et modifiez une assertion, par exemple :

```python
def test_create_todo(client):
    res = client.post("/api/todos", json={"title": "Nouvelle tâche de test"})
    assert res.status_code == 999      # <- volontairement faux
```

Vérifiez :

```bash
python -m pytest -q
```

### 3.3 — Demander autre chose à l'agent

```text
Ajoute un champ "notes" optionnel aux todos : accepte en POST et en PATCH,
retourne None par defaut.
```

### 3.4 — Ce que vous devez observer

Quand l'agent estime avoir terminé, le hook `Stop` échoue, **et l'agent reboucle de
lui-même** sur le test cassé. Personne ne lui a demandé de lancer les tests.

**C'est la démonstration centrale du Jour 1 : la boucle de vérification devient
structurelle.**

Notez sur la fiche de suivi :

| Mesure | Valeur |
|---|---|
| Nombre de blocages `Stop` observés | |
| L'agent a-t-il réparé le bon test ? | |
| Combien de tours supplémentaires ? (`/usage`) | |

### 3.5 — Le cas limite à discuter

Si l'agent ne **peut pas** réparer — parce que le test cassé exprime une exigence
qu'il ne comprend pas — il boucle. **Le hook a raison, c'est à vous de trancher.**


---

## Étape 4 — Committer la politique

```bash
git checkout tests/test_app.py
python -m pytest -q
git add .claude/
git commit -m "atelier A5 : garde-fous - blocage, formatage, refus de conclure sur suite rouge"
```

---

## Résultat attendu

- [ ] `git push` refusé **par le message de votre hook**, pas seulement par la permission
- [ ] Le script testé à la main en amont, avec le bon code de sortie
- [ ] Le formatage s'applique automatiquement après chaque édition
- [ ] L'agent reboucle sur un test cassé au lieu de conclure
- [ ] `.claude/` complet committé, suite au vert

## Commandes vues dans cet atelier

| Commande | Rôle |
|---|---|
| `/hooks` | Voir les hooks effectivement chargés |
| `/config` (alias `/settings`) | Ouvrir l'interface de configuration |
| `claude doctor` | Voir la configuration **résolue** et les entrées invalides |
| `claude --debug='hooks'` | Tracer l'exécution des hooks |
| `/usage` | Compter le coût des tours de rebouclage |
| **Échap** | Interrompre une boucle |

## Les événements de hook les plus utiles

| Événement | Quand | Usage typique |
|---|---|---|
| `PreToolUse` | Avant chaque appel d'outil | Interdire une commande, un chemin |
| `PostToolUse` | Après un appel réussi | Formater, linter, régénérer |
| `Stop` | Quand l'agent veut conclure | Refuser de conclure sur une suite rouge |
| `UserPromptSubmit` | À chaque message envoyé | Injecter du contexte, filtrer |
| `SessionStart` / `SessionEnd` | Ouverture / fermeture | Préparer l'environnement, auditer |
| `SubagentStop` | Fin d'un subagent | Valider le rapport d'un critique |
| `PreCompact` | Avant compaction | Sauvegarder ce qui va disparaître |


## Piste experte

1. **Rejouer le ticket hostile.** Reprenez `tickets/TODO-207.md` de l'atelier A4 et
   relancez-le. Le hook `PreToolUse` doit désormais bloquer l'action **même si le
   modèle décide de la tenter**. Vous avez transformé une consigne en garantie.
   Complétez le tableau des défenses de A4.



2. **Hook non déterministe.** Un hook peut être un **prompt** ou un **subagent**, pas
   seulement une commande. Configurez un `Stop` qui invoque `critique-tests` et refuse
   la conclusion si le rapport contient un constat bloquant. Comparez la fiabilité
   avec la version « commande » : **que se passe-t-il quand le vérificateur est
   lui-même un modèle ?** C'est la question centrale du Jour 2.

## Dépannage

**Le hook s'exécute mais son message n'apparaît pas** — écrivez sur `stderr` et
sortez avec le code `2`. Un `exit 1` laisse passer l'action.

**Tracer ce qui se passe réellement** :

```bash
claude --debug='hooks'
```


