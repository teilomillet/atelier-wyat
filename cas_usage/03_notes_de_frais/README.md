<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 03 — Contrôler les notes de frais

*Finance · secteur : Tous · type de tâche : **Choice + Noul + code** · ✅ à montrer (version wyat + code)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (15 lignes).*

**Problème.** Le contrôle de gestion relit chaque note de frais contre la politique.

**Décision.** wyat range la dépense (repas seul, repas client, train, hôtel, taxi, autre) et répond à des questions de **mots** (alcool ? 1re classe de jour ? taxi après 22 h ou avec bagages ? sans justificatif ?) ; **le code compare les montants aux plafonds**. Action : valider, ou renvoyer avec le motif.

## Lancer
```sh
.venv/bin/python cas_usage/03_notes_de_frais/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 3 — Contrôler une note de frais : wyat lit les conditions « en mots », le code compare les montants."""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")
oui = lambda question, texte: modele.decide(wyat.Request.noul(question, context=texte)).probability_true >= 0.5

TYPES = {"repas_seul": "Repas pris seul", "repas_client": "Repas avec un client", "train": "Billet de train",
         "hotel": "Nuit d'hôtel", "taxi": "Course de taxi", "autre": "Autre dépense (parking, fournitures…)"}
PLAFONDS = {"repas_seul": 25, "repas_client": 40, "hotel": 130}   # € (par personne ou par nuit) : du CODE, pas du modèle

def controle(texte: str) -> list[str]:
    genre = modele.decide(wyat.Request.choice("De quel type de dépense s'agit-il ?", TYPES, context=texte)).selected
    montant = float(m.group(1).replace(",", ".")) if (m := re.search(r"(\d+(?:,\d+)?) ?€", texte)) else 0.0
    nuits = int(m.group(1)) if (m := re.search(r"(\d+) nuits", texte)) else 1
    personnes = int(m.group(1)) if (m := re.search(r"(\d+) personnes", texte)) else 1
    unitaire = montant / (nuits if genre == "hotel" else personnes)
    motifs = [f"{unitaire:.0f} € > plafond {PLAFONDS[genre]} €"] if unitaire > PLAFONDS.get(genre, 1e9) else []
    if genre == "repas_seul" and oui("La dépense comprend-elle de l'alcool (vin, bière…) ?", texte): motifs.append("alcool sans client")
    if genre == "train" and oui("Le billet est-il en première classe pendant la journée ?", texte): motifs.append("1re classe de jour")
    if genre == "taxi" and not oui("La course a-t-elle lieu après 22 h, ou avec des bagages lourds ?", texte): motifs.append("taxi non justifié")
    if oui("Le texte indique-t-il qu'il n'y a pas de justificatif ?", texte): motifs.append("sans justificatif")
    return [genre] + motifs

scores = {"ecriture": [0, 0], "verification": [0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    genre, *motifs = controle(ligne["depense"])
    verdict = "non_conforme" if motifs else "conforme"
    scores[ligne["jeu"]][0] += verdict == ligne["attendu"]
    scores[ligne["jeu"]][1] += 1
    print(f"{ligne['depense'][:56]:<56} [{genre}] → {verdict:<12} {'; '.join(motifs):<26} {'✓' if verdict == ligne['attendu'] else '✗ attendu ' + ligne['attendu']}")
print("\n" + " ; ".join(f"{jeu} : {j}/{n} justes" for jeu, (j, n) in scores.items()))
```

## Sortie réelle (mlx)
```
Déjeuner seul à Lyon, 18,50 €, sans alcool               [repas_seul] → conforme                                ✓
Déjeuner seul à Lille, 34,00 €, aucun client présent     [repas_seul] → non_conforme 34 € > plafond 25 €; sans justificatif ✓
Dîner avec le client Arvel (2 personnes), 72 €, client n [repas_client] → conforme                                ✓
Billet Paris–Marseille en 1re classe, voyage de jour, 2  [train] → non_conforme 1re classe de jour         ✓
Billet Paris–Nantes en 2de classe, 64 €                  [train] → conforme                                ✓
Hôtel à Bordeaux, 1 nuit, 98 € petit-déjeuner compris    [hotel] → conforme                                ✓
Hôtel à Toulouse, 1 nuit, 189 €                          [hotel] → non_conforme 189 € > plafond 130 €      ✓
Taxi de 23 h 40 de la gare à l'hôtel, 21 €               [taxi] → conforme                                ✓
Taxi à 14 h entre deux rendez-vous dans Paris, 26 €, san [taxi] → non_conforme taxi non justifié          ✓
Déjeuner seul, 16 €, dont une bouteille de vin 9 €       [repas_seul] → non_conforme alcool sans client         ✓
Repas sans justificatif, 22 €                            [repas_seul] → non_conforme sans justificatif          ✓
Parking de l'aéroport, 3 jours, 45 €, justificatif joint [autre] → conforme                                ✓
Déjeuner seul à Nantes, 23,50 €, justificatif joint      [repas_seul] → conforme                                ✓
Hôtel à Paris, 2 nuits, 310 € au total                   [hotel] → non_conforme 155 € > plafond 130 €      ✓
Taxi à 15 h avec deux valises de matériel de démonstrati [taxi] → conforme                                ✓

ecriture : 12/12 justes ; verification : 3/3 justes

[mlx, 7 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `ecriture : 12/12 justes ; verification : 3/3 justes` (identique)

## Adapter chez vous
Vos plafonds dans `PLAFONDS` (du code) ; une question oui / non par règle « en mots » ; branchez-le sur l'export de votre outil de notes de frais (CSV).

## Ce qui se passe et pourquoi (résultats et pièges)
**Première version (une seule question « conforme à la politique ? » avec la politique entière en contexte) : 9/12**, et une version « quelle règle est enfreinte ? » : 7/12. Le modèle ne compare pas bien 189 € à 130 €. Leçon : les chiffres au code, les mots au modèle. Les 3 lignes « vérification » ont été écrites après la mise au point.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
