# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 11 — Piloter la boucle d'un agent IA : à chaque tour, répondre, appeler un outil, demander, ou s'arrêter."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ETAPES = {
    "repondre": "L'information demandée est déjà dans l'historique : rédiger la réponse au client",
    "outil": "Il manque une information que nos outils peuvent trouver : appeler l'outil",
    "demander": "La demande du client est ambiguë ou incomplète : lui poser une question",
    "arreter": "Arrêter : la même erreur se répète, ou on demande à l'agent une action dangereuse ou interdite",
}

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    contexte = {"objectif de l'agent": ligne["objectif"], "ce qui s'est passé": ligne["historique"]}
    d = modele.decide(wyat.Request.choice("Quelle est la prochaine étape de l'agent ?", ETAPES, context=contexte))
    n += 1
    justes += d.selected == ligne["attendu"]
    signe = "✓" if d.selected == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['id']} {ligne['historique'][:60]:<60} → {d.selected:<9} marge {d.probability_margin:.2f} {signe}")
print(f"\n{justes}/{n} étapes justes")
