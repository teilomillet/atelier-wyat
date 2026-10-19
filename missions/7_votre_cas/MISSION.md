<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Étape 7 — Adapter à votre propre cas

**Situation.** Vous voulez maintenant appliquer un modèle de décision à votre propre projet ou à votre équipe.

**Ce qui se passe et pourquoi (en regardant les 26 exemples de `cas_usage/`)**
1. **Ce qu'on observe.**
   - Poser une question négative floue (*« Est-ce un autre organisme que la mairie ? »*, cas 18) donne **`7/12`** ; la remplacer par un **`Choice` explicite** avec les options bien décrites monte à **`12/12`**.
   - Mettre des montants chiffrés dans le prompt (notes de frais au cas 03, prix d'une annonce au cas 24) trompe le modèle (**`3/8`** au cas 24) ; séparer **les mots au modèle (`wyat`)** et **les chiffres/dates/listes au code** monte à **`12/12`** (cas 03) et **`6/8`** avec **`3/3` contrefaçons attrapées** (cas 24).
2. **La question.** Dans votre cas, qu'est-ce qui relève de la **compréhension des mots** (`wyat`), qu'est-ce qui relève d'un **calcul ou d'une règle exacte** (`if` en code), et sous quelle **marge** passez-vous la main à un humain ?

**À vous de jouer (en 3 étapes simples)**
1. Choisissez dans [`cas_usage/README.md`](../../cas_usage/README.md) le script (`01` à `26`) le plus proche de votre idée et copiez-le dans `travail/mon_cas/`.
2. Remplacez les options et `donnees.csv` par ~10 exemples de votre cas (en gardant **3 exemples de côté** pour vérifier à la fin).
3. Lancez `.venv/bin/python travail/mon_cas/cas.py`, changez **une seule chose** (une définition d'option, le seuil ou une règle de code), et relancez pour voir la différence.

**Pour aller en production**
- La checklist en 1 page : [`docs/fiches/fiche_entreprise.md`](../../docs/fiches/fiche_entreprise.md) et [`docs/integration_dev.md`](../../docs/integration_dev.md).
- Les poids `wyat-1-800m` sont gratuits pour apprendre et tester ([`docs/licence_du_modele.md`](../../docs/licence_du_modele.md)). Pour une licence commerciale ou un **modèle de décision sur mesure** entraîné sur vos données, contactez [Teïlo Millet](https://github.com/teilomillet).
