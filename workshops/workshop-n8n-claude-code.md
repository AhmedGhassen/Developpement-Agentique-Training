# Workshop : Automatisation agentique avec n8n + Claude Code (MCP)

**Durée estimée : 3h30 - 4h**
**Niveau : débutant à intermédiaire**
**Prérequis participants : un ordinateur avec VS Code ou Claude Code installé, un compte email**

---

## Objectifs pédagogiques

À la fin de ce workshop, les participants sauront :
1. Connecter un agent IA (Claude Code) à n8n via le protocole MCP
2. Construire des workflows n8n **en langage naturel**, sans glisser-déposer manuel
3. Configurer un agent IA (AI Agent node) avec sortie structurée fiable
4. Diagnostiquer les pièges classiques (auth OAuth, mapping de données, formats de sortie)

---

## Partie 0 —

### Étape 0.1 — Créer un compte n8n Cloud

1. Aller sur **n8n.io**
2. Cliquer sur **Get Started** / **Start free trial**
3. Créer un compte (email ou Google/GitHub)
4. Noter l'URL de l'instance : `https://VOTRE-NOM.app.n8n.cloud`



### Étape 0.2 — Activer l'accès MCP sur l'instance

1. Dans n8n : **Settings > Instance-level MCP**
2. Cliquer sur **Enable MCP access**
3. Vérifier que le statut passe à **Enabled**

### Étape 0.3 — Importer le workflow de base (fourni par le formateur)

1. Dans n8n, cliquer sur **+ > Import from file** (ou **Import file** depuis l'écran d'accueil)
2. Importer le fichier `workshop-base.json` (squelette fourni : Form Trigger → nœud vide)
3. Enregistrer le workflow sous le nom **"workshop-translate"**

### Étape 0.4 — Exposer le workflow à MCP

1. **Settings > Instance-level MCP > Workflows exposed**
2. **Enable workflows** → sélectionner **"workshop-translate"** → **Enable**

### Étape 0.5 — Connecter Claude Code

Dans un terminal:

```bash
claude mcp add --transport http n8n-mcp https://VOTRE-NOM.app.n8n.cloud/mcp-server/http
```
```
https://brushless-douglas-retreative.ngrok-free.dev/mcp-server/http
```
Une fenêtre de navigateur s'ouvre pour l'authentification OAuth → se connecter avec le compte n8n créé à l'étape 0.1 → **Autoriser**.

### Étape 0.6 — Vérification

Dans Claude Code, taper :

```
Liste mes workflows n8n disponibles
```

✅ **Résultat attendu** : Claude Code répond en listant le workflow **"workshop-translate"**.

❌ **Si ça ne fonctionne pas**, vérifier dans cet ordre :
- MCP est bien "Enabled" dans les settings n8n
- Le workflow est bien coché dans "Workflows exposed"
- Relancer `claude mcp list` pour voir le statut de connexion

---

## Partie 1 — Prise en main : premier workflow via langage naturel (45 min)

### Exercice 1.1 — Créer un workflow simple par la conversation

**Objectif** : observer comment Claude Code traduit une demande en langage naturel en appels d'outils MCP concrets sur n8n.

**Prompt à donner aux participants :**

```
Crée un nouveau workflow n8n nommé "hello-world" avec :
- Un Webhook Trigger en GET
- Un nœud qui renvoie simplement le texte "Bonjour depuis n8n !"
Publie-le et donne-moi l'URL du webhook.
```

**Ce qu'il faut observer et commenter en groupe :**
- Claude Code liste d'abord les outils disponibles (`create_workflow`, `add_node`, etc.)
- Il construit le JSON du workflow étape par étape
- Il vous redonne l'URL testable à la fin

**Vérification :** ouvrir l'URL du webhook dans un navigateur → le texte "Bonjour depuis n8n !" doit s'afficher.

### Exercice 1.2 — Modifier ce workflow en langage naturel

