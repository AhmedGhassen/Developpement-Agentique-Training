# Atelier A8 — Faire attraper à la machine ce que l'œil ne voit pas

**Jour 2 · 55 min · individuel** · Dépôt : `todo-app-new-feature/workshop1` · Outil : **Claude Code**

## Objectif

À la fin de l'atelier, vous aurez un test qui **échoue automatiquement quand un
espacement bouge de deux pixels**. Aujourd'hui, personne dans votre équipe ne
détecterait ça avant qu'un utilisateur le signale.

## La tâche

L'API renvoie un champ `priority` (`low` / `normal` / `high`) pour chaque tâche.
**Le front ne l'affiche pas.** Vous allez ajouter le badge de priorité — mais dans un
ordre précis : décrire d'abord, coder ensuite, mesurer, puis verrouiller.

## Ce dont vous avez besoin

Claude Code, Python, et un navigateur que l'agent peut piloter.

---

# Étape 0 — Préparer

### 0.1 — Le dossier

```powershell
cd D:\Documents\nvidia-courses\agenticAI\todo-app-new-feature\workshop1
git checkout -b atelier-a8
```

### 0.2 — Lancer l'application dans une SECONDE fenêtre PowerShell

```powershell
cd D:\Documents\nvidia-courses\agenticAI\todo-app-new-feature\workshop1
python app.py
```

**Laissez cette fenêtre ouverte** tout l'atelier.

### 0.3 — Regarder la page

Ouvrez **http://localhost:5000**

**Vous devez voir** : quatre tâches, avec un badge de catégorie chacune
(TRAVAIL, URGENT, PERSO). **Aucun badge de priorité.**

### 0.4 — Vérifier que la donnée existe pourtant

```powershell
curl.exe "http://localhost:5000/api/todos"
```

**Vous devez voir** `"priority": "normal"` dans chaque tâche. L'information est là,
elle n'est simplement affichée nulle part.

---

# Étape 1 — Brancher le navigateur

Choisissez **une** voie.

### Voie A — votre Chrome · *extension Claude in Chrome installée*

```powershell
claude --chrome
```

### Voie C — navigateur jetable · *aucune extension, marche partout*

```powershell
claude mcp add --scope project playwright -- npx -y '@playwright/mcp@latest'
claude
```

### Vérifier la connexion

Dans la session :

```
/mcp
```

**Vous devez voir** le serveur `claude-in-chrome` ou `playwright`, connecté.

### Test de fumée — indispensable

```
Ouvre http://localhost:5000 et dis-moi ce que tu vois : combien de tâches,
quels badges, quels filtres.
```


---

# Étape 2 — Donner des noms aux valeurs

Ouvrez `static/style.css`. Les couleurs et les distances y sont écrites en clair, et
répétées : le bleu `#0071e3` apparaît deux fois, `8px` trois fois, aucune n'a de nom.

**Le problème** : vous ne pouvez pas écrire une spécification qui dit « même bleu que
les boutons » si ce bleu n'a pas de nom. Vous écririez `#0071e3`, et vous auriez
recréé le problème.

### 2.1 — Le prompt

```
Analyse static/style.css et inventorie les valeurs répétées : couleurs,
espacements, rayons, tailles de police.

Propose un bloc :root de variables CSS qui les nomme, puis remplace les
valeurs en clair par ces variables.

Aucun changement visuel : le rendu doit être strictement identique après ta
modification.

Montre-moi le bloc :root avant de modifier le fichier.
```

### 2.2 — Ce que ça produit

```css
:root {
  --color-accent: #0071e3;
  --color-border: #d2d2d7;
  --space-sm: 8px;
  --radius-md: 8px;
}

button       { background: var(--color-accent); }
.filter-btn.active { background: var(--color-accent); }
```

Le bleu n'est plus écrit qu'**à un seul endroit**. Partout ailleurs, on l'appelle par
son nom.

### 2.3 — Vérifier — c'est un renommage, pas une décoration

Rechargez http://localhost:5000 avec **Ctrl+F5**.

**Rien ne doit avoir bougé.** Ni les couleurs, ni les espacements, ni les badges.
Si quelque chose a changé, l'agent a regroupé deux valeurs différentes sous un même
nom — demandez-lui de revenir en arrière.

### 2.4 — Committer

```powershell
git add static/style.css
git commit -m "atelier A8 : valeurs CSS nommees, rendu inchange"
```

---

# Étape 3 — Écrire la spécification, sans une ligne de code

**C'est l'étape que tout le monde saute, et c'est celle qui décide de tout le reste.**
Sans elle, l'agent compare son résultat à rien, et vous validez à l'œil.

### 3.1 — Le prompt

