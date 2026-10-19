<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 22 — Industrie / énergie : router la maintenance et repérer les risques HSE

*Maintenance / HSE · secteur : Énergie / industrie · type de tâche : **Choice + Noul** · ✅ à montrer*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (10 lignes).*

**Problème.** Les demandes de maintenance arrivent en texte libre ; les signaux de sécurité y sont noyés.

**Décision.** Choice sur le métier (mécanique, électricité, instrumentation, automatisme) et oui / non « risque pour les personnes ou l'environnement ? » avec un seuil **bas** (0,3) : un appel de trop au responsable HSE coûte peu.

## Lancer
```sh
.venv/bin/python cas_usage/22_maintenance_et_hse/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 22 — Industrie / énergie : router les demandes de maintenance par métier (Choice) et repérer tout risque HSE (Noul, seuil bas)."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

METIERS = {
    "mecanique": "Mécanique : pompe, vanne, roulement, vibration, fuite sur une tuyauterie, courroie",
    "electrique": "Électricité : armoire électrique, disjoncteur, moteur électrique, câblage, éclairage",
    "instrumentation": "Instrumentation : capteur, transmetteur, mesure de pression, de débit ou de température, étalonnage",
    "automatisme": "Automatisme et informatique industrielle : automate, supervision, écran opérateur, réseau industriel",
}
HSE = ("Ce signalement décrit-il un risque pour la sécurité des personnes ou pour l'environnement "
       "(fuite de produit, odeur de gaz, risque de chute, brûlure, électrocution, déversement) ?")
SEUIL_HSE = 0.3   # bas exprès : un appel de trop au responsable HSE coûte peu

metier_ok = hse_ok = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    d = modele.decide(wyat.Request.choice("Quel métier doit intervenir ?", METIERS, context=l["demande"]))
    p = modele.decide(wyat.Request.noul(HSE, context=l["demande"])).probability_true
    alerte = p >= SEUIL_HSE
    n += 1
    metier_ok += d.selected == l["metier"]
    hse_ok += alerte == (l["hse"] == "oui")
    print(f"{l['demande'][:56]:<56} → {d.selected:<15} (marge {d.probability_margin:.2f}) HSE {p:.2f}{' ⚠ RESPONSABLE HSE' if alerte else ''}"
          f"  attendu {l['metier']}/{l['hse']}")
print(f"\nmétier {metier_ok}/{n} ; signal HSE {hse_ok}/{n}")
```

## Sortie réelle (mlx)
```
La pompe P-204 vibre fortement et fait un bruit de frott → mecanique       (marge 0.99) HSE 0.05  attendu mecanique/non
Odeur de gaz près de la vanne V-12, zone de dépotage ; l → mecanique       (marge 0.98) HSE 0.97 ⚠ RESPONSABLE HSE  attendu mecanique/oui
Le capteur de pression PT-301 affiche une valeur figée à → instrumentation (marge 0.97) HSE 0.19  attendu instrumentation/non
Le disjoncteur de l'armoire A3 saute à chaque démarrage  → electrique      (marge 0.98) HSE 0.95 ⚠ RESPONSABLE HSE  attendu electrique/oui
L'écran de supervision de la ligne 2 ne se met plus à jo → automatisme     (marge 0.98) HSE 0.03  attendu automatisme/non
Fuite d'huile hydraulique au pied de la presse, la flaqu → mecanique       (marge 0.89) HSE 0.83 ⚠ RESPONSABLE HSE  attendu mecanique/oui
Demande d'étalonnage annuel des débitmètres du poste de  → instrumentation (marge 0.97) HSE 0.19  attendu instrumentation/non
Le garde-corps de la passerelle du silo 3 est desserré e → mecanique       (marge 0.55) HSE 0.58 ⚠ RESPONSABLE HSE  attendu mecanique/oui
Plusieurs néons de l'atelier B clignotent.               → electrique      (marge 0.67) HSE 0.05  attendu electrique/non
Après la mise à jour, l'automate de la station de traite → automatisme     (marge 0.89) HSE 0.06  attendu automatisme/non

métier 10/10 ; signal HSE 10/10

[mlx, 5 s chargement compris]
```

## Adapter chez vous
Vos métiers et vos équipements ; les mots-clés de danger (gaz, H2S) aussi en règles ; branché sur la GMAO à la création de la demande.

## Ce qui se passe et pourquoi (résultats et pièges)
Première version, non retouchée : **10/10 et 10/10**. Le garde-corps desserré n'est signalé qu'avec le seuil bas (0,58 : il passerait encore à 0,5, pas à 0,6). Données courtes et nettes : sur de vraies demandes, mesurez avant d'annoncer quoi que ce soit.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
