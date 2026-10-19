# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 26 — Consultation ou comité : quel énoncé de synthèse représente le mieux l'ensemble des avis ? (Choice, aide au rapporteur)"""
import csv
import json
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    enonces = json.loads(l["enonces"])
    d = modele.decide(wyat.Request.choice(
        "Quel énoncé de synthèse représente le plus fidèlement l'ensemble des avis, y compris les avis minoritaires ?",
        enonces, context={"question": l["question"], "avis": l["avis"].split(" || ")}))
    n += 1
    justes += d.selected == l["attendu"]
    print(f"{l['question'][:50]:<50} → {d.selected} ({d.probabilities_by_id[d.selected]:.2f}, marge {d.probability_margin:.2f}) "
          f"{'✓' if d.selected == l['attendu'] else '✗ attendu ' + l['attendu']}")
print(f"\n{justes}/{n} ; le rapporteur relit toujours : c'est une suggestion d'ordre, pas une synthèse")
