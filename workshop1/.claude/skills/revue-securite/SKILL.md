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