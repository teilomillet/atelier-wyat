# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 22 — Industrie / énergie : router les demandes de maintenance par métier (Choice) et repérer tout risque HSE (Noul, seuil bas)."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

METIERS = {
    "mecanique": "Mécanique : pompe, vanne, roulement, vibration, fuite sur une tuyauterie, courroie",
    "electrique": "Électricité : armoire électrique, disjoncteur, moteur électrique, câblage, éclairage",
    "instrumentation": "Instrumentation : capteur, transmetteur, mesure de pression, de débit ou de température, étalonnage",
    "automatisme": "Automatisme et informatique industrielle : automate, supervision, écran opérateur, réseau industriel",
}
HSE = ("Ce signalement décrit-il un risque pour la sécurité des personnes ou pour l'environnement "
       "(fuite de produit, odeur de gaz, risque de chute, brûlure, électrocution, déversement) ?")
SEUIL_HSE = 0.3   # bas exprès : un appel de trop au responsable HSE coûte peu

metier_ok = hse_ok = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    d = modele.decide(wyat.Request.choice("Quel métier doit intervenir ?", METIERS, context=l["demande"]))
    p = modele.decide(wyat.Request.noul(HSE, context=l["demande"])).probability_true
    alerte = p >= SEUIL_HSE
    n += 1
    metier_ok += d.selected == l["metier"]
    hse_ok += alerte == (l["hse"] == "oui")
    print(f"{l['demande'][:56]:<56} → {d.selected:<15} (marge {d.probability_margin:.2f}) HSE {p:.2f}{' ⚠ RESPONSABLE HSE' if alerte else ''}"
          f"  attendu {l['metier']}/{l['hse']}")
print(f"\nmétier {metier_ok}/{n} ; signal HSE {hse_ok}/{n}")
