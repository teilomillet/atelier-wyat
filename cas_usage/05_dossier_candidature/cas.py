# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 5 — Vérifier qu'une candidature est COMPLÈTE (pas de jugement sur la personne) et demander ce qui manque."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

PIECES = {   # pièce → (question oui / non, phrase de relance automatique)
    "poste": ("Le message indique-t-il pour quel poste ou quelle offre la personne candidate ?", "le poste visé"),
    "disponibilite": ("Le candidat dit-il quand il peut commencer (date, délai de préavis, ou immédiatement) ?", "votre date de disponibilité"),
    "cv": ("Le message dit-il qu'un CV est joint à ce message ?", "votre CV"),
}

scores = {"ecriture": [0, 0], "verification": [0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    manque = []
    for cle, (question, phrase) in PIECES.items():
        p = modele.decide(wyat.Request.noul(question, context=ligne["candidature"])).probability_true
        present = "oui" if p >= 0.5 else "non"
        scores[ligne["jeu"]][0] += present == ligne[cle]
        scores[ligne["jeu"]][1] += 1
        print(f"  {ligne['id']} {cle:<14} P(oui) {p:.2f} → {present} (attendu {ligne[cle]})")
        if present == "non":
            manque.append(phrase)
    action = "complet → dossier transmis au recruteur" if not manque else "relance : merci de préciser " + ", ".join(manque)
    print(f"{ligne['id']} : {action}")
print("\n" + " ; ".join(f"{jeu} : {j}/{n} pièces bien détectées" for jeu, (j, n) in scores.items()))
