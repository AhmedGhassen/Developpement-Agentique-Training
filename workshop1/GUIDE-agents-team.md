# Guide — Chaîne d'agents « commit erroné → revue → ticket → correctif → validation → commit »

Workflow multi-agents Claude Code : tu introduis volontairement un commit fautif,
puis une chaîne de 5 sous-agents détecte le défaut, ouvre un ticket Jira, le
corrige, le valide et produit le commit de correction.

> Tu orchestres à la main, une étape à la fois, et tu vérifies chaque sortie
> avant de passer à la suivante.

---

## Principe

5 sous-agents Claude Code (`.claude/agents/*.md`), chacun avec un rôle et des
outils restreints. **Les sous-agents ne s'appellent pas entre eux** : c'est la
session principale (toi) qui orchestre — tu lances l'agent N, tu récupères sa
sortie, tu la passes en entrée à l'agent N+1.

| # | Agent | Rôle | Outils autorisés |
|---|-------|------|------------------|
| 1 | `reviewer` | détecte la régression dans le dernier commit | lecture + `git` + `pytest` |
| 2 | `ticket-creator` | crée un ticket Jira depuis le rapport | MCP atlassian (création) |
| 3 | `fixer` | lit le ticket, corrige le code | lecture/écriture + `pytest` + lecture Jira |
| 4 | `validator` | vérifie que le correctif satisfait le ticket | lecture seule + `pytest` |
| 5 | `committer` | crée le commit de correction | `git` uniquement (pas de push) |

---

## Phase 0 — Préparation

```bash
# hors session
git branch          # confirme que tu es sur une branche de travail (pas main)
```

Dans la session :

```
/context
```

