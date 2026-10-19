# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""La même décision avec le paquet atelier : moteur choisi tout seul, cache, mode secours.

Lancer : .venv/bin/python exemples/02_une_decision_atelier.py
         WYAT_PRECALCULE=1 .venv/bin/python exemples/02_une_decision_atelier.py   (sans modèle)
"""
import atelier as at

modele = at.charger_modele()
for message in ["on m'a prélevé deux fois ce mois-ci", "la box clignote rouge depuis hier soir", "bonjour"]:
    d = at.decider(modele, message)          # options de référence : at.OPTIONS
    print(f"{message:<45} → {d.selected:<12} marge {d.probability_margin:.2f}")