```
Écris specs/badge-priorite.md : la spécification du badge de priorité qui
sera affiché sur chaque carte de tâche, à droite du badge de catégorie.

Décris :
- sa position et son espacement par rapport au titre et au badge de catégorie
- sa taille de police, sa graisse, son rayon
- ses couleurs de fond, de texte et de bordure pour low, normal et high
- ce qui se passe quand le titre de la tâche est très long

Exprime chaque valeur avec les variables :root existantes. Si aucune
variable ne correspond, dis-le et propose la variable manquante — ne mets
aucune valeur en clair.

Donne le ratio de contraste texte/fond de chacune des trois variantes.

N'écris aucun code à cette étape.
```

### 3.2 — Relire le fichier

```powershell
notepad specs\badge-priorite.md
```



### 3.3 — Committer la spécification AVANT le code

```powershell
git add specs/
git commit -m "atelier A8 : specification du badge de priorite"
```

C'est volontaire : la spécification est datée avant l'implémentation. On pourra
prouver qu'elle n'a pas été réécrite après coup pour coller au résultat.

---

# Étape 4 — Implémenter

### 4.1 — Le prompt

```
Implémente le badge de priorité dans static/script.js et static/style.css,
en respectant strictement specs/badge-priorite.md.

Aucune valeur en clair : uniquement les variables :root.
Le badge de catégorie existant ne change pas.

Si la spécification est ambiguë sur un point, arrête-toi et pose-moi la
question au lieu de choisir à ma place.
```


### 4.2 — Regarder

Rechargez http://localhost:5000 avec **Ctrl+F5**.

**Vous devez voir** un second badge sur chaque tâche.

---

# Étape 5 — La boucle de vérification


### 5.1 — Tester les cas prévus par la spécification

```
Crée trois tâches via l'interface : une "high" avec un titre très long,
une "low", une "normal". Vérifie que le badge ne déborde pas et que le
titre reste lisible dans les trois cas.
```

### 5.2 — Mesurer ce que ça coûte

```
/context
```

Notez le chiffre. Les captures et le DOM consomment beaucoup. Si la consommation
dérape, demandez à l'agent de cibler un sélecteur précis au lieu de lire toute la page.

---

# Étape 6 — Le verrou anti-régression

### 6.1 — Installer l'outillage

```powershell
pip install pytest-playwright
playwright install chromium
```

### 6.2 — Créer le test

```
Ajoute tests/test_visuel.py : un test Playwright qui compare le rendu de la
liste des tâches à une capture de référence, pixel par pixel.

Utilise la comparaison visuelle intégrée de Playwright :

    expect(page.locator("#todo-list")).to_have_screenshot("todo-list.png")

Ne compare PAS les dimensions du bloc : un test qui vérifie seulement la
taille laisse passer un décalage de deux pixels et tout changement de
couleur.

Contraintes :
- fixe la taille de la fenêtre à 1280x720 pour que le rendu soit stable
- attends que la liste contienne au moins une tâche avant de capturer
- tolérance stricte : max_diff_pixels=100
- cible #todo-list, pas la fenêtre entière

Explique-moi la commande pour générer la capture de référence.
```

```powershell
python -m pytest -q tests/test_visuel.py
```

**Vous devez voir** : `1 passed`.

### 6.3 — Le casser — c'est le seul moment qui prouve quelque chose

```
Dans style.css, remplace l'espacement horizontal du badge de priorité par
la variable d'espacement immédiatement inférieure.
```

Rechargez la page : **vous ne verrez probablement aucune différence à l'œil.**
Deux pixels.

```powershell
python -m pytest -q tests/test_visuel.py
```

**Vous devez voir** : `1 failed`.

**C'est le résultat de l'atelier.** La machine a attrapé ce que votre œil n'a pas vu.

Un test de capture qui n'a jamais échoué ne garantit rien — il dort. Celui-ci vient de
prouver qu'il est réveillé.

### 6.4 — Remettre en état

```powershell
git checkout static/style.css
python -m pytest -q
```

---

# Étape 7 — Committer

```powershell
git add specs/ static/ tests/
git commit -m "atelier A8 : badge de priorite specifie, implemente, verrouille par capture"
```

---

# Résultat attendu

- [ ] Les valeurs de `style.css` nommées, **avec un rendu strictement identique**
- [ ] `specs/badge-priorite.md` écrit **et committé avant** tout code
- [ ] Le badge implémenté, aucune valeur en clair dans le diff
- [ ] Une boucle de vérification où l'agent **cite des valeurs mesurées**
- [ ] Un test de capture qui **échoue** sur un écart de deux pixels
- [ ] Une mesure `/context` après la boucle navigateur

# Ce qu'il faut retenir

| Constat | Conséquence |
|---|---|
| Sans spécification, l'agent compare son rendu à rien | Il « valide » toujours, et vous validez à l'œil |
| Sans vocabulaire, la spécification retombe en pixels | Nommer d'abord, spécifier ensuite |
| Deux pixels ne se voient pas, et se cumulent | Seule une capture de référence les attrape |
| Un test qui n'a jamais échoué ne garantit rien | Il faut le casser une fois pour le croire |

# Toutes les commandes de l'atelier

