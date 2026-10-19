# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 8 — Donner une priorité P1 à P4 aux alertes d'exploitation (Score : une échelle ordonnée)."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ECHELLE = [   # du moins grave au plus grave : wyat rend une probabilité par niveau et une valeur moyenne
    "P4 : aucune gêne pour les clients, demande de confort ou cosmétique, peut attendre des semaines",
    "P3 : gêne légère ou risque lointain, le service fonctionne, à traiter cette semaine",
    "P2 : dégradation importante ou panne prévisible très bientôt, à traiter aujourd'hui",
    "P1 : service essentiel en panne pour beaucoup de clients, intervention immédiate, astreinte réveillée",
]

justes = proches = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.score("Quelle est la priorité de cette alerte ?", ECHELLE, context=ligne["alerte"]))
    niveau = f"P{4 - int(d.selected)}"
    attendu = int(ligne["attendu"][1])
    n += 1
    justes += niveau == ligne["attendu"]
    proches += abs(int(niveau[1]) - attendu) <= 1
    signe = "✓" if niveau == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['alerte'][:66]:<66} → {niveau} (valeur {d.expected_ordinal_value:.2f} sur 0–3) {signe}")
print(f"\n{justes}/{n} priorités exactes, {proches}/{n} à un niveau près")
