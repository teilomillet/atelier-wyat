<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Étape 2 — Cadrer la décision (sans modèle)

**Situation.** Avant de brancher le modèle, l'équipe définit les options. Quelqu'un propose : *« Mettons juste un mot par option (`Facturation`, `Technique`…), et ajoutons une option "Pas sûr : demander à un humain" pour être prudents ! »*

**Ce qui se passe et pourquoi**
1. **Ce qu'on observe (`notebooks/bloc1_demo.ipynb`).** Si on ajoute une option fourre-tout *« Pas sûr ou pas clair : transmettre à une personne »*, même une panne évidente (*« la box clignote rouge depuis hier soir »*) quitte `technique` et tombe dans `humain` (`P = 0,48`) ! Et si on ne met qu'un seul mot par option, le score tombe à **65,1 %** (`41/63`).
2. **La question.** Pourquoi une panne de box évidente est-elle aspirée par l'option « pas sûr » ?
3. **Pourquoi le doute ne doit pas être une option.** Le modèle ne connaît pas vos habitudes internes : il ne lit que les mots écrits dans chaque option. Une case floue (« pas sûr », « tout le reste », « divers ») ressemble à tout et aspire les messages clairs. On gère donc le doute par une **règle d'escalade sur la marge**, jamais par une option fourre-tout.

**À vous de jouer** : complétez `travail/cadrage.toml`
```toml
question = "Quel service doit traiter ce message client ?"
escalade = "Si la marge est faible, ou si le client parle de décès ou de justice : un conseiller lit le message."
[options]
facturation = "Facturation et paiements : montant d'une facture, débits ou prélèvements bancaires, remboursement"
[actions]
facturation = "File Compta, réponse sous 48 h"
```

**Vérifier** (`atelier verifier 2`)
- **3 à 8 options**, chacune décrite en **au moins 6 mots** ;
- **aucun fourre-tout** (« pas sûr », « tout le reste », « divers », « inconnu »…) ;
- une **action concrète** par option dans `[actions]` ;
- une règle **`escalade`** qui dit quand un humain reprend la main.

**Indices**
1. Décrivez ce que chaque option couvre, comme si vous l'expliquiez à un nouveau collègue.
2. Mettez les mots qu'utilisent les clients : *prélevé*, *débité*, *remboursé*, *colis*, *carte SIM*, *résilier*.
3. Supprimez toute option « pas sûr / tout le reste » de `[options]` : mettez cette règle dans `escalade`.
