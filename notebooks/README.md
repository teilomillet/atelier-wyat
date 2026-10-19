<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Les 5 notebooks de l'atelier

Si vous aimez explorer de façon visuelle (tableaux, graphiques de marges, courbes de calibration), vous pouvez parcourir ces notebooks dans Jupyter :

```sh
.venv/bin/jupyter lab notebooks/
```

> **Astuce :** si vous voulez juste lire les résultats et les graphiques sur GitHub sans rien lancer, ouvrez directement le dossier [`executes/`](executes/) qui contient les mêmes notebooks déjà exécutés avec leurs vraies sorties.

| Notebook | Version déjà exécutée | Ce qu'on y voit |
|---|---|---|
| [`bloc1_demo.ipynb`](bloc1_demo.ipynb) | [`bloc1_demo_execute.ipynb`](executes/bloc1_demo_execute.ipynb) | Première décision, probabilités par option, **marge**, et pourquoi l'option fourre-tout « pas sûr » échoue. |
| [`bloc3_accord_annotateurs.ipynb`](bloc3_accord_annotateurs.ipynb) | [`bloc3_accord_annotateurs_execute.ipynb`](executes/bloc3_accord_annotateurs_execute.ipynb) | Calcul de l'accord entre annotateurs ($\kappa$ de Fleiss) et messages où même les humains hésitent. |
| [`bloc4_lancer_wyat.ipynb`](bloc4_lancer_wyat.ipynb) | [`bloc4_lancer_wyat_execute.ipynb`](executes/bloc4_lancer_wyat_execute.ipynb) | Évaluation sur les 63 messages de `dev`, distribution des marges (bonnes réponses vs erreurs) et réparation d'une option. |
| [`bloc5_mesurer_et_choisir.ipynb`](bloc5_mesurer_et_choisir.ipynb) | [`bloc5_mesurer_et_choisir_execute.ipynb`](executes/bloc5_mesurer_et_choisir_execute.ipynb) | Choix du **seuil de marge**, courbe de calibration et ouverture finale du **test scellé** *(à ouvrir après l'étape 5)*. |
| [`bloc6_securite_et_limites.ipynb`](bloc6_securite_et_limites.ipynb) | [`bloc6_securite_et_limites_execute.ipynb`](executes/bloc6_securite_et_limites_execute.ipynb) | Garde-fou sur les commandes shell d'un agent IA, détection d'arnaques SMS/e-mail, injections de prompt et limites. |