**Prompt :**

```
Modifie le workflow "hello-world" pour qu'il renvoie maintenant un JSON
avec deux champs : message et date_actuelle (au format ISO).
```

**Point pédagogique** : Claude Code doit *retrouver* le workflow existant (recherche via `search_workflows`), l'ouvrir, et éditer un nœud existant plutôt que tout recréer — bonne illustration de la différence entre "create" et "edit" côté MCP.

---

## Partie 2 — Construire l'agent de traduction (60-90 min)

C'est l'exercice principal du workshop : reproduire un agent IA complet avec formulaire d'entrée, traitement par IA, sortie structurée, et écriture dans Google Sheets.

### Exercice 2.1 — Le formulaire d'entrée

**Prompt :**

```
Dans le workflow "workshop-translate", ajoute un nœud "On form submission"
avec :
- Un champ texte "text" (obligatoire)
- Titre du formulaire : "Traducteur IA"
- Description : "Entrez un texte à traduire"
```

**Vérification** : cliquer sur le nœud → récupérer la **Test URL** → l'ouvrir dans un navigateur → le formulaire doit s'afficher.

### Exercice 2.2 — L'agent IA avec sortie structurée

**Prompt :**

```
Ajoute un nœud AI Agent connecté à la sortie du formulaire, avec :
- Un modèle de chat (utilise le modèle configuré par défaut sur l'instance)
- Ce prompt système : "You are a translation agent. Receive the user's
  input text and detect its language, then translate it into Arabic,
  French, and English. Always return the original text unchanged."
- Une sortie structurée (Structured Output Parser) avec un schéma JSON
  exigeant CES CHAMPS COMME REQUIRED (obligatoires, pas optionnels) :
  original_text, arabic_text, french_text, english_text, notice (string)
```

> ⚠️ **Piège classique à anticiper avec le groupe** : si les champs du schéma JSON ne sont pas marqués `required`, le modèle peut renvoyer un objet vide `{}` qui passe quand même la validation. C'est l'erreur n°1 que vous rencontrerez en atelier — gardez ce point en tête pour dépanner rapidement.

**Test intermédiaire :**

```
Exécute uniquement le nœud AI Agent avec le texte de test "bonjour la vie"
et montre-moi le résultat JSON.
```

✅ **Résultat attendu** : un objet contenant les 5 champs remplis, pas un objet `output: {}` vide.

### Exercice 2.3 — Connecter à Google Sheets

**Prompt :**

```
Ajoute un nœud Google Sheets après l'AI Agent qui ajoute une ligne
(Append Row) avec les colonnes : original_text, arabic_text, french_text,
english_text, notice. Utilise le credential Google Sheets déjà configuré
sur l'instance (ou aide-moi à en créer un si besoin).
```

> ⚠️ **Piège classique n°2** : la sortie du Structured Output Parser est **imbriquée** sous une clé `output` (ex: `output.original_text`, pas `original_text` directement). En mode "Map Automatically", Google Sheets ne trouvera rien à mapper. Il faut soit :
> - Passer en **"Map Each Column Manually"** et référencer explicitement `{{ $json.output.original_text }}` pour chaque colonne
> - Ou insérer un nœud **Edit Fields (Set)** intermédiaire qui "aplatit" les champs avant l'écriture

**Prompt de correction si le mapping échoue :**

```
La sortie de l'AI Agent est imbriquée sous une clé "output". Corrige le
mapping du nœud Google Sheets pour que chaque colonne pointe vers
$json.output.NOM_DU_CHAMP au lieu de $json.NOM_DU_CHAMP.
```

### Exercice 2.4 — Test de bout en bout

1. Ouvrir la Test URL du formulaire
2. Soumettre un texte (ex: "good morning everyone")
3. Vérifier dans la Google Sheet que la ligne a bien été ajoutée avec les 5 colonnes remplies

