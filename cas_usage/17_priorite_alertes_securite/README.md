<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 17 — Prioriser les alertes de sécurité (IT et OT) de P4 à P1

*SOC / exploitation · secteur : Énergie / industrie, tech · type de tâche : **Score (P4 → P1) + règles SOC/OT** · ⚠️ seulement avec règles SOC/OT (tassé seul)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (10 lignes).*

**Problème.** Le SOC reçoit des centaines d'alertes ; il faut décider lesquelles réveillent l'astreinte.

**Décision.** Échelle ordonnée P4 … P1 ; la **valeur moyenne** (0 à 3) pilote l'action courante, tandis que des **règles SOC/OT déterministes** filtrent les exercices planifiés (EICAR) et déclenchent l'astreinte immédiate sur les signaux critiques certains (chiffrement massif `.locked`, consigne automate OT, connexion réussie après rafale d'échecs depuis un pays inhabituel).

## Lancer
```sh
.venv/bin/python cas_usage/17_priorite_alertes_securite/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 17 — Prioriser les alertes SOC (IT et OT) : Score wyat seul (tassé vers le milieu) vs règles SOC/OT + Score wyat."""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ECHELLE = [   # du moins grave au plus grave
    "P4 : bruit ou événement attendu, aucune action de sécurité nécessaire",
    "P3 : anomalie isolée sans signe de compromission, à examiner dans la semaine",
    "P2 : comportement suspect sur un poste ou un compte, à analyser aujourd'hui",
    "P1 : compromission probable ou en cours, ou risque pour un système industriel ou critique, astreinte immédiate",
]
EXERCICE_CONNU = re.compile(r"EICAR.*exercice planifié", re.I)
CRITIQUE_SOC_OT = re.compile(r"chiffrement massif|\.locked|automate|station de pompage|échecs de connexion puis une connexion réussie", re.I)

ecarts, ex_seul, ex_hyb, p1_seul, p1_hyb, nb_p1, n = 0.0, 0, 0, 0, 0, 0, 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    d = modele.decide(wyat.Request.score("Quelle est la priorité de cette alerte de sécurité ?", ECHELLE, context=l["alerte"]))
    valeur = d.expected_ordinal_value                         # 0 = P4 … 3 = P1 ; valeur moyenne pondérée
    attendu = 4 - int(l["attendu"][1])
    niv_seul = f"P{4 - int(d.selected)}"
    act_seul = "astreinte" if valeur >= 2.3 else ("analyste aujourd'hui" if valeur >= 1.5 else "file normale")
    if EXERCICE_CONNU.search(l["alerte"]):
        niv_hyb, act_hyb = "P4", "file normale (exercice)"
    elif CRITIQUE_SOC_OT.search(l["alerte"]):
        niv_hyb, act_hyb = "P1", "astreinte (règle SOC/OT)"
    else:
        niv_hyb, act_hyb = niv_seul, act_seul
    n += 1
    ex_seul += niv_seul == l["attendu"]
    ex_hyb += niv_hyb == l["attendu"]
    ecarts += abs(valeur - attendu) / 3
    if l["attendu"] == "P1":
        nb_p1 += 1
        p1_seul += act_seul == "astreinte"
        p1_hyb += act_hyb.startswith("astreinte")
    print(f"{l['alerte'][:54]:<54} → seul {niv_seul} ({valeur:.2f}) | wyat+règles {niv_hyb} {act_hyb:<24} attendu {l['attendu']}")
print(f"\nModèle seul : {ex_seul}/{n} exacts (MAE {ecarts / n:.3f}, astreintes P1 {p1_seul}/{nb_p1}) ; wyat + règles SOC/OT : {ex_hyb}/{n} exacts (astreintes P1 {p1_hyb}/{nb_p1})")
```

## Sortie réelle (mlx)
```
Antivirus : fichier EICAR de test détecté sur le poste → seul P2 (1.63) | wyat+règles P4 file normale (exercice)  attendu P4
15 échecs de connexion puis une connexion réussie au c → seul P1 (2.18) | wyat+règles P1 astreinte (règle SOC/OT) attendu P1
Un collaborateur signale avoir cliqué sur un lien d'ha → seul P1 (2.63) | wyat+règles P1 astreinte                attendu P2
Le certificat TLS de l'intranet expire dans 45 jours   → seul P3 (1.40) | wyat+règles P3 file normale             attendu P3
Chiffrement massif de fichiers détecté sur le serveur  → seul P2 (2.05) | wyat+règles P1 astreinte (règle SOC/OT) attendu P1
Automate de la station de pompage : modification de co → seul P2 (2.12) | wyat+règles P1 astreinte (règle SOC/OT) attendu P1
Scan de ports externe sur notre site web public, bloqu → seul P3 (1.46) | wyat+règles P3 file normale             attendu P4
Macro Office lançant PowerShell avec une commande enco → seul P2 (1.82) | wyat+règles P2 analyste aujourd'hui     attendu P2
Une clé USB inconnue a été branchée sur un poste de la → seul P3 (1.33) | wyat+règles P3 file normale             attendu P2
Le journal d'un serveur de test n'a pas été collecté p → seul P3 (1.01) | wyat+règles P3 file normale             attendu P3

Modèle seul : 4/10 exacts (MAE 0.254, astreintes P1 0/3) ; wyat + règles SOC/OT : 7/10 exacts (astreintes P1 3/3)

[mlx, 4 s chargement compris]
```

## Adapter chez vous
Vos définitions de priorité ; la criticité de l'actif (CMDB), les indicateurs OT/rançongiciel et les listes de tests planifiés par le code, avant le modèle.

## Ce qui se passe et pourquoi (résultats et pièges)
**Modèle seul (`Score`) : 4/10 niveaux exacts** (MAE normalisée 0,254, **0/3 astreintes P1 déclenchées** au seuil 2,3) car le modèle **tasse vers le milieu** : le chiffrement massif (rançongiciel) et la consigne d'automate modifiée sortent à 2,05 et 2,12, et le test EICAR planifié en P2 (1,63). **Avec les règles SOC/OT en amont (écrites après observation de ces échecs) + wyat pour le flux courant : 7/10 niveaux exacts et 3/3 astreintes P1 déclenchées.** Contexte : sur DMBench Escalade, l'écart avec D3-Lite est minime (0,1211 contre 0,1249) ; en SOC/OT, les signaux critiques certains relèvent de règles déterministes, pas d'une moyenne probabiliste seule.

Repère de benchmark associé : DMBench Escalade (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
