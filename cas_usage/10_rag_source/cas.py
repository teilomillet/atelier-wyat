# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 10 — Dans un assistant à base documentaire (RAG) : garder les bons passages, et vérifier que la réponse s'appuie sur la source."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

PERTINENT = "Ce passage contient-il l'information qui permet de répondre à la question ?"
APPUYEE = "Tout ce qu'affirme la réponse est-il dit dans le passage source ?"

ok_p = ok_a = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    p1 = modele.decide(wyat.Request.noul(PERTINENT, context={"question": ligne["question"], "passage": ligne["passage"]})).probability_true
    p2 = modele.decide(wyat.Request.noul(APPUYEE, context={"passage source": ligne["passage"], "réponse": ligne["reponse"]})).probability_true
    pert, app = ("oui" if p1 >= 0.5 else "non"), ("oui" if p2 >= 0.5 else "non")
    n += 1
    ok_p += pert == ligne["pertinent"]
    ok_a += app == ligne["appuyee"]
    action = "afficher la réponse" if pert == app == "oui" else "ne pas afficher : « je ne sais pas, voici le lien »"
    print(f"{ligne['id']} pertinent {p1:.2f} ({pert}, attendu {ligne['pertinent']}) · appuyée {p2:.2f} ({app}, attendu {ligne['appuyee']}) → {action}")
print(f"\npassage pertinent : {ok_p}/{n} justes ; réponse appuyée par la source : {ok_a}/{n} justes")
