<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Jeu de données de l'atelier — 100 % SYNTHÉTIQUE

**Aucun message réel de client.** Les 155 messages ont été **écrits par une IA (Grok Bot) en octobre 2026** pour cet atelier, puis relus par une IA. Ils simulent le support client de **Lumio**, un opérateur fictif (box, mobile, TV, envoi de matériel). Les numéros, montants, références et IMEI sont inventés.

> ⚠️ Relecture humaine conseillée avant l'atelier : les étiquettes de référence sont celles de l'auteur, discutables par construction sur les cas ambigus. C'est voulu, et c'est l'objet du bloc 3.

## Comment ils ont été faits
1. Choix de 5 services : `facturation`, `technique`, `resiliation`, `livraison`, `autre`.
2. Rédaction manuelle (par l'IA) de messages variés : registre formel ou familier, fautes de frappe (« jarrive pa a me conecter »), messages très courts (« colis pas reçu », « lol »), plusieurs intentions, et des **pièges** où un mot trompeur (« factures », « paiements », « résilier ») n'est pas le vrai sujet.
3. Pour chaque message : une **étiquette de référence** (`label`), les **étiquettes défendables** (`labels_acceptables`, séparées par `|`), une **difficulté** (`facile` / `ambigu` / `multi` / `piege`) et une note.
4. Découpage déterministe (graine 2026) par `scripts/construire_dataset.py` :

| Fichier | n | Rôle |
|---|---:|---|
| `labeling_15.csv` | 15 | exercice d'annotation du bloc 3, **sans étiquettes** (3 par service, dont 7 difficiles) |
| `labeling_15_corrige.csv` | 15 | le corrigé (à ne montrer qu'après l'exercice) |
| `dev.csv` | 63 | jeu de travail : on regarde les erreurs, on réécrit les options |
| `test_scelle.csv` | 77 | **test scellé** : ouvert une seule fois, options figées (bloc 5) |
| `dev_rapide.csv` | 20 | **mode rapide** (PC sans GPU) : sous-ensemble stratifié de dev (étiquette puis difficulté) |
| `test_scelle_rapide.csv` | 25 | **mode rapide** : sous-ensemble stratifié du test scellé |
| `tous_les_messages.csv` | 155 | tout, pour référence |
| `annotations_atelier.csv` | 15 × 10 | gabarit vide à remplir pendant le bloc 3 |
| `annotations_exemple_SIMULEES.csv` | 15 × 10 | annotations **simulées au hasard** (`scripts/simuler_annotations.py`), pour montrer les calculs si le groupe n'a pas saisi les siennes |

Répartition — dev : facturation 15, technique 16, résiliation 9, livraison 12, autre 11 (difficiles : 15). Test : facturation 19, technique 19, résiliation 12, livraison 14, autre 13 (difficiles : 23).

## Honnêteté méthodologique
- Les sous-ensembles rapides sont tirés **une seule fois** par `scripts/construire_sous_ensembles.py` (graine 2026, plus forts restes), sans regarder les résultats du modèle. Le hasard a donné un test rapide plus difficile (64 % contre 74 % sur le test complet) : on l'a gardé tel quel. Les 3 messages « piège » (1 dans dev, 2 dans le test) n’y figurent pas : trop rares pour être tirés à cette taille.
- Les options de référence (`notebooks/atelier.py`) ont été **écrites et comparées sur dev uniquement**, puis **figées avant** la seule exécution sur le test scellé.
- Les messages synthétiques sont plus « propres » que les vrais : les performances réelles seront différentes, probablement plus basses.
- Pour de vraies données : anonymisation (noms, téléphones, adresses, IBAN, numéros de contrat), base légale RGPD, minimisation, durée de conservation, et un test scellé gardé par quelqu'un qui n'écrit pas les options.
- Jeux publics possibles pour s'entraîner : BANKING77 (anglais, 77 intentions bancaires), MASSIVE (Amazon, 51 langues dont le français), CLINC150. Vérifiez les licences.
