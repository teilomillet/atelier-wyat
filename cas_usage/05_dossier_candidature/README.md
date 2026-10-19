<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 05 — Vérifier qu'une candidature est complète (pas de tri des personnes)

*RH · secteur : Tous · type de tâche : **Noul (3 questions)** · ✅ à montrer*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (9 lignes).*

**Problème.** Les candidatures arrivent incomplètes ; on relance à la main pour le poste visé, la disponibilité ou le CV.

**Décision.** Trois questions oui / non (poste ? disponibilité ? CV joint ?). Action : dossier complet → recruteur ; sinon **relance automatique polie** de ce qui manque. **Aucune note, aucun classement des candidats.**

## Lancer
```sh
.venv/bin/python cas_usage/05_dossier_candidature/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 5 — Vérifier qu'une candidature est COMPLÈTE (pas de jugement sur la personne) et demander ce qui manque."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

PIECES = {   # pièce → (question oui / non, phrase de relance automatique)
    "poste": ("Le message indique-t-il pour quel poste ou quelle offre la personne candidate ?", "le poste visé"),
    "disponibilite": ("Le candidat dit-il quand il peut commencer (date, délai de préavis, ou immédiatement) ?", "votre date de disponibilité"),
    "cv": ("Le message dit-il qu'un CV est joint à ce message ?", "votre CV"),
}

scores = {"ecriture": [0, 0], "verification": [0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    manque = []
    for cle, (question, phrase) in PIECES.items():
        p = modele.decide(wyat.Request.noul(question, context=ligne["candidature"])).probability_true
        present = "oui" if p >= 0.5 else "non"
        scores[ligne["jeu"]][0] += present == ligne[cle]
        scores[ligne["jeu"]][1] += 1
        print(f"  {ligne['id']} {cle:<14} P(oui) {p:.2f} → {present} (attendu {ligne[cle]})")
        if present == "non":
            manque.append(phrase)
    action = "complet → dossier transmis au recruteur" if not manque else "relance : merci de préciser " + ", ".join(manque)
    print(f"{ligne['id']} : {action}")
print("\n" + " ; ".join(f"{jeu} : {j}/{n} pièces bien détectées" for jeu, (j, n) in scores.items()))
```

## Sortie réelle (mlx)
```
  c1 poste          P(oui) 0.96 → oui (attendu oui)
  c1 disponibilite  P(oui) 0.95 → oui (attendu oui)
  c1 cv             P(oui) 0.96 → oui (attendu oui)
c1 : complet → dossier transmis au recruteur
  c2 poste          P(oui) 0.03 → non (attendu non)
  c2 disponibilite  P(oui) 0.27 → non (attendu non)
  c2 cv             P(oui) 0.97 → oui (attendu oui)
c2 : relance : merci de préciser le poste visé, votre date de disponibilité
  c3 poste          P(oui) 0.74 → oui (attendu oui)
  c3 disponibilite  P(oui) 0.96 → oui (attendu oui)
  c3 cv             P(oui) 0.02 → non (attendu non)
c3 : relance : merci de préciser votre CV
  c4 poste          P(oui) 0.30 → non (attendu oui)
  c4 disponibilite  P(oui) 0.67 → oui (attendu oui)
  c4 cv             P(oui) 0.96 → oui (attendu oui)
c4 : relance : merci de préciser le poste visé
  c5 poste          P(oui) 0.16 → non (attendu non)
  c5 disponibilite  P(oui) 0.81 → oui (attendu oui)
  c5 cv             P(oui) 0.04 → non (attendu non)
c5 : relance : merci de préciser le poste visé, votre CV
  c6 poste          P(oui) 0.96 → oui (attendu oui)
  c6 disponibilite  P(oui) 0.29 → non (attendu non)
  c6 cv             P(oui) 0.92 → oui (attendu oui)
c6 : relance : merci de préciser votre date de disponibilité
  c7 poste          P(oui) 0.93 → oui (attendu oui)
  c7 disponibilite  P(oui) 0.94 → oui (attendu oui)
  c7 cv             P(oui) 0.94 → oui (attendu oui)
c7 : complet → dossier transmis au recruteur
  c8 poste          P(oui) 0.06 → non (attendu non)
  c8 disponibilite  P(oui) 0.79 → oui (attendu oui)
  c8 cv             P(oui) 0.03 → non (attendu non)
c8 : relance : merci de préciser le poste visé, votre CV
  c9 poste          P(oui) 0.78 → oui (attendu oui)
  c9 disponibilite  P(oui) 0.34 → non (attendu non)
  c9 cv             P(oui) 0.96 → oui (attendu oui)
c9 : relance : merci de préciser votre date de disponibilité

ecriture : 17/18 pièces bien détectées ; verification : 9/9 pièces bien détectées

[mlx, 5 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `ecriture : 17/18 pièces bien détectées ; verification : 9/9 pièces bien détectées` (identique)

## Adapter chez vous
Vos pièces obligatoires ; vérifiez la présence réelle de la pièce jointe par le code (type de fichier) et gardez wyat pour le texte.

## Ce qui se passe et pourquoi (résultats et pièges)
Trier ou noter des candidats avec un modèle est un usage à haut risque (AI Act, discrimination) : ne le faites pas ici. « Disponible » : la première formulation ratait « je peux commencer immédiatement » et « préavis de 2 mois ». Le métier sans le mot « poste » (« développeuse back-end ») est parfois raté : la relance coûte peu.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
