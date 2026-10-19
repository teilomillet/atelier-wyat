# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 4 — Relire un contrat : plusieurs petites questions fermées sur le même document, une fiche de relecture."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

CLAUSES = {   # question → options fermées ; l'id "oui" signale le point à faire relire par le juridique
    "reconduction_tacite": ("Que se passe-t-il à la fin de la durée du contrat ?",
                            {"oui": "Il se renouvelle ou se prolonge automatiquement si personne ne le dénonce",
                             "non": "Il prend fin, sans renouvellement automatique"}),
    "preavis_long": ("Quel préavis faut-il respecter pour mettre fin au contrat ?",
                     {"non": "Un préavis de 3 mois ou moins", "oui": "Un préavis de plus de 3 mois", "aucun": "Aucun préavis indiqué"}),
    "penalites": ("Que prévoit le contrat si le prestataire est en retard ?",
                  {"oui": "Une pénalité, une indemnité ou une réduction de prix", "non": "Rien, ou aucune pénalité n'est due"}),
    "hors_ue": ("Où les données sont-elles hébergées selon le contrat ?",
                {"non": "Dans l'Union européenne (France, Allemagne, Irlande…)", "oui": "Hors de l'Union européenne (États-Unis, Canada, Inde…)",
                 "aucun": "Le contrat ne le précise pas"}),
}

scores = {"ecriture": [0, 0], "verification": [0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    print(f"Contrat {ligne['id']} ({ligne['jeu']})")
    for cle, (question, options) in CLAUSES.items():
        d = modele.decide(wyat.Request.choice(question, options, context=ligne["contrat"]))
        bon = d.selected == ligne[cle]
        scores[ligne["jeu"]][0] += bon
        scores[ligne["jeu"]][1] += 1
        print(f"  {cle:<20} → {d.selected:<5} {options[d.selected][:60]:<60} marge {d.probability_margin:.2f} {'✓' if bon else '✗ attendu ' + ligne[cle]}")
print("\n" + " ; ".join(f"{jeu} : {j}/{n} cases justes" for jeu, (j, n) in scores.items()))
