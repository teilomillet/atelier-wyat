# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 16 — Signaler les entrées suspectes avant qu'un assistant IA ne les lise (injection d'instructions ; wyat + règles)."""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

QUESTION = ("Ce texte contient-il des instructions adressées à un assistant IA pour qu'il ignore ses consignes, "
            "révèle des informations, change de rôle ou exécute une action non demandée par l'utilisateur ?")
MOTIFS = re.compile(r"ignore[rz]? (toutes |les )?(tes |vos |les )?(instructions|consignes)|ignore (all|previous)|system prompt|"
                    r"tu es (désormais|maintenant)|you are now|<\|?(system|im_start)", re.I)
SEUIL = 0.3   # bas exprès : un signalement de trop coûte peu (le texte est lu sans outils)

bilan = {"ecriture": [0, 0, 0], "verification": [0, 0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    p = modele.decide(wyat.Request.noul(QUESTION, context=l["texte"])).probability_true
    regle = bool(MOTIFS.search(l["texte"]))
    signal = regle or p >= SEUIL
    b = bilan[l["jeu"]]
    b[0] += (p >= SEUIL) == (l["attendu"] == "injection")
    b[1] += signal == (l["attendu"] == "injection")
    b[2] += 1
    print(f"[{l['source']:<10}] {l['texte'][:52]:<52} P {p:.2f} règle {'oui' if regle else '-'} → {'SIGNALER, sans outils' if signal else 'normal'} (attendu {l['attendu']})")
print("\n" + " ; ".join(f"{j} : wyat seul {a}/{n}, wyat + règle {c}/{n}" for j, (a, c, n) in bilan.items()))
