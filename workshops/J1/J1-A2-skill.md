# Atelier A2 — Écrire une skill qui se déclenche vraiment

**Jour 1**

> **Dépôt de travail** : `todo-app/workshop1`, branche `atelier-agentique`,
> avec le résultat de l'atelier A1 committé.

## Objectif

Produire une skill dont le **déclenchement automatique** est démontré par votre
binôme, et comprendre que la `description` est l'interface publique de la skill —
pas sa documentation.

La plupart des skills écrites en entreprise ne se déclenchent jamais. La cause est
presque toujours la même : une description qui dit *quoi* sans dire *quand*.

## Prérequis

- Atelier A1 terminé et committé (`9 passed`)
- Un diff à analyser : celui de A1 convient (la route `GET /api/todos/<id>`)

---

## Étape 1 — Comprendre où vivent les skills 

Trois emplacements, trois portées :

| Chemin | Portée | Versionné |
|---|---|---|
| `.claude/skills/<nom>/SKILL.md` | Ce projet | Oui — c'est celui de l'atelier |
| `~/.claude/skills/<nom>/SKILL.md` | Tous vos projets | Non |
| Plugin | Distribué à l'équipe | Selon le plugin |

Voyez ce que vous avez déjà : dans la session, tapez `/` et parcourez la liste. Les
skills intégrées (`/code-review`, `/security-review`, `/debug`, `/dataviz`…)
apparaissent au même endroit que les vôtres.

---

## Étape 2 — Choisir la bonne procédure 

Choisissez **une** procédure réelle de votre équipe. Critères d'une bonne candidate :

- Vous l'exécutez **régulièrement mais pas à chaque session** (sinon : `CLAUDE.md`)
- Elle a des **étapes** et un **format de sortie** attendu
- Vous savez dire à quoi ressemble un bon résultat

Bons exemples : revue de sécurité d'un diff, préparation de release, analyse
d'incident, migration de schéma, rédaction d'un ADR, audit de dépendances.