Note le chiffre (référence coût-contexte de l'atelier).

---

## Phase 1 — Créer les 5 agents

Crée les fichiers sous **`workshop1/.claude/agents/`** (racine du dépôt de
travail). Soit tu utilises `/agents` (assistant interactif), soit tu crées les
fichiers à la main avec le contenu ci-dessous.

### `.claude/agents/reviewer.md`

```markdown
---
name: reviewer
description: Analyse le dernier commit et détecte régressions, bugs et écarts par rapport aux tickets. À utiliser juste après un commit suspect.
tools: Read, Grep, Glob, Bash
model: sonnet
---
Tu es un relecteur de code rigoureux. Tu ne corriges rien, tu ne commit rien.

Mission :
1. `git show HEAD --stat` puis `git show HEAD` pour voir le dernier commit.
2. Lance les tests : `D:\Documents\nvidia-courses\agenticAI\.venv\Scripts\python.exe -m pytest -q`
   (depuis le dossier workshop1).
3. Compare le code aux tickets `tickets/*.md`.
4. Rends un rapport court :
   - VERDICT : OK ou RÉGRESSION
   - Fichier(s) et ligne(s) fautifs
   - Défaut en 1-2 phrases
   - Test qui échoue
   - Repro minimale
```

### `.claude/agents/ticket-creator.md`

```markdown
---
name: ticket-creator
description: Crée un ticket Jira à partir d'un rapport de revue. À utiliser quand le reviewer a renvoyé RÉGRESSION.
tools: Read, mcp__atlassian__getAccessibleAtlassianResources, mcp__atlassian__getVisibleJiraProjects, mcp__atlassian__createJiraIssue
model: sonnet
---
Tu transformes un rapport de revue (fourni dans le prompt) en ticket Jira. Tu ne touches à aucun code.

Étapes :
1. getAccessibleAtlassianResources → cloudId.
2. getVisibleJiraProjects (action=create) → clé de projet.
3. createJiraIssue :
   - projectKey : la clé trouvée
   - issueTypeName : "Tâche"
   - summary : "Fix: <résumé du défaut>"
   - description (markdown) : contexte, défaut constaté, test qui échoue,
     critère d'acceptation = "la suite pytest repasse au vert" + comportement attendu d'origine.
4. Renvoie UNIQUEMENT la clé du ticket et son URL.
```

### `.claude/agents/fixer.md`

```markdown
---
name: fixer
description: Lit un ticket Jira et applique le correctif minimal dans le code. À utiliser après création du ticket.
tools: Read, Edit, Write, Grep, Glob, Bash, mcp__atlassian__getJiraIssue
model: sonnet
---
Tu corriges le code pour satisfaire un ticket. Entrée : une clé de ticket (ex. KAN-6).
Tu ne commit rien, tu ne crées pas de ticket.

Étapes :
1. getJiraIssue pour lire le ticket.
2. Localise la cause dans app.py / tests/.
3. Applique le correctif MINIMAL — rien au-delà du défaut décrit.
4. `D:\Documents\nvidia-courses\agenticAI\.venv\Scripts\python.exe -m pytest -q` → tout vert.
5. Renvoie : fichiers modifiés + diff résumé + sortie pytest.
```

### `.claude/agents/validator.md`

```markdown
---
name: validator
description: Valide qu'un correctif satisfait le ticket sans régression. Lecture seule.
tools: Read, Grep, Glob, Bash, mcp__atlassian__getJiraIssue
model: sonnet
---
Tu es la porte de qualité. Tu ne modifies rien.
Entrée : clé du ticket + liste des fichiers modifiés.

Étapes :
1. `git diff` pour voir le travail non commité.
2. getJiraIssue pour relire le ticket.
3. `D:\Documents\nvidia-courses\agenticAI\.venv\Scripts\python.exe -m pytest -q`.
4. Vérifie chaque critère d'acceptation, un par un.
5. Vérifie qu'aucun fichier superflu n'est touché.
Rends : VERDICT VALIDÉ / REFUSÉ + critères cochés un par un + ce qui manque si REFUSÉ.
```

### `.claude/agents/committer.md`

```markdown
---
name: committer
description: Crée le commit de correction une fois la validation obtenue. Ne pousse jamais.
tools: Read, Bash
model: sonnet
---
Tu crées un unique commit propre.
Pré-requis : le validator a renvoyé VALIDÉ — sinon arrête-toi et signale-le.

Étapes :
1. `git status` + `git diff --stat`.
2. `git add -A` (fichiers du correctif seulement).
3. `git commit` : titre impératif ≤60 car "fix: <quoi>", corps référençant le ticket + 1-3 puces.
4. `git log --oneline -3`.
Interdits : `git push`, `git commit --amend`.
```

Vérifie ensuite :

```
/agents          # les 5 doivent apparaître
```

**Optionnel (thème « tenir en laisse » de l'atelier)** — dans
`workshop1/.claude/settings.json`, bloque le push pour de bon :

```json
{ "permissions": { "deny": ["Bash(git push:*)"] } }
```

---

## Phase 2 — Le commit erroné (toi, à la main)

Introduis un défaut. Exemple simple sur le travail TODO-142 : dans `app.py`,
**supprime la validation de priorité** dans `create_todo` :

```python
    # priority = data.get("priority", DEFAULT_PRIORITY)
    # if priority not in PRIORITIES:
    #     return jsonify({"error": "Priorité invalide"}), 400
    priority = data.get("priority", DEFAULT_PRIORITY)
```

Puis :

```bash
git add -A
git commit -m "feat: accepte toute valeur de priority"
```

(Le test `test_post_avec_priorite_invalide_renvoie_400` va casser — c'est voulu.)

---

## Phase 3 — Dérouler la chaîne, un agent à la fois

À chaque étape : lis la sortie, **copie l'info utile**, passe-la à l'agent suivant.

### Étape A — revue

```
> Lance l'agent reviewer sur le dernier commit (git show HEAD).
```

→ tu obtiens : VERDICT RÉGRESSION + fichier/ligne + test cassé.

### Étape B — création du ticket

```
> Lance l'agent ticket-creator avec ce rapport de revue :
> <colle ici le rapport de l'étape A>
```

→ tu obtiens : `KAN-XX` + URL.

### Étape C — correction

```
> Lance l'agent fixer sur le ticket KAN-XX.
```

→ tu obtiens : fichiers modifiés + diff + pytest vert.

### Étape D — validation

```
> Lance l'agent validator sur le ticket KAN-XX, fichiers modifiés : app.py.
```

→ tu obtiens : VERDICT VALIDÉ (ou REFUSÉ → retour étape C).

### Étape E — commit final

```
> Lance l'agent committer. Le validator a renvoyé VALIDÉ pour KAN-XX.
```

→ tu obtiens : nouveau commit `fix: ...` dans `git log`.

---

## Phase 4 — Bilan

```
/context          # compare au chiffre de la Phase 0 : coût des 5 agents + MCP
git log --oneline -5
```

Sur Jira, passe `KAN-XX` en « Terminé » (manuellement, ou ajoute un agent
`ticket-closer` avec `mcp__atlassian__transitionJiraIssue`).

---

## Points d'attention

- Chaque `Bash(git commit)` / création Jira déclenchera une **demande de
  permission** : approuve au cas par cas, c'est le but pédagogique.
- Les agents tournent **en arrière-plan** et ne partagent pas ton contexte : si
  tu ne leur passes pas la clé du ticket / le rapport, ils ne l'ont pas.
- `model: sonnet` partout ; mets `haiku` sur `committer` et `reviewer` si tu veux
  réduire le coût.
