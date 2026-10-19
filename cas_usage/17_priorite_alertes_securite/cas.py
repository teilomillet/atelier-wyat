# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 17 — Prioriser les alertes SOC (IT et OT) : Score wyat seul (tassé vers le milieu) vs règles SOC/OT + Score wyat."""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ECHELLE = [   # du moins grave au plus grave
    "P4 : bruit ou événement attendu, aucune action de sécurité nécessaire",
    "P3 : anomalie isolée sans signe de compromission, à examiner dans la semaine",
    "P2 : comportement suspect sur un poste ou un compte, à analyser aujourd'hui",
    "P1 : compromission probable ou en cours, ou risque pour un système industriel ou critique, astreinte immédiate",
]
EXERCICE_CONNU = re.compile(r"EICAR.*exercice planifié", re.I)
CRITIQUE_SOC_OT = re.compile(r"chiffrement massif|\.locked|automate|station de pompage|échecs de connexion puis une connexion réussie", re.I)

ecarts, ex_seul, ex_hyb, p1_seul, p1_hyb, nb_p1, n = 0.0, 0, 0, 0, 0, 0, 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    d = modele.decide(wyat.Request.score("Quelle est la priorité de cette alerte de sécurité ?", ECHELLE, context=l["alerte"]))
    valeur = d.expected_ordinal_value                         # 0 = P4 … 3 = P1 ; valeur moyenne pondérée
    attendu = 4 - int(l["attendu"][1])
    niv_seul = f"P{4 - int(d.selected)}"
    act_seul = "astreinte" if valeur >= 2.3 else ("analyste aujourd'hui" if valeur >= 1.5 else "file normale")
    if EXERCICE_CONNU.search(l["alerte"]):
        niv_hyb, act_hyb = "P4", "file normale (exercice)"
    elif CRITIQUE_SOC_OT.search(l["alerte"]):
        niv_hyb, act_hyb = "P1", "astreinte (règle SOC/OT)"
    else:
        niv_hyb, act_hyb = niv_seul, act_seul
    n += 1
    ex_seul += niv_seul == l["attendu"]
    ex_hyb += niv_hyb == l["attendu"]
    ecarts += abs(valeur - attendu) / 3
    if l["attendu"] == "P1":
        nb_p1 += 1
        p1_seul += act_seul == "astreinte"
        p1_hyb += act_hyb.startswith("astreinte")
    print(f"{l['alerte'][:54]:<54} → seul {niv_seul} ({valeur:.2f}) | wyat+règles {niv_hyb} {act_hyb:<24} attendu {l['attendu']}")
print(f"\nModèle seul : {ex_seul}/{n} exacts (MAE {ecarts / n:.3f}, astreintes P1 {p1_seul}/{nb_p1}) ; wyat + règles SOC/OT : {ex_hyb}/{n} exacts (astreintes P1 {p1_hyb}/{nb_p1})")
