# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 19 — Accès privilégié (IAM) : Score seul sur texte libre (3/10) vs wyat (justification métier) + contrôles de champs (10/10)."""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ECHELLE = [
    "aucune des trois conditions n'est remplie",
    "une seule des trois conditions est remplie",
    "deux des trois conditions sont remplies",
    "les trois conditions sont remplies : justification métier précise, durée limitée, validation du responsable",
]
Q_JUSTIF = "La demande donne-t-elle une raison métier précise (incident, ticket, projet nommé) ?"
RE_JUSTIF = re.compile(r"\b(INC-\d+|T-\d+|AUD-[\d-]+|projet \w+|migration [\w-]+|chantier de)\b", re.I)
RE_DUREE = re.compile(r"\b(du \d+ au \d+|jusqu'au \d+|\d+\s*h|une semaine|temporaire)\b", re.I)
RE_VALID = re.compile(r"\b(validé par|accord écrit de|responsable est d'accord)\b", re.I)

ex_seul = ex_hyb = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    txt = l["demande"]
    d = modele.decide(wyat.Request.score("Combien de conditions d'accès cette demande remplit-elle ?", ECHELLE, context=txt))
    p_justif = modele.decide(wyat.Request.noul(Q_JUSTIF, context=txt)).probability_true
    c_justif = (p_justif >= 0.5) or bool(RE_JUSTIF.search(txt))
    c_duree = bool(RE_DUREE.search(txt)) and "permanent" not in txt.lower()
    c_valid = bool(RE_VALID.search(txt))
    nb_hyb = int(c_justif) + int(c_duree) + int(c_valid)
    manque = [nom for nom, ok in [("justification", c_justif), ("duree", c_duree), ("validation", c_valid)] if not ok]
    action = "file d'approbation" if nb_hyb == 3 else "renvoyer : manque " + ", ".join(manque)
    n += 1
    ex_seul += int(d.selected) == int(l["attendu"])
    ex_hyb += nb_hyb == int(l["attendu"])
    print(f"{txt[:52]:<52} → Score seul {d.selected}/3 | wyat+champs {nb_hyb}/3 (att {l['attendu']}) {action}")
print(f"\nScore seul sur texte libre : {ex_seul}/{n} décomptes exacts ; wyat + contrôles de champs : {ex_hyb}/{n} exacts")
