<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 26 — Consultation ou comité : quel énoncé de synthèse est le plus fidèle ?

*Concertation / direction · secteur : Secteur public, direction · type de tâche : **Choice** · ⚠️ aide au rapporteur*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (5 lignes).*

**Problème.** Après une consultation, le rapporteur hésite entre plusieurs formulations de synthèse ; certaines oublient les avis minoritaires.

**Décision.** Choice entre 3 énoncés candidats, avec les avis en contexte. Action : proposer un ordre au rapporteur, qui relit et choisit.

## Lancer
```sh
.venv/bin/python cas_usage/26_synthese_consultation/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 26 — Consultation ou comité : quel énoncé de synthèse représente le mieux l'ensemble des avis ? (Choice, aide au rapporteur)"""
import csv
import json
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    enonces = json.loads(l["enonces"])
    d = modele.decide(wyat.Request.choice(
        "Quel énoncé de synthèse représente le plus fidèlement l'ensemble des avis, y compris les avis minoritaires ?",
        enonces, context={"question": l["question"], "avis": l["avis"].split(" || ")}))
    n += 1
    justes += d.selected == l["attendu"]
    print(f"{l['question'][:50]:<50} → {d.selected} ({d.probabilities_by_id[d.selected]:.2f}, marge {d.probability_margin:.2f}) "
          f"{'✓' if d.selected == l['attendu'] else '✗ attendu ' + l['attendu']}")
print(f"\n{justes}/{n} ; le rapporteur relit toujours : c'est une suggestion d'ordre, pas une synthèse")
```

## Sortie réelle (mlx)
```
Faut-il passer à trois jours de télétravail par se → b (0.77, marge 0.57) ✓
Faut-il fermer la rue de l'école à la circulation  → c (0.56, marge 0.17) ✗ attendu a
Faut-il remplacer les réunions hebdomadaires par u → c (0.96, marge 0.93) ✓
Faut-il imposer l'authentification à deux facteurs → b (0.99, marge 0.98) ✓
Faut-il ouvrir la médiathèque le dimanche ?        → a (0.93, marge 0.88) ✓

4/5 ; le rapporteur relit toujours : c'est une suggestion d'ordre, pas une synthèse

[mlx, 3 s chargement compris]
```

## Adapter chez vous
Vos énoncés rédigés par des humains (le modèle ne rédige pas) ; jamais pour trancher un vote.

## Ce qui se passe et pourquoi (résultats et pièges)
Première version, non retouchée : **4/5**. L'erreur choisit « fermer la rue toute la journée » (marge 0,17) contre la synthèse fidèle : une marge faible doit être lue comme « à relire ». Contexte : sur Habermas Machine (choisir l'énoncé de groupe préféré), wyat-1-800m fait 42,18 % pour une chance de 31,1 % (D3-Lite 37,95 %) : mieux que le hasard, loin d'être fiable.

Repère de benchmark associé : Habermas Machine (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
