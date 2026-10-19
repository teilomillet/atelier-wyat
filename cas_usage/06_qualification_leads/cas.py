# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 6 — Qualifier les demandes entrantes du formulaire « professionnels » : qui rappeler vite ?"""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {
    "appeler": "Une entreprise qui veut acheter nos offres : besoin précis, taille ou délai donnés, ou demande de rappel",
    "informer": "Une personne ou une entreprise intéressée par nos offres, sans projet daté : lui envoyer de la documentation",
    "ecarter": "Pas un futur client : étudiant, curieux sans projet, ou quelqu'un qui veut NOUS vendre un service (démarchage, SEO, publicité)",
}
ACTIONS = {"appeler": "→ commercial, rappel sous 24 h", "informer": "→ e-mail de présentation + relance à 1 mois", "ecarter": "→ archivé"}

scores = {"ecriture": [0, 0], "verification": [0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.choice("Quelle suite donner à cette demande de contact ?", OPTIONS, context=ligne["demande"]))
    scores[ligne["jeu"]][0] += d.selected == ligne["attendu"]
    scores[ligne["jeu"]][1] += 1
    signe = "✓" if d.selected == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['demande'][:58]:<58} {d.selected:<8} {ACTIONS[d.selected]:<38} marge {d.probability_margin:.2f} {signe}")
print("\n" + " ; ".join(f"{jeu} : {j}/{n} demandes bien qualifiées" for jeu, (j, n) in scores.items()))