```powershell
# Préparer
cd D:\Documents\nvidia-courses\agenticAI\todo-app-new-feature\workshop1
git checkout -b atelier-a8
python app.py                          # seconde fenetre
curl.exe "http://localhost:5000/api/todos"

# Navigateur
claude --chrome
claude mcp add --scope project playwright -- npx -y '@playwright/mcp@latest'

# Verifier le diff
git diff static/style.css | Select-String -Pattern "#[0-9a-fA-F]{3,6}|[0-9]+px"

# Verrou visuel
pip install pytest-playwright
playwright install chromium
python -m pytest -q tests/test_visuel.py

# Remettre en etat
git checkout static/style.css

# Committer
git add specs/ static/ tests/
git commit -m "atelier A8 : badge de priorite specifie, implemente, verrouille par capture"
```

| Commande | Ce qu'elle fait |
|---|---|
| `claude --chrome` · `/chrome` | Pilote votre Chrome via l'extension |
| `claude mcp add … playwright` | Ajoute un navigateur jetable, sans extension |
| `/mcp` | Vérifie que le navigateur est connecté |
| `/context` | Mesure ce que coûte la boucle visuelle |
| `/design [brief]` | Skill intégrée : produire une maquette |
| `playwright install chromium` | Installe le navigateur des tests de capture |
| **Ctrl+F5** | Recharge la page sans le cache |

# Pièges classiques

| Symptôme | Cause | Correction |
|---|---|---|
| L'agent « valide » sans citer une valeur | Pas de spécification, ou prompt trop vague | Refaire l'étape 3, puis exiger les styles calculés |
| Des valeurs en clair dans le diff | Spécification écrite en pixels | Corriger la **spécification**, pas le code |
| Le rendu a changé après le nommage | Deux valeurs différentes regroupées | Revenir en arrière, recommencer par petits lots |
| La page n'affiche pas le nouveau badge | Cache du navigateur | **Ctrl+F5** |
| L'agent ne voit pas la page | `python app.py` arrêté, ou mauvais port | Relancer la seconde fenêtre |
| Le test de capture passe toujours | Il capture la fenêtre entière, ou tolérance trop haute | Cibler `#todo-list`, baisser la tolérance, **le casser pour vérifier** |
| Le test échoue sur une autre machine | Polices et rendu différents | Fixer la taille de fenêtre, ou exécuter en conteneur |
| Le contexte explose | Lectures de page entière répétées | Cibler un sélecteur, mesurer avec `/context` |
| Chaque action demande une approbation | Mode plan actif | **Shift+Tab** pour en sortir |

# Piste experte

### 1. Chiffrer le coût de la boucle

| Mesure | Valeur |
|---|---|
| `/context` avant la boucle | |
| `/context` après 3 itérations | |
| Coût moyen par itération | |

Puis testez **une** optimisation — lire un sélecteur au lieu de la page entière — et
mesurez le gain.

### 2. L'accessibilité, qui est mesurable

```
Injecte axe-core dans la page, lance l'analyse, et liste les violations de
contraste et de rôles ARIA sur la liste des tâches. Corrige celles qui
concernent les badges.
```

Notez combien de violations existaient **avant** votre badge. Il y en a.

### 3. La limite de la vérification automatique

Donnez au badge `high` une couleur moins visible que celle du badge `low`.

Le test de capture passe — vous avez régénéré la référence. `axe-core` passe — le
contraste est suffisant. Et pourtant la hiérarchie visuelle est fausse.

**Conclusion à énoncer** : l'agent fait converger le **mesurable**, l'humain tranche
l'**intention**. Savoir dire où passe cette frontière est le vrai livrable de l'atelier.

### 4. Partir d'une maquette plutôt que du code

```
/design une carte de tâche avec badge de catégorie et badge de priorité,
trois variantes de priorité, dans le style visuel actuel de l'application
```

Refaites l'étape 3 en spécifiant depuis la maquette. Comparez les deux
spécifications : laquelle est la plus exploitable ?

# Dépannage

**L'extension Chrome ne se connecte pas** — vérifiez qu'elle est activée dans
`chrome://extensions`, que vous êtes sur le même compte, et relancez `/chrome`.

**Le navigateur ne peut pas ouvrir `localhost`** — le navigateur intégré de l'app
Desktop ne voit pas un serveur lancé ailleurs. Utilisez Claude in Chrome ou Playwright.

**`playwright install` échoue derrière un proxy** — définissez `HTTPS_PROXY`, ou sautez
l'étape 6. Le reste de l'atelier tient debout, vous perdez seulement le verrou.

**`pip install pytest-playwright` échoue** — vérifiez que votre environnement virtuel
est activé : `.\.venv\Scripts\Activate.ps1`.

**Le rendu diffère entre le navigateur de l'agent et le vôtre** — zoom, taille de
fenêtre, thème système. Fixez la taille de fenêtre dans le test et notez-la dans la
spécification.
