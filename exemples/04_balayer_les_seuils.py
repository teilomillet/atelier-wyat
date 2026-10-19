# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Politique à seuil : pour chaque marge minimale, combien on automatise et combien d'erreurs.

Lancer : .venv/bin/python exemples/04_balayer_les_seuils.py
"""
import atelier as at

modele = at.charger_modele()
rapport, _ = at.evaluer(modele, at.lire("dev"))
for seuil in (0.0, 0.2, 0.5, 0.7, 0.9):
    s = rapport.selective(min_margin=seuil)            # API wyat : automatiser si marge ≥ seuil
    erreurs = s.automated - s.correct
    print(f"seuil {seuil:.1f} : {s.automation_rate:5.1%} automatisé, {erreurs} erreurs, "
          f"{s.total - s.automated} messages pour un humain")

print(at.router(modele, "SVP rappelez-moi, c'est urgent", seuil=0.5))   # la politique, en une ligne