**Debug collectif** : si une ligne vide apparaît, demander aux participants d'ouvrir le nœud Google Sheets → onglet **OUTPUT** → vérifier ce qui a été réellement envoyé.

---

## Partie 3 — Aller plus loin (60 min, selon niveau/temps restant)

Choisir 1 à 3 exercices selon le niveau du groupe.

### Exercice 3.1 (intermédiaire) — Ajouter une gestion d'erreur

**Prompt :**

```
Configure le nœud AI Agent pour qu'en cas d'échec de format de sortie,
il retente automatiquement 2 fois avant d'échouer, plutôt que d'arrêter
le workflow immédiatement.
```

Discussion en groupe : pourquoi les LLM ne respectent pas toujours un format structuré à 100% ? Notion de fiabilité du "tool calling".

### Exercice 3.2 (intermédiaire) — Ajouter un outil (Tool) à l'agent

**Prompt :**

```
Ajoute un outil de recherche web (HTTP Request Tool ou SerpAPI si
disponible) à l'AI Agent, pour qu'il puisse vérifier le sens d'une
expression idiomatique avant de la traduire.
```

Point pédagogique : différence entre un "Chat Model" simple et un "Agent" qui peut *décider* d'appeler des outils.

### Exercice 3.3 (avancé) — Workflow déclenché par un autre agent

**Prompt :**

```
Crée un second workflow "notif-slack" (ou email) qui est déclenché
automatiquement chaque fois qu'une nouvelle ligne est ajoutée à la
Google Sheet, envoyant un résumé de la traduction.
```

### Exercice 3.4 (avancé) — Audit du workflow par Claude Code

**Prompt :**

```
Analyse le workflow "workshop-translate" et propose 3 améliorations
possibles (robustesse, coût, lisibilité), sans les appliquer —
liste-les simplement.
```

Bon exercice de clôture : montre Claude Code en mode "consultant" plutôt que "exécutant".

---

## Partie 4 — Debrief (15 min)

Questions à poser en groupe :
- Qu'est-ce qui a été plus rapide en langage naturel vs. glisser-déposer manuel ?
- Où l'agent IA (Claude Code) s'est-il trompé ou a nécessité une correction ?
- Quels sont les risques d'exposer un serveur MCP publiquement (sécurité, tokens, accès) ?

---

## Annexe A — Checklist de dépannage rapide

| Symptôme | Cause probable | Solution |
|---|---|---|
| `MCP: List Servers` ne montre rien | Fichier de config mal formé ou fenêtre pas rechargée | Vérifier le JSON, puis `Developer: Reload Window` |
| Erreur OAuth "redirect_uri_mismatch" | URL de redirection non enregistrée côté Google/n8n | Vérifier la cohérence entre l'URL affichée dans n8n et celle enregistrée dans Google Cloud Console |
| "Model output doesn't fit required format" | Le modèle IA n'a pas respecté le schéma structuré | Relancer l'exécution ; si persistant, changer de modèle ou simplifier le schéma |
| Ligne ajoutée vide dans Google Sheets | Champs imbriqués sous "output" non mappés | Passer en mapping manuel avec `$json.output.champ` |
| "At least one value has to be added" | Champs de mapping vides côté Google Sheets | Remplir chaque valeur avec la bonne expression |

## Annexe B — Fichier workflow de base à fournir

Préparer un export JSON du squelette (Form Trigger vide, sans les nœuds AI Agent/Google Sheets) à distribuer avant le workshop, pour que chaque participant parte du même point.

## Annexe C — Prompt système complet pour l'AI Agent

```
You are a translation agent.

Your task is to receive the user's input, which may be in any language,
and:
1. Keep the original text unchanged (original_text)
2. Translate it into Arabic (arabic_text)
3. Translate it into French (french_text)
4. Translate it into English (english_text)
5. Add a short note (notice) mentioning the detected source language

Always return all five fields, even if some translations are identical
to the original text.
```
