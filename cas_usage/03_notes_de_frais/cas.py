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
