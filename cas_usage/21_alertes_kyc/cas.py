# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 21 — Banque : pré-tri des alertes KYC / LCB-FT pour les analystes (Choice, rien n'est clôturé sans humain, journal d'audit)."""
import csv
import datetime
import json
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {
    "homonymie": "Probable faux positif : homonymie avec une personne d'une liste, date de naissance ou nationalité différente",
    "piece_manquante": "Pièce manquante ou expirée : justificatif d'identité, de domicile ou de revenus à demander au client",
    "mise_a_jour": "Changement de situation du client à mettre à jour : adresse, employeur, revenus, statut",
    "analyse_lcbft": "Opérations inhabituelles à analyser : montants ou flux incohérents avec le profil, fractionnement, pays à risque, tiers inconnus",
}
FILE = {"homonymie": "clôture proposée (validation analyste en lot)", "piece_manquante": "relance client",
        "mise_a_jour": "mise à jour du dossier", "analyse_lcbft": "ANALYSTE LCB-FT (prioritaire)"}

justes = n = 0
with open(ICI / "journal_kyc.jsonl", "w", encoding="utf-8") as journal:
    with open(ICI / "donnees.csv", encoding="utf-8") as _f:
        _lignes = list(csv.DictReader(_f))
    for l in _lignes:
        d = modele.decide(wyat.Request.choice("Quelle suite donner à cette alerte ?", OPTIONS, context=l["alerte"]))
        suite = FILE[d.selected] if d.probability_margin >= 0.5 else "analyste (marge faible)"
        journal.write(json.dumps({"horodatage": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "alerte": l["id"],
                                  "modele": d.model_id[:16], "probabilites": {k: round(v, 4) for k, v in d.probabilities_by_id.items()},
                                  "choix": d.selected, "marge": round(d.probability_margin, 4), "suite": suite}, ensure_ascii=False) + "\n")
        n += 1
        justes += d.selected == l["attendu"]
        print(f"{l['alerte'][:58]:<58} → {d.selected:<15} marge {d.probability_margin:.2f} {suite[:30]:<30} {'✓' if d.selected == l['attendu'] else '✗ attendu ' + l['attendu']}")
print(f"\n{justes}/{n} alertes bien pré-triées ; journal (probabilité par option) : cas_usage/21_alertes_kyc/journal_kyc.jsonl")
