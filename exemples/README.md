<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# 7 petits scripts pour découvrir `wyat`

Si vous préférez apprendre en lisant du code court plutôt que des slides, commencez ici dans l'ordre (`00` → `06`).
Chaque script fait entre 15 et 45 lignes et peut se lancer avec le vrai modèle ou instantanément en mode pré-calculé (`WYAT_PRECALCULE=1`).

```sh
.venv/bin/python exemples/00_natif_contre_wyat.py
# ou sans charger le modèle :
WYAT_PRECALCULE=1 .venv/bin/python exemples/00_natif_contre_wyat.py
```

| Script | Ce qu'il montre en quelques lignes |
|---|---|
| [`00_natif_contre_wyat.py`](00_natif_contre_wyat.py) | Compare un tri par **mots-clés** (`45/63`, 0 abstention) au même tri avec **`wyat`** (`55/63` + **marge de confiance** quand un message mélange deux sujets). |
| [`01_une_decision_wyat.py`](01_une_decision_wyat.py) | L'API `wyat` pure en 15 lignes : `wyat.load()`, `Request.choice()`, `d.selected`, `d.probability_margin`, `d.probabilities_by_id`. |
| [`02_une_decision_atelier.py`](02_une_decision_atelier.py) | Même chose avec l'assistant de l'atelier (`atelier.modele.decider`), et le piège du message `"bonjour"` classé avec une forte marge. |
| [`03_evaluer_un_jeu.py`](03_evaluer_un_jeu.py) | Évaluer un fichier d'options (`options.toml`) sur les 63 messages de `dataset/dev.csv` : exactitude, intervalle de confiance et liste des erreurs. |
| [`04_balayer_les_seuils.py`](04_balayer_les_seuils.py) | Tester différents **seuils de marge** (`0.0`, `0.2`, `0.5`…) pour voir combien d'erreurs disparaissent quand on passe les cas douteux à un humain. |
| [`05_garde_fou.py`](05_garde_fou.py) | Filtrer une commande shell (`git status`, `rm -rf "$BUILD_DIR"/`, `pg_dump …`) en combinant liste blanche, règles de code et questions oui/non (`Request.noul`). |
| [`06_arnaques.py`](06_arnaques.py) | Détecter un SMS/e-mail d'arnaque avec `Request.noul` et afficher les 4 signaux explicatifs (`urgence`, `identifiants`, `argent`, `imitation`). |
