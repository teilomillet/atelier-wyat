# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Une décision avec wyat tout seul (sans le paquet atelier) : ce qu'il y a dessous.

Lancer : .venv/bin/python exemples/01_une_decision_wyat.py
"""
import os
import platform

import wyat

backend = "mlx" if (platform.system(), platform.machine()) == ("Darwin", "arm64") else "torch"
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend=backend)   # téléchargé une fois (≈ 1,8 Go)

requete = wyat.Request.choice(
    "Quel service doit traiter ce message client ?",
    {
        "facturation": "Facturation et paiements : débits ou prélèvements bancaires, remboursement",
        "technique": "Problème technique : internet, box, mobile ou application en panne",
        "autre": "Autre demande précise",
    },
    context="Bonjour, on m'a prélevé deux fois 29,99 € ce mois-ci, vous pouvez me rembourser ?",
)
decision = modele.decide(requete)
print("choix :", decision.selected)
print("marge :", round(decision.probability_margin, 3))
print("probabilités :", {k: round(v, 3) for k, v in decision.probabilities_by_id.items()})
