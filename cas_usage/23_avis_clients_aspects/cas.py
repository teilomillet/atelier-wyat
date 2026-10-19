# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 23 — Avis clients (FR / EN) : étiqueter chaque aspect cité et sa tonalité (un Choice par aspect), pour le service client."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ASPECTS = {
    "produit": "la qualité du produit (matière, finition, solidité)",
    "boutique": "l'accueil et le conseil en boutique",
    "livraison": "la livraison ou l'emballage",
    "apres_vente": "le service après-vente, la réparation ou l'entretien",
}
TONALITE = {"positif": "L'avis en parle positivement", "negatif": "L'avis en parle négativement", "absent": "L'avis n'en parle pas"}

def etiquettes(avis: str) -> set[str]:
    sortie = set()
    for aspect, libelle in ASPECTS.items():
        d = modele.decide(wyat.Request.choice(f"Que dit cet avis sur {libelle} ?", TONALITE, context=avis))
        if d.selected != "absent":
            sortie.add(f"{aspect}:{d.selected}")
    return sortie

total_f1 = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    predit, attendu = etiquettes(l["avis"]), set(filter(None, l["attendu"].split(";")))
    vp = len(predit & attendu)
    f1 = 1.0 if not predit and not attendu else (2 * vp / (len(predit) + len(attendu)))
    total_f1 += f1
    n += 1
    print(f"{l['avis'][:54]:<54} → {', '.join(sorted(predit)) or '-'}  (F1 {f1:.2f} ; attendu {', '.join(sorted(attendu))})")
print(f"\nF1 moyen par avis : {100 * total_f1 / n:.1f} sur 100")
