# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 7 — Modérer les avis clients avant publication : publier, masquer, ou faire vérifier par une personne."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {   # plusieurs options précises valent mieux qu'une option « masquer » fourre-tout
    "publier": "Avis sur le produit ou le service, positif ou négatif, même sévère, sans insulte ni menace",
    "insulte": "Insulte ou menace contre une personne",
    "pub": "Publicité, lien vers un autre site ou spam",
    "coordonnees": "L'avis contient une adresse postale, un numéro de téléphone ou un e-mail",
    "verifier": "Accusation grave (escroquerie, insulte reçue, fraude) contre l'entreprise ou un salarié, à vérifier avant publication",
}
ACTION = {"publier": "publier", "insulte": "masquer", "pub": "masquer", "coordonnees": "masquer", "verifier": "verifier"}

scores = {"ecriture": [0, 0], "verification": [0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.choice("Que faire de cet avis client avant publication ?", OPTIONS, context=ligne["avis"]))
    action = ACTION[d.selected] if d.probability_margin >= 0.3 else "verifier"   # en cas de doute : une personne
    scores[ligne["jeu"]][0] += action == ligne["attendu"]
    scores[ligne["jeu"]][1] += 1
    signe = "✓" if action == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['avis'][:62]:<62} → {action:<9} (choix {d.selected}, marge {d.probability_margin:.2f}) {signe}")
print("\n" + " ; ".join(f"{jeu} : {j}/{n} avis bien traités" for jeu, (j, n) in scores.items()))
