# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 9 — Avant d'envoyer un mail à l'extérieur : contient-il des données personnelles ? (wyat + règles écrites)"""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

QUESTION = ("Ce mail contient-il des données personnelles sur une personne identifiable "
            "(coordonnées, numéro bancaire, santé, numéro de sécurité sociale, sanction) ?")
SENSIBLE = "Ce mail parle-t-il de la santé, d'une absence pour maladie, d'une sanction ou d'un licenciement d'une personne identifiable ?"
MOTIFS = {   # ce que le code sait trouver mieux qu'un modèle : des formats
    "IBAN": r"\bFR\d{2}(?: ?\d{4}){5}", "carte": r"\b(?:\d{4} ?){4}\b", "téléphone": r"\b0[1-9](?: ?\d{2}){4}\b", "e-mail": r"[\w.-]+@[\w-]+\.\w+",
    "sécu": r"\b[12] ?\d{2} ?\d{2} ?\d{2} ?\d{3} ?\d{3} ?\d{2}\b",
}

scores = {"ecriture": [0, 0, 0], "verification": [0, 0, 0]}   # wyat seul, wyat + règles, total
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    p = max(modele.decide(wyat.Request.noul(q, context=ligne["mail"])).probability_true for q in (QUESTION, SENSIBLE))
    formats = [nom for nom, motif in MOTIFS.items() if re.search(motif, ligne["mail"])]
    wyat_seul = "oui" if p >= 0.5 else "non"
    les_deux = "oui" if formats or p >= 0.5 else "non"
    s = scores[ligne["jeu"]]
    s[0] += wyat_seul == ligne["attendu"]
    s[1] += les_deux == ligne["attendu"]
    s[2] += 1
    print(f"{ligne['mail'][:58]:<58} P(oui) {p:.2f}  règles {formats or '-'}  → {'BLOQUER, à relire' if les_deux == 'oui' else 'envoyer'} (attendu {ligne['attendu']})")
print("\n" + " ; ".join(f"{jeu} : wyat seul {a}/{n}, wyat + règles {b}/{n}" for jeu, (a, b, n) in scores.items()))
