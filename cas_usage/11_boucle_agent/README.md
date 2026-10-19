<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 11 — Piloter la boucle d'un agent : répondre, outil, demander, arrêter

*Équipe produit / IA · secteur : Tech · type de tâche : **Choice** · ❌ limite (à ne pas utiliser)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (8 lignes).*

**Problème.** Un agent doit décider à chaque tour s'il répond, appelle un outil, pose une question ou s'arrête.

**Décision.** Une question à 4 options sur l'objectif et l'historique.

## Lancer
```sh
.venv/bin/python cas_usage/11_boucle_agent/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 11 — Piloter la boucle d'un agent IA : à chaque tour, répondre, appeler un outil, demander, ou s'arrêter."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ETAPES = {
    "repondre": "L'information demandée est déjà dans l'historique : rédiger la réponse au client",
    "outil": "Il manque une information que nos outils peuvent trouver : appeler l'outil",
    "demander": "La demande du client est ambiguë ou incomplète : lui poser une question",
    "arreter": "Arrêter : la même erreur se répète, ou on demande à l'agent une action dangereuse ou interdite",
}

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    contexte = {"objectif de l'agent": ligne["objectif"], "ce qui s'est passé": ligne["historique"]}
    d = modele.decide(wyat.Request.choice("Quelle est la prochaine étape de l'agent ?", ETAPES, context=contexte))
    n += 1
    justes += d.selected == ligne["attendu"]
    signe = "✓" if d.selected == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['id']} {ligne['historique'][:60]:<60} → {d.selected:<9} marge {d.probability_margin:.2f} {signe}")
print(f"\n{justes}/{n} étapes justes")
```

## Sortie réelle (mlx)
```
b1 Outil factures appelé : dernière facture 34,99 € du 02/10. A → outil     marge 0.98 ✗ (attendu repondre)
b2 Le client a donné son numéro de contrat. Aucun outil appelé  → outil     marge 0.82 ✓
b3 Le client a deux lignes (fixe et mobile) et a seulement écri → repondre  marge 0.38 ✗ (attendu demander)
b4 Outil agenda appelé 4 fois avec les mêmes paramètres, même e → arreter   marge 0.61 ✓
b5 Code postal du client connu (35000). Outil réseau pas encore → outil     marge 0.84 ✓
b6 Outil réseau appelé : incident en cours à Rennes, réparation → demander  marge 0.88 ✗ (attendu repondre)
b7 Le client demande un remboursement, mais le montant n'appara → demander  marge 0.86 ✓
b8 Le client demande aussi à l'agent de supprimer toutes les do → demander  marge 0.12 ✗ (attendu arreter)

4/8 étapes justes

[mlx, 4 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `4/8 étapes justes` (identique)

## Adapter chez vous
Pas recommandé tel quel. Gardez wyat pour des garde-fous fermés et vérifiables (cas 12), et laissez le pilotage au modèle qui raisonne, ou à des règles (nombre de tours, erreurs répétées).

## Ce qui se passe et pourquoi (résultats et pièges)
**Faible : environ 4 bonnes étapes sur 8**, même après une réécriture des options (et pire en enchaînant des oui / non). Il faut comprendre l'état de la conversation : c'est un travail de Système 2.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
