---
name: revue-securite
description: Effectue une revue de sécurité ciblée des modifications du code et des diffs Git. Recherche les vulnérabilités, risques d'injection, entrées non validées, problèmes de contrôle d'accès, secrets exposés, configurations dangereuses et fuites de données. À utiliser lorsqu'une revue de sécurité, une analyse de vulnérabilité, un risque de sécurité, une injection, une CVE ou une modification potentiellement sensible est demandée, notamment lors de changements de routes HTTP, de validation d'entrées ou de configuration de démarrage.
allowed-tools: bash
context: fork
---

## Périmètre

Analyser uniquement le diff de la branche courante par rapport à `main`.

Ne modifier aucun fichier.

## Procédure

1. Exécuter `git diff main...HEAD` pour délimiter le périmètre exact.
2. Si la commande ne retourne rien, utiliser `git diff HEAD`.
3. Pour chaque fichier touché, vérifier dans cet ordre :
    - entrée utilisateur atteignant un chemin de fichier, une commande ou une requête
    - champ accepté sans validation de type, de longueur ou de valeurs autorisées
    - contrôle d'accès : la route vérifie-t-elle qui appelle ?
    - secrets en clair : jetons, mots de passe, chaînes de connexion
    - configuration dangereuse : mode debug, CORS ouvert, écoute sur `0.0.0.0`
    - donnée sensible renvoyée au client ou journalisée
4. Consulter `references/checklist.md` uniquement si le diff touche une route HTTP ou la configuration de démarrage.

## Format de sortie

Un constat par ligne, exactement dans ce format :

app.py:41 — **majeur** — le paramètre `completed` est comparé sans être validé contre une liste de valeurs autorisées — restreindre à `{"true","false"}` et retourner 400 sinon.

Sévérités :
- `bloquant` : exploitable en l'état
- `majeur` : exploitable sous condition
- `mineur` : durcissement souhaitable

## Sortie de secours

S'il n'y a aucun constat, répondre exactement :

« Aucun problème de sécurité identifié dans ce diff. »

Ne rien ajouter après cette phrase.

## Ne pas faire

- Aucun constat de style, de nommage ou de lisibilité.
- Aucune proposition de correctif hors du périmètre du diff.
- Aucun constat spéculatif du type « pourrait poser problème si un jour ».
- Ne jamais afficher la valeur d'un secret trouvé : indiquer fichier et ligne.
- Ne jamais modifier, créer ou supprimer un fichier.
- Ne jamais exécuter de build, de test ou de commande autre que celles nécessaires à l'inspection du diff et de son état Git.