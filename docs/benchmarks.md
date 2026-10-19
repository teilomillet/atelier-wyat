<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Benchmarks : ce qui motive les exemples, et ce qu'il faut en penser

The following are previously measured comparisons of wyat-1-800m versus D3-Lite. They motivate the examples; the new fixtures do not reproduce those benchmarks or establish a fresh head-to-head result.

*Traduction : les chiffres ci-dessous sont des comparaisons mesurées auparavant entre wyat-1-800m et D3-Lite. Ils motivent les exemples ; les nouveaux jeux de l'atelier ne reproduisent pas ces benchmarks et n'établissent pas une nouvelle comparaison.*

| Exemple lié | Évaluation et métrique | Wyat | D3-Lite | Population | Cas de l'atelier |
|---|---|---|---|---|---|
| Énoncé de groupe | JDI Habermas Machine, preference accuracy | 42.18% | 37.95% | 1,676 | [26](../cas_usage/26_synthese_consultation/README.md) |
| Tri d'hameçonnage | JDI PhishNChips, accuracy | 57.45% | 54.85% | 2,000 | [13](../cas_usage/13_hameconnage_mails/README.md) |
| Étiquettes d'avis | JDI ACOS, per-review F1 on a 0–100 scale | 8.05 | 6.45 | 400 reviews / 1,565 requests | [23](../cas_usage/23_avis_clients_aspects/README.md) |
| Pertinence produit | JDI Amazon ESCI, macro-F1 on a 0–100 scale | 42.72 | 41.28 | 5,000 | [24](../cas_usage/24_surveillance_annonces/README.md) |
| Sortie de code | JDI CRUXEval, accuracy | 34.56% | 33.68% | 570 | [15](../cas_usage/15_garde_code_genere/README.md) |
| Coup d'échecs | JDI ChessBench, accuracy | 8.60% | 8.34% | 5,000 | aucun (voir plus bas) |
| Conditions d'une demande | DMBench French v4 Conditions, modal Score accuracy | 30/40 | 24/40 | 20 paired families | [19](../cas_usage/19_conditions_acces_privilegie/README.md) |
| Passage de relais | DMBench French v4 Routing, Noul accuracy | 33/40 | 31/40 | 20 paired families | [18](../cas_usage/18_reorientation_usagers/README.md) |
| Demande modifiée | DMBench French v4 Updating, expected-score pair ordering | 10/12 | 8/12 | 12 pairs | [20](../cas_usage/20_demande_modifiee_virement/README.md) |
| Priorité d'incident | DMBench French v4 Escalation, normalized expected-score MAE ↓ | 0.1211 | 0.1249 | 40 questions / 20 paired families | [17](../cas_usage/17_priorite_alertes_securite/README.md) |

