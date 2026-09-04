# Guide — Versionner le projet Workshop sur GitHub

Ce guide reprend, dans l'ordre, toutes les étapes pour :
1. Créer un repo privé GitHub
2. S'authentifier correctement (token)
3. Organiser le projet dans un sous-dossier `workshop1/`
4. Pousser le tout sur GitHub

---

## 1. Créer le repo privé sur GitHub

🔗 **https://github.com/new**

| Champ | Valeur |
|---|---|
| Repository name | `Developpement-Agentique-Training` |
| Visibility | **Private** ✅ |
| Add a README file | ❌ ne pas cocher |
| Add .gitignore | ❌ ne pas cocher |
| Add license | ❌ ne pas cocher |

Clique sur **Create repository**.

---

## 2. Créer un Personal Access Token (authentification)

GitHub n'accepte plus les mots de passe classiques en ligne de commande depuis 2021 — il faut un **token**.

🔗 **https://github.com/settings/tokens**

### Si tu utilises un token classique (recommandé, plus simple)

1. **Generate new token** → **Generate new token (classic)**
2. Note : `workshop-todo-app`
3. Expiration : 30 jours (ou selon préférence)
4. Cocher la case **`repo`** (coche automatiquement toutes les sous-permissions)
5. **Generate token**
6. Copier le token affiché (`ghp_...`) — **il ne sera plus jamais visible ensuite**

### Si tu utilises un token fine-grained

1. **Generate new token** → **Fine-grained tokens**
2. Repository access : **All repositories** (ou "Only select repositories" + choisir le repo)
3. Dans **Permissions > Repository permissions**, régler **Contents** sur **Read and write**
4. **Generate token**
5. Copier le token affiché

> ⚠️ **Ne jamais coller le token en clair dans un chat, un fichier commité, ou un message partagé.** Traite-le comme un mot de passe.

---

## 3. Nettoyer un éventuel cache d'identifiants invalide (si erreurs répétées)

```powershell
git config --global --unset credential.helper
```

Si l'erreur persiste malgré un bon token, vérifier le **Gestionnaire d'identifiants Windows** :
- Démarrer → *Gestionnaire d'identifiants* → *Identifiants Windows*
- Supprimer toute entrée `git:https://github.com`

---

## 4. Organiser le projet en local dans `workshop1/`

Se placer dans le dossier du projet (celui contenant déjà `.git`) :

```powershell
cd D:\Documents\nvidia-courses\agenticAI\todo-app
```

Créer le sous-dossier et y déplacer tous les fichiers du projet :

```powershell
mkdir workshop1
Move-Item -Path app.py, static, tests, requirements.txt, README.md, .gitignore -Destination workshop1
```

Vérifier l'arborescence obtenue :

```powershell
Get-ChildItem -Recurse -Depth 1
```

Structure attendue :

```
todo-app/                     (dossier de travail local, hors du repo)
├── .git/
└── workshop1/
    ├── app.py
    ├── static/
    │   ├── index.html
    │   ├── style.css
    │   └── script.js
    ├── tests/
    │   └── test_app.py
    ├── requirements.txt
    ├── README.md
    └── .gitignore
```

Committer cette réorganisation :

```powershell
git add -A
git commit -m "Réorganisation: projet déplacé dans workshop1/"
```

---

## 5. Relier le repo local au repo distant et pousser

```powershell
git remote set-url origin https://HediFkih:TON_TOKEN@github.com/HediFKIH/Developpement-Agentique-Training.git
git branch -M main
git push -u origin main
```

*(Remplacer `TON_TOKEN` par le vrai token généré à l'étape 2, collé directement dans le terminal — jamais partagé ailleurs.)*

### Nettoyer l'URL après un push réussi (optionnel, recommandé)

Une fois le premier push confirmé, retirer le token de l'URL stockée (Git/Windows retiendra l'authentification correctement après un push réussi) :

```powershell
git remote set-url origin https://github.com/HediFKIH/Developpement-Agentique-Training.git
```

---

## 6. Vérification finale

🔗 **https://github.com/HediFKIH/Developpement-Agentique-Training**

Le repo doit afficher un dossier `workshop1/` contenant tous les fichiers du projet, avec l'historique des commits visible.

---

## 7. Rappel — introduire le bug volontaire (point de départ du workshop)

Dans `workshop1/app.py`, repérer la fonction `get_todos()` et modifier cette ligne :

```python
want_completed = completed_param.lower() == "true"
```

en :

```python
want_completed = completed_param.lower() != "true"
```

Committer et pousser ce "mauvais commit" :

```powershell
git add -A
git commit -m "fix: améliore la lisibilité du filtre completed"
git push
```

Vérifier que le bug est actif :

```powershell
cd workshop1
pytest -v
```

→ 2 tests doivent échouer (`test_filter_completed_true_returns_only_completed`, `test_filter_completed_false_returns_only_incomplete`).

C'est ce commit buggé qui servira de point de départ au workshop (ticket Jira, branche de correction, fix par l'agent IA, test, PR, merge).

---

## Annexe — Commandes de dépannage rapides

| Problème | Commande |
|---|---|
| Vérifier le dossier courant | `pwd` (bash) / `Get-Location` (PowerShell) |
| Vérifier si `.git` existe | `Get-ChildItem -Force` (doit lister `.git`) |
| Voir l'historique des commits | `git log --oneline` |
| Voir le(s) remote(s) configuré(s) | `git remote -v` |
| Supprimer un remote existant | `git remote remove origin` |
| Voir le statut courant | `git status` |
