<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 10 — Assistant documentaire : passage pertinent ? réponse appuyée par la source ?

*Base de connaissances / support · secteur : Tech · type de tâche : **Noul (2 questions)** · ⚠️ limite*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (8 lignes).*

**Problème.** Un assistant à base documentaire (RAG) répond parfois à côté, ou affirme ce que la source ne dit pas.

**Décision.** Avant d'afficher : le passage répond-il à la question ? la réponse est-elle dite dans le passage ? Sinon : « je ne sais pas, voici le lien ».

## Lancer
```sh
.venv/bin/python cas_usage/10_rag_source/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 10 — Dans un assistant à base documentaire (RAG) : garder les bons passages, et vérifier que la réponse s'appuie sur la source."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

PERTINENT = "Ce passage contient-il l'information qui permet de répondre à la question ?"
APPUYEE = "Tout ce qu'affirme la réponse est-il dit dans le passage source ?"

ok_p = ok_a = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    p1 = modele.decide(wyat.Request.noul(PERTINENT, context={"question": ligne["question"], "passage": ligne["passage"]})).probability_true
    p2 = modele.decide(wyat.Request.noul(APPUYEE, context={"passage source": ligne["passage"], "réponse": ligne["reponse"]})).probability_true
    pert, app = ("oui" if p1 >= 0.5 else "non"), ("oui" if p2 >= 0.5 else "non")
    n += 1
    ok_p += pert == ligne["pertinent"]
    ok_a += app == ligne["appuyee"]
    action = "afficher la réponse" if pert == app == "oui" else "ne pas afficher : « je ne sais pas, voici le lien »"
    print(f"{ligne['id']} pertinent {p1:.2f} ({pert}, attendu {ligne['pertinent']}) · appuyée {p2:.2f} ({app}, attendu {ligne['appuyee']}) → {action}")
print(f"\npassage pertinent : {ok_p}/{n} justes ; réponse appuyée par la source : {ok_a}/{n} justes")
```

## Sortie réelle (mlx)
```
g1 pertinent 0.99 (oui, attendu oui) · appuyée 0.98 (oui, attendu oui) → afficher la réponse
g2 pertinent 0.99 (oui, attendu oui) · appuyée 0.01 (non, attendu non) → ne pas afficher : « je ne sais pas, voici le lien »
g3 pertinent 0.04 (non, attendu non) · appuyée 0.39 (non, attendu non) → ne pas afficher : « je ne sais pas, voici le lien »
g4 pertinent 0.98 (oui, attendu oui) · appuyée 0.99 (oui, attendu oui) → afficher la réponse
g5 pertinent 0.99 (oui, attendu oui) · appuyée 0.97 (oui, attendu oui) → afficher la réponse
g6 pertinent 0.99 (oui, attendu non) · appuyée 0.72 (oui, attendu non) → afficher la réponse
g7 pertinent 0.90 (oui, attendu oui) · appuyée 0.92 (oui, attendu oui) → afficher la réponse
g8 pertinent 0.90 (oui, attendu oui) · appuyée 0.96 (oui, attendu non) → afficher la réponse

passage pertinent : 7/8 justes ; réponse appuyée par la source : 6/8 justes

[mlx, 4 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `passage pertinent : 7/8 justes ; réponse appuyée par la source : 6/8 justes` (identique)

## Adapter chez vous
Branché entre la recherche et l'affichage ; le seuil réglé sur 50 paires question / passage de votre base.

## Ce qui se passe et pourquoi (résultats et pièges)
Il attrape une réponse fausse grossière (30 jours au lieu de 14 : 0,01) mais **laisse passer une contradiction nette** (« ouvert 7 jours sur 7 » contre « du lundi au samedi » : 0,96) et un passage hors sujet du même thème. Un modèle spécialisé de vérification fera mieux.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