Sources : chiffres JDI de wyat dans [`runs/wyat-1-800m-public03/scores.json`](https://huggingface.co/datasets/teilomillet/wyat-1-800m-decision-index-0.3/blob/a0b54dfbd3a899af9af6c1bfc97cd3655151ce16/runs/wyat-1-800m-public03/scores.json) ; chiffres JDI de D3-Lite (« vLLM-SR d3-lite (0.8B) ») sur le [tableau public](https://multimodalart-jev-decision-index.static.hf.space/data/index.json) ; chiffres DMBench : DMBench French v4 (rapport « D3-Lite versus the two Wyat models on frozen French v4 », où wyat-1-800m porte son nom de travail RUN-13). Vérifié le 19/10/2026 : les deux adresses répondent et chaque chiffre du tableau correspond aux sources.

## Comment lire ce tableau

- **Ces lignes ont été choisies parce que wyat y fait mieux que D3-Lite.** Sur l'ensemble, c'est l'inverse : sur DMBench French v4, D3-Lite fait 85,8 % en Choice et 88,8 % en oui / non, contre 76,0 % et 79,0 % pour wyat-1-800m, avec une meilleure calibration (Brier 0,0875 contre 0,1749). Dans les mêmes catégories que le tableau, D3-Lite est devant sur d'autres formats : Routage en Choice 39/40 contre 35/40, Escalade en oui / non 38/40 contre 31/40, Mise à jour en Choice 38/40 contre 31/40.
- **Les écarts sont souvent petits** (ESCI +1,4 point, CRUXEval +0,9, ChessBench +0,3, Escalade 0,004 de MAE) et non testés statistiquement. 40 questions par case DMBench, c'est du bruit à quelques questions près.
- **Plusieurs scores absolus sont bas, ou proches du hasard.** Niveaux de hasard indiqués par le fichier de scores : PhishNChips 50 % (wyat 57,45 %), Habermas Machine 31,1 % (42,18 %), CRUXEval **36,97 %** (wyat 34,56 % et D3-Lite 33,68 % sont **sous** le hasard), ChessBench 8,19 % (8,60 %), ACOS 3,1 (8,05), ESCI 20,27 (42,72).
- Les chiffres JDI de wyat viennent de son propre fichier de résultats (soumis, non vérifié) : wyat-1-800m n'apparaît pas sur le tableau public. Indice global : 25,78 dans ce fichier (`decision_index` = `balanced_skill`). Sur le tableau public, D3-Lite a `balanced_skill` 32,33 et `public_skill` 36,93 : pour comparer, prenez la même colonne.

## Ce que l'atelier en tire

wyat-1-800m est un **premier filtre local et rapide** qui **passe la main à un humain** quand il hésite et se combine avec des **règles déterministes en code** : pas un détecteur autonome. Les cas de l'atelier inspirés de ces lignes ont été écrits de zéro (aucune donnée de benchmark copiée) et leurs résultats montrent à la fois l'approche naïve / modèle seul et l'approche cadrée ou hybride (`wyat` + code) :
- **Demande modifiée (cas 20)** : 10/10 dès la première formulation, y compris lorsqu'un second courriel annule le changement de RIB ;
- **Tri d'hameçonnage (cas 13)** : 11/12 (le faux partage SharePoint hors liste officielle passe à P = 0,08) ;
- **Énoncé de groupe (cas 26)** : 4/5 (l'erreur a une marge faible de 0,17 : à relire par le rapporteur) ;
- **Passage de relais / réorientation (cas 18)** : **7/12** avec une question oui / non négative floue (« relève d'un autre organisme que la mairie ? »), contre **12/12** en `Choice` fermé lorsque le périmètre de la mairie est décrit explicitement à côté des 5 organismes externes ;
- **Pertinence produit / surveillance d'annonces (cas 24)** : **3/8** quand on mélange le prix chiffré dans le contexte du modèle, contre **6/8** quand `wyat` juge la relation sur le texte seul et que le code contrôle le prix (`< 40 %` du prix boutique) et les mots-clés de contrefaçon (**3/3** contrefaçons signalées) ;
- **Priorité d'incident SOC/OT (cas 17)** : **4/10** niveaux exacts avec `Score` seul (tassé vers le milieu : 0/3 astreintes P1 au seuil 2,3), contre **7/10** niveaux exacts et **3/3** astreintes P1 en plaçant des règles déterministes SOC/OT en amont ;
- **Conditions d'accès privilégié (cas 19)** : **3/10** décomptes exacts avec `Score` seul sur texte libre, contre **10/10** en confiant la durée, la validation et l'identifiant de ticket à des contrôles de champs en code et la justification métier à `wyat`.

Un avantage mesuré sur un benchmark ne dispense jamais de cadrer les options, de séparer ce qui relève du code (chiffres, dates, listes) de ce qui relève du modèle (les mots), et de mesurer sur vos propres données : c'est la raison d'être des étapes 2 à 6.

ChessBench n'a pas d'exemple : 8,6 % pour un hasard à 8,2 %, ce n'est pas un usage.
