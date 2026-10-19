# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 12 — Sécurité : garde-fou avant les commandes d'un agent de code, et alerte sur les SMS / e-mails suspects (voir bloc 6)."""
import csv
from pathlib import Path

import atelier as at   # le garde-fou complet (règles + wyat + vérifications) est dans atelier/securite.py

ICI = Path(__file__).parent
modele = at.charger_modele(verbeux=False)
reglage = at.ReglageGarde(seuil=0.4, verifs=("sortie", "secrets"))   # réglage choisi sur dev au bloc 6

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    if ligne["type"] == "commande":
        action, raison, _ = at.garde(modele, ligne["contexte"], ligne["texte"], reglage=reglage)
        bon = (action == "autoriser") == (ligne["attendu"] == "autoriser")   # « demander » ou « refuser » : arrêté
    else:
        canal, expediteur = ligne["contexte"].split(" ", 1)
        p = at.p_arnaque(modele, canal, expediteur, ligne["texte"])
        action, raison = ("SUSPECT" if p >= 0.4 else "ok"), f"P(frauduleux) {p:.2f}"
        bon = (action == "SUSPECT") == (ligne["attendu"] == "frauduleux")
    n += 1
    justes += bon
    print(f"{ligne['texte'][:56]:<56} → {action:<9} {raison[:44]:<44} {'✓' if bon else '✗ attendu ' + ligne['attendu']}")
print(f"\n{justes}/{n} décisions de sécurité justes")
