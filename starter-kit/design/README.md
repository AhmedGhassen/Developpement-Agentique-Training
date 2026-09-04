# Maquette de secours — atelier A8

À utiliser quand l'accès Figma (ou l'accès au serveur MCP de design) n'est pas
disponible. C'est le cas le plus fréquent en entreprise : prévoyez-le.

## Fichiers

| Fichier | Pour qui | Quand le distribuer |
|---|---|---|
| `card-facture.html` | Participants | Dès le début de l'atelier |
| `specs-reference/card.md` | Formateur | **Après** l'étape 4, pour comparer |

## Mode d'emploi

1. Ouvrez `card-facture.html` dans un navigateur. C'est la « maquette » de l'atelier :
   trois états d'un composant `Card` de facture (default, hover, disabled).
2. Les participants ne réimplémentent **pas** ce HTML. Ils doivent :
   - étape 2 : produire `specs/card.md` en observant la maquette
   - étape 3 : implémenter le composant dans le système du projet, avec ses tokens
   - étape 4 : vérifier le rendu dans le navigateur contre leur propre spécification
3. À l'étape 4, sortez `specs-reference/card.md` et comparez avec les spécifications
   produites par les participants. Les écarts sont le matériau du debrief.

## Pourquoi une maquette en HTML plutôt qu'une image

Une image force l'agent à estimer des valeurs au pixel. Un HTML avec variables CSS
permet de démontrer le vrai geste de l'atelier : **extraire des tokens, pas des
pixels**. C'est précisément ce qui distingue une spécification exploitable d'une
description approximative.

Si vous voulez la difficulté maximale (estimation visuelle pure), faites une capture
d'écran de la page et ne distribuez que l'image.

## Ce que le debrief doit faire ressortir

- Combien de participants ont écrit `padding: 16px` au lieu de `spacing.md` ?
- Combien ont décrit les **trois** états, et pas seulement l'état par défaut ?
- Combien ont signalé les valeurs pour lesquelles **aucun token n'existe** dans leur
  projet, au lieu de coder la valeur en dur ?
- Combien ont documenté la transition (durée, courbe) et le comportement responsive ?

La dernière question est celle que presque tout le monde manque : une spécification
qui oublie le mouvement produit une implémentation qui semble correcte sur capture
et fausse à l'usage.
