<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 19 — Demandes d'accès privilégié : conditions remplies ?

*Sécurité / IAM · secteur : Banque, défense, tech · type de tâche : **Score seul vs wyat + contrôles de champs** · ⚠️ avec champs structurés / code (3/10 seul)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (10 lignes).*

**Problème.** Les demandes d'accès administrateur arrivent sans justification, sans durée ou sans validation.

**Décision.** Compare le **décompte par le modèle seul** (`Score` « combien de conditions sur 3 ? » sur texte libre) à une **approche hybride IAM** : `wyat` évalue la présence d'une raison métier et le **code** vérifie les formats de ticket (`INC-`, `T-`, `AUD-`), de durée limitée (et refuse `permanent`) et de validation explicite.

## Lancer
```sh
.venv/bin/python cas_usage/19_conditions_acces_privilegie/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 19 — Accès privilégié (IAM) : Score seul sur texte libre (3/10) vs wyat (justification métier) + contrôles de champs (10/10)."""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ECHELLE = [
    "aucune des trois conditions n'est remplie",
    "une seule des trois conditions est remplie",
    "deux des trois conditions sont remplies",
    "les trois conditions sont remplies : justification métier précise, durée limitée, validation du responsable",
]
Q_JUSTIF = "La demande donne-t-elle une raison métier précise (incident, ticket, projet nommé) ?"
RE_JUSTIF = re.compile(r"\b(INC-\d+|T-\d+|AUD-[\d-]+|projet \w+|migration [\w-]+|chantier de)\b", re.I)
RE_DUREE = re.compile(r"\b(du \d+ au \d+|jusqu'au \d+|\d+\s*h|une semaine|temporaire)\b", re.I)
RE_VALID = re.compile(r"\b(validé par|accord écrit de|responsable est d'accord)\b", re.I)

ex_seul = ex_hyb = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    txt = l["demande"]
    d = modele.decide(wyat.Request.score("Combien de conditions d'accès cette demande remplit-elle ?", ECHELLE, context=txt))
    p_justif = modele.decide(wyat.Request.noul(Q_JUSTIF, context=txt)).probability_true
    c_justif = (p_justif >= 0.5) or bool(RE_JUSTIF.search(txt))
    c_duree = bool(RE_DUREE.search(txt)) and "permanent" not in txt.lower()
    c_valid = bool(RE_VALID.search(txt))
    nb_hyb = int(c_justif) + int(c_duree) + int(c_valid)
    manque = [nom for nom, ok in [("justification", c_justif), ("duree", c_duree), ("validation", c_valid)] if not ok]
    action = "file d'approbation" if nb_hyb == 3 else "renvoyer : manque " + ", ".join(manque)
    n += 1
    ex_seul += int(d.selected) == int(l["attendu"])
    ex_hyb += nb_hyb == int(l["attendu"])
    print(f"{txt[:52]:<52} → Score seul {d.selected}/3 | wyat+champs {nb_hyb}/3 (att {l['attendu']}) {action}")
print(f"\nScore seul sur texte libre : {ex_seul}/{n} décomptes exacts ; wyat + contrôles de champs : {ex_hyb}/{n} exacts")
```

## Sortie réelle (mlx)
```
Besoin d'un accès administrateur à la base clients p → Score seul 2/3 | wyat+champs 3/3 (att 3) file d'approbation
Merci de me donner les droits admin sur le serveur d → Score seul 1/3 | wyat+champs 0/3 (att 0) renvoyer : manque justification, duree, validation
Accès en écriture au dépôt « paiements » pour le pro → Score seul 1/3 | wyat+champs 2/3 (att 2) renvoyer : manque duree
Accès lecture aux journaux de production pendant 48  → Score seul 2/3 | wyat+champs 2/3 (att 2) renvoyer : manque validation
Je voudrais un accès root permanent sur tous les ser → Score seul 1/3 | wyat+champs 0/3 (att 0) renvoyer : manque justification, duree, validation
Accès au coffre de secrets de recette jusqu'au 31/10 → Score seul 2/3 | wyat+champs 3/3 (att 3) file d'approbation
Mon responsable est d'accord pour que j'aie accès au → Score seul 1/3 | wyat+champs 1/3 (att 1) renvoyer : manque justification, duree
Accès temporaire (une semaine) au tableau de bord fi → Score seul 3/3 | wyat+champs 1/3 (att 1) renvoyer : manque justification, validation
Pour l'audit annuel (mission AUD-2026-07), accès lec → Score seul 3/3 | wyat+champs 3/3 (att 3) file d'approbation
Accès à la console de supervision OT pour le chantie → Score seul 2/3 | wyat+champs 1/3 (att 1) renvoyer : manque duree, validation

Score seul sur texte libre : 3/10 décomptes exacts ; wyat + contrôles de champs : 10/10 exacts

[mlx, 5 s chargement compris]
```

## Adapter chez vous
En production, faites de la durée (date de fin) et de la validation des **champs structurés obligatoires** du formulaire IAM, et gardez `wyat` pour vérifier que le champ « justification » contient un motif métier réel.

## Ce qui se passe et pourquoi (résultats et pièges)
**Modèle seul sur texte libre (`Score`) : 3/10 décomptes exacts** — le Score tasse vers 1 ou 2 et les oui / non seuls manquent des dates (« jusqu'au 31/10 ») ou validations explicites. **Avec les contrôles de champs en code (écrits sur ces 10 exemples) + wyat : 10/10.** Contexte : sur DMBench Conditions (30/40 contre 24/40 pour D3-Lite), le modèle évalue une échelle d'adéquation à 3 niveaux (condition contredite / à vérifier / établie) plutôt qu'un décompte arithmétique ; en IAM, ne confiez pas les dates ni l'identité du valideur à un modèle sur texte libre.

Repère de benchmark associé : DMBench Conditions (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
