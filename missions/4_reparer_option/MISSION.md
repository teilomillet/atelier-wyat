<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Étape 4 — Le libellé d'une option est sa définition

**Situation.** Quelqu'un raccourcit l'option `facturation` en *« Facturation : questions sur les factures »* pour que ce soit « plus propre ». Aussitôt, les messages *« vous m'avez débité 9,99 € »* et *« le prélèvement n'est pas passé »* partent chez `autre`. Personne n'a touché au code ni au modèle : seule une phrase dans `options.toml` a changé.

**Ce qui se passe et pourquoi**
1. **Ce qu'on observe (`atelier evaluer --options travail/options.toml --erreurs`).** Avec cette option raccourcie, le score sur `dev` chute de **87,3 % (`55/63`)** à **76,2 % (`48/63`)**.
2. **La question.** En lisant les erreurs affichées par `--erreurs`, quels mots reviennent dans les messages de `facturation` que le modèle a ratés ?
3. **Pourquoi le libellé est la définition.** Le modèle ne devine pas vos habitudes : il compare le message du client aux mots écrits dans chaque option. Si `facturation` ne parle que de « factures », un client qui parle de « prélèvement », de « débit » ou de « remboursement » part ailleurs. L'avantage : **on corrige le comportement du modèle simplement en précisant la définition en français**, sans ré-entraîner.

**À vous de jouer** : réparez l'option `facturation` dans `travail/options.toml` *(en travaillant uniquement sur `dev`)*

**Vérifier** (`atelier verifier 4`)
- les 5 clés (`facturation`, `technique`, `resiliation`, `livraison`, `autre`) sont conservées ;
- exactitude sur `dev` **≥ 85 %** (au moins **+5 points** par rapport au départ).

> **Règle du jeu** : ne regardez pas le test scellé maintenant — on l'ouvrira une seule fois à la fin de l'étape 5.

**Indices**
1. Lancez `atelier evaluer --options travail/options.toml --erreurs` et lisez les messages `facturation` mal classés.
2. Ajoutez dans `facturation` les mots des clients : *montant d'une facture, débits ou prélèvements bancaires, remboursement, paiement*.
3. N'ajoutez pas de formule « tout le reste » dans `autre` : elle aspirerait les messages des autres services (`65,1 %`).