Mauvais exemples : « améliorer le code » (trop large, se déclenchera partout),
« lancer les tests » (trop simple, c'est une commande).

> Si vous manquez d'idée, prenez la revue de sécurité : le gabarit complet est
> ci-dessous et dans `starter-kit/.claude/skills/revue-securite/SKILL.md`.
> Le dépôt `todo-app` s'y prête : aucune authentification, aucune limite de taille
> sur `title`, `debug=True` dans `app.run`, état global mutable.

---

## Étape 3 — Créer la structure 

### 3.1 — Le dossier

**PowerShell**

```powershell
New-Item -ItemType Directory -Force .claude\skills\revue-securite | Out-Null
```

**bash**

```bash
mkdir -p .claude/skills/revue-securite
```

### 3.2 — Le fichier `SKILL.md`

Créez `.claude/skills/revue-securite/SKILL.md` avec exactement ce contenu :

```markdown
---
name: revue-securite
description: >
  Revue de sécurité d'un diff sur une API Flask : entrées non validées,
  contrôle d'accès, secrets en clair, configuration dangereuse, données
  renvoyées au client. À utiliser quand l'utilisateur demande une revue de
  sécurité, parle de faille, de risque, d'injection ou de CVE, ou quand il
  modifie une route HTTP, la validation d'un champ, ou la configuration
  de démarrage de l'application.
allowed-tools: Read Grep Glob Bash(git diff *) Bash(git status)
disallowed-tools: Edit Write
---

## Périmètre

Analyser uniquement le diff de la branche courante par rapport à `main`.
Ne modifier aucun fichier.

## Procédure

1. `git diff main...HEAD` pour délimiter le périmètre exact.
   Si la commande ne retourne rien, utiliser `git diff HEAD`.
2. Pour chaque fichier touché, vérifier dans cet ordre :
   - entrée utilisateur atteignant un chemin de fichier, une commande ou une requête
   - champ accepté sans validation de type, de longueur ou de valeurs autorisées
   - contrôle d'accès : la route vérifie-t-elle qui appelle ?
   - secrets en clair : jetons, mots de passe, chaînes de connexion
   - configuration dangereuse : mode debug, CORS ouvert, écoute sur 0.0.0.0
   - donnée sensible renvoyée au client ou journalisée
3. Consulter `references/checklist.md` **uniquement** si le diff touche
   une route HTTP ou la configuration de démarrage.

## Format de sortie

Un constat par ligne, exactement dans ce format :

app.py:41 — **majeur** — le paramètre `completed` est comparé sans être
validé contre une liste de valeurs autorisées — restreindre à
{"true","false"} et retourner 400 sinon.

Sévérités : `bloquant` (exploitable en l'état), `majeur` (exploitable sous
condition), `mineur` (durcissement souhaitable).

## Sortie de secours

S'il n'y a aucun constat, répondre exactement :
« Aucun problème de sécurité identifié dans ce diff. »
Ne rien ajouter après cette phrase.

## Ne pas faire

- Aucun constat de style, de nommage ou de lisibilité.
- Aucune proposition de correctif hors du périmètre du diff.
- Aucun constat spéculatif du type « pourrait poser problème si un jour ».
- Ne jamais afficher la valeur d'un secret trouvé : indiquer fichier et ligne.
```

### 3.3 — Les quatre éléments qui font la différence

- **`description`** : elle contient un QUOI **et** un QUAND. Le QUAND est ce qui
  permet le déclenchement automatique. Sans lui, la skill n'existe que sous `/`.
- **La sortie de secours** : sans elle, l'agent inventera des constats pour ne pas
  rendre une réponse vide. C'est le remède le plus efficace au bruit.
- **La section « Ne pas faire »** : c'est ce qui améliore le plus la qualité perçue.
- **`disallowed-tools: Edit Write`** : retire ces outils du pool pendant que la skill
  est active. **C'est ce champ qui empêche la skill de modifier des fichiers**, pas
  `allowed-tools` — qui, lui, pré-approuve des outils sans les restreindre. Les deux
  se lisent en sens inverse et c'est la confusion la plus fréquente.

### 3.4 — Recharger

Les skills sont détectées à chaud, mais en cas de doute :

```
/exit
```

```bash
claude
```

---

## Étape 4 — Tester l'invocation explicite 

Dans la session :

```
/revue-securite
```

**Ce que vous devez voir** : la skill s'exécute, lance `git diff`, produit des
constats au format demandé, et **ne modifie aucun fichier**.

Sur le diff de A1, les constats plausibles sont : `todo_id` typé par la route donc
sûr, absence totale d'authentification sur une route qui expose des données,
absence de limite de longueur sur `title` en POST et en PATCH, `debug=True` dans
`app.run`.

**Si le format n'est pas respecté**, ne réécrivez pas la procédure : rendez la
section « Format de sortie » plus directive en donnant un exemple littéral de ligne
attendue. C'est ce qui marche.

**Vérifiez l'absence d'effet de bord :**

```bash
git status
```

Aucun fichier ne doit avoir changé.

---

## Étape 5 — Committer 

```bash
git add .claude/skills/
git commit -m "atelier A2 : skill de revue de securite"
```

---

## Résultat attendu

- [ ] Une skill invocable par `/revue-securite`
- [ ] Un déclenchement automatique 
- [ ] Une sortie au format imposé, sans constat cosmétique
- [ ] `git status` propre après exécution : la skill n'a rien modifié
- [ ] La sortie de secours fonctionne quand il n'y a rien à signaler

## Commandes vues dans cet atelier

| Commande | Rôle |
|---|---|
| `/` puis les premières lettres | Filtrer la liste des skills et commandes |
| `/revue-securite` | Invocation explicite de votre skill |
| `/security-review` | La skill intégrée équivalente — comparez vos résultats |
| `/code-review` (alias `/review`) | Revue de diff intégrée |
| `/context` | Vérifier ce que le chargement de la skill a coûté |

## Frontmatter : les champs qui servent vraiment

| Champ | Effet |
|---|---|
| `name` | Nom affiché. Par défaut : le nom du dossier |
| `description` | **L'interface publique.** Décide du déclenchement automatique |
| `when_to_use` | Phrases déclencheuses supplémentaires, ajoutées à `description` |
| `allowed-tools` | Outils **pré-approuvés** le temps du tour (ne restreint rien) |
| `disallowed-tools` | Outils **retirés** le temps du tour — c'est le verrou |
| `disable-model-invocation: true` | Interdit le déclenchement automatique : `/nom` seulement |
| `user-invocable: false` | L'inverse : seul l'agent peut la charger |
| `context: fork` | Exécute la skill dans un sous-contexte isolé |
| `agent` | Quel type de subagent utiliser avec `context: fork` |
| `paths` | Globs qui limitent l'activation automatique |
| `argument-hint` | Aide d'autocomplétion : `[fichier]` |


## Piste experte

1. **Contexte isolé, mesuré.** Ajoutez au frontmatter :

   ```yaml
   context: fork
   agent: Explore
   background: false
   ```

   Relancez la skill sur un diff volumineux et comparez `/context` avant / après
   avec la version non isolée. **L'écart est le bénéfice de l'isolation, en tokens.**
   Notez-le sur la fiche de suivi : c'est la même mesure qu'à l'atelier A3.


