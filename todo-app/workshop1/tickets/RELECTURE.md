# Relecture de TODO-150

1. Un developpeur pourrait-il l'implementer sans poser de question ?
   -> peut-être, mais il y a des ambiguïtés sur la manière de gérer la compatibilité avec les consommateurs externes et sur la transition entre l'ancien et le nouveau champ.

2. Quel test ecrirais-je en premier ?
   -> fais le bon choix : un test qui vérifie que l'API renvoie correctement le champ `amount_cents` et que l'ancien champ `amount` est toujours présent pour les consommateurs existants.

3. Qu'est-ce qui reste ambigu ?
   -> il faut décider comment gérer la compatibilité avec les consommateurs externes qui attendent toujours le champ `amount` et comment faire la transition entre l'ancien et le nouveau champ.
