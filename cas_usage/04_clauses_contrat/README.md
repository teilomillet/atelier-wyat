<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 04 — Relire les clauses d'un contrat fournisseur

*Juridique / achats · secteur : Tous · type de tâche : **Choice (plusieurs questions sur un document)** · ✅ à montrer*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (5 lignes).*

**Problème.** Avant signature, on cherche toujours les mêmes clauses : reconduction tacite, préavis, pénalités, hébergement des données.

**Décision.** Quatre questions fermées sur le même contrat → une fiche de relecture. Action : surligner les points « oui » pour le juriste ; il décide.

## Lancer
```sh
.venv/bin/python cas_usage/04_clauses_contrat/cas.py
```

## Le code (`cas.py`)
```python
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
```

## Sortie réelle (mlx)
```
Contrat k1 (ecriture)
  reconduction_tacite  → oui   Il se renouvelle ou se prolonge automatiquement si personne  marge 0.83 ✓
  preavis_long         → oui   Un préavis de plus de 3 mois                                 marge 0.81 ✓
  penalites            → non   Rien, ou aucune pénalité n'est due                           marge 0.98 ✓
  hors_ue              → non   Dans l'Union européenne (France, Allemagne, Irlande…)        marge 0.04 ✓
Contrat k2 (ecriture)
  reconduction_tacite  → non   Il prend fin, sans renouvellement automatique                marge 0.91 ✓
  preavis_long         → non   Un préavis de 3 mois ou moins                                marge 0.79 ✓
  penalites            → oui   Une pénalité, une indemnité ou une réduction de prix         marge 0.95 ✓
  hors_ue              → oui   Hors de l'Union européenne (États-Unis, Canada, Inde…)       marge 0.91 ✓
Contrat k3 (ecriture)
  reconduction_tacite  → oui   Il se renouvelle ou se prolonge automatiquement si personne  marge 0.93 ✓
  preavis_long         → non   Un préavis de 3 mois ou moins                                marge 0.65 ✓
  penalites            → oui   Une pénalité, une indemnité ou une réduction de prix         marge 0.93 ✓
  hors_ue              → non   Dans l'Union européenne (France, Allemagne, Irlande…)        marge 0.29 ✓
Contrat k4 (verification)
  reconduction_tacite  → oui   Il se renouvelle ou se prolonge automatiquement si personne  marge 0.63 ✓
  preavis_long         → oui   Un préavis de plus de 3 mois                                 marge 0.26 ✓
  penalites            → non   Rien, ou aucune pénalité n'est due                           marge 0.98 ✓
  hors_ue              → oui   Hors de l'Union européenne (États-Unis, Canada, Inde…)       marge 0.38 ✓
Contrat k5 (verification)
  reconduction_tacite  → non   Il prend fin, sans renouvellement automatique                marge 0.78 ✓
  preavis_long         → non   Un préavis de 3 mois ou moins                                marge 0.11 ✓
  penalites            → oui   Une pénalité, une indemnité ou une réduction de prix         marge 0.93 ✓
  hors_ue              → aucun Le contrat ne le précise pas                                 marge 0.38 ✗ attendu non

ecriture : 12/12 cases justes ; verification : 7/8 cases justes

[mlx, 5 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `ecriture : 12/12 cases justes ; verification : 7/8 cases justes` (identique)

## Adapter chez vous
Vos clauses sensibles (une question chacune, avec des options qui décrivent les issues possibles) ; découpez les longs contrats par article (limite d'environ 2 000 jetons par requête).

## Ce qui se passe et pourquoi (résultats et pièges)
**Première version en oui / non : 9/12** : « le contrat prend fin, sans renouvellement » lu comme une reconduction (0,97), « hébergé à Roubaix » lu comme hors UE (0,94). Des options fermées qui décrivent les issues font mieux. Sur 2 contrats écrits ensuite : 7/8 (« données stockées au Canada » → « non précisé », marge 0,38 : à relire). Le juriste garde la décision : c'est un surligneur, pas un avis.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
