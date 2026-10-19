<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Étape 3 — Accord entre humains et test scellé (sans modèle)

**Situation.** Avant de tester le modèle, on donne les **15 mêmes messages** (`docs/fiches/fiche_bloc3_annotation.md`) à deux ou trois personnes, sans qu'elles se parlent. Sur *« internet coupe tout le temps, je vais finir par résilier »*, l'un coche `technique`, l'autre `resiliation`.

**Ce qui se passe et pourquoi**
1. **Ce qu'on observe.** Même entre humains expérimentés, les messages qui mélangent deux sujets créent des désaccords.
2. **Les deux questions.**
   - Si les humains eux-mêmes ne sont pas d'accord sur un message, un modèle peut-il « avoir juste » ?
   - Si on modifie nos options toute la semaine en regardant les erreurs sur les mêmes 63 messages, le score obtenu sera-t-il honnête ?
3. **Pourquoi on mesure le $\kappa$ et on scelle un test.**
   - Le **$\kappa$ (kappa) de Fleiss** mesure l'accord réel entre annotateurs *une fois retiré le hasard* (`0` = hasard, `1` = parfait, `> 0,4` = modéré, `> 0,6` = bon). C'est le **plafond** que le modèle ne pourra pas dépasser.
   - Pour ne pas tricher en réglant ses options sur les exemples qu'on regarde, on sépare les données en deux dès le départ : **`dev`** (`dataset/dev.csv`, 63 messages) pour travailler, et le **test scellé** (`dataset/test_scelle.csv`, 77 messages) qu'on n'ouvrira **qu'une seule fois**, à la fin.

**À vous de jouer** : complétez `travail/annotations.csv`
Étiquetez les 15 messages (à deux ou trois personnes, ou vous en `A1` et votre assistant IA en `A2`) :
```csv
numero,A1,A2
1,facturation,facturation
```

**Vérifier** (`atelier verifier 3` ou `atelier accord travail/annotations.csv`)
- 15 messages et au moins 2 colonnes d'annotateurs (`A1`, `A2`…) ;
- affiche l'accord en %, le **$\kappa$ de Fleiss** et les **3 messages les plus disputés**.

**Indices**
1. Les 5 étiquettes s'écrivent sans accent : `facturation`, `technique`, `resiliation`, `livraison`, `autre`.
2. Le $\kappa$ est plus bas que le % d'accord brut : il retire la part due au hasard.
3. Regardez les 3 messages les plus disputés : donnez-vous une règle simple pour les messages à deux sujets.
