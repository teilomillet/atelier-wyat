# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 20 — Fil d'échanges avec un fournisseur : quelle est la demande ACTUELLE ? (Choice ; tout changement de RIB → contre-appel)"""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {
    "paiement_habituel": "Payer la facture sur les coordonnées bancaires habituelles, déjà connues",
    "changement_rib": "Payer sur de nouvelles coordonnées bancaires (nouvel IBAN, nouvelle banque)",
    "report_annulation": "Reporter, suspendre ou annuler le paiement",
    "autre": "Autre demande sans rapport avec le paiement (livraison, devis, contact)",
}

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    fil = [m.strip() for m in l["fil"].split("||")]          # messages du plus ancien au plus récent
    contexte = "\n".join(f"Message {i + 1} : {m}" for i, m in enumerate(fil))
    d = modele.decide(wyat.Request.choice("D'après le dernier état de l'échange, que demande le fournisseur ?", OPTIONS, context=contexte))
    if d.selected == "changement_rib" or d.probability_margin < 0.4:
        action = "CONTRE-APPEL au numéro connu avant tout paiement"   # procédure anti-fraude, jamais automatisée
    else:
        action = "traitement normal"
    n += 1
    justes += d.selected == l["attendu"]
    print(f"{fil[-1][:56]:<56} → {d.selected:<18} marge {d.probability_margin:.2f} {action} {'✓' if d.selected == l['attendu'] else '✗ attendu ' + l['attendu']}")
print(f"\n{justes}/{n} demandes actuelles identifiées")
