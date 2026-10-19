<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 21 — Banque : pré-tri des alertes KYC / LCB-FT

*Conformité / sécurité financière · secteur : Banque · type de tâche : **Choice + journal** · ✅ à montrer (avec repli humain)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (10 lignes).*

**Problème.** Les outils de filtrage produisent beaucoup d'alertes, dont une majorité de faux positifs (homonymies) et de pièces manquantes.

**Décision.** Homonymie / pièce manquante / mise à jour / analyse LCB-FT. Rien n'est clôturé sans humain : l'homonymie est **proposée** à la clôture et validée en lot ; marge < 0,5 → analyste. Probabilité de chaque option écrite dans `journal_kyc.jsonl`.

## Lancer
```sh
.venv/bin/python cas_usage/21_alertes_kyc/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 21 — Banque : pré-tri des alertes KYC / LCB-FT pour les analystes (Choice, rien n'est clôturé sans humain, journal d'audit)."""
import csv
import datetime
import json
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {
    "homonymie": "Probable faux positif : homonymie avec une personne d'une liste, date de naissance ou nationalité différente",
    "piece_manquante": "Pièce manquante ou expirée : justificatif d'identité, de domicile ou de revenus à demander au client",
    "mise_a_jour": "Changement de situation du client à mettre à jour : adresse, employeur, revenus, statut",
    "analyse_lcbft": "Opérations inhabituelles à analyser : montants ou flux incohérents avec le profil, fractionnement, pays à risque, tiers inconnus",
}
FILE = {"homonymie": "clôture proposée (validation analyste en lot)", "piece_manquante": "relance client",
        "mise_a_jour": "mise à jour du dossier", "analyse_lcbft": "ANALYSTE LCB-FT (prioritaire)"}

justes = n = 0
with open(ICI / "journal_kyc.jsonl", "w", encoding="utf-8") as journal:
    with open(ICI / "donnees.csv", encoding="utf-8") as _f:
        _lignes = list(csv.DictReader(_f))
    for l in _lignes:
        d = modele.decide(wyat.Request.choice("Quelle suite donner à cette alerte ?", OPTIONS, context=l["alerte"]))
        suite = FILE[d.selected] if d.probability_margin >= 0.5 else "analyste (marge faible)"
        journal.write(json.dumps({"horodatage": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "alerte": l["id"],
                                  "modele": d.model_id[:16], "probabilites": {k: round(v, 4) for k, v in d.probabilities_by_id.items()},
                                  "choix": d.selected, "marge": round(d.probability_margin, 4), "suite": suite}, ensure_ascii=False) + "\n")
        n += 1
        justes += d.selected == l["attendu"]
        print(f"{l['alerte'][:58]:<58} → {d.selected:<15} marge {d.probability_margin:.2f} {suite[:30]:<30} {'✓' if d.selected == l['attendu'] else '✗ attendu ' + l['attendu']}")
print(f"\n{justes}/{n} alertes bien pré-triées ; journal (probabilité par option) : cas_usage/21_alertes_kyc/journal_kyc.jsonl")
```

## Sortie réelle (mlx)
```
Correspondance de nom avec une liste de sanctions : Jean D → homonymie       marge 0.76 clôture proposée (validation a ✓
La carte d'identité enregistrée pour ce client a expiré en → piece_manquante marge 0.54 relance client                 ✓
Dix dépôts en espèces de 9 500 € en deux semaines sur le c → piece_manquante marge 0.43 analyste (marge faible)        ✗ attendu analyse_lcbft
Le client signale un nouvel employeur et une hausse de sal → mise_a_jour     marge 0.93 mise à jour du dossier         ✓
Virements entrants réguliers d'une société inconnue immatr → analyse_lcbft   marge 0.98 ANALYSTE LCB-FT (prioritaire)  ✓
Justificatif de domicile de plus de trois mois pour l'ouve → piece_manquante marge 0.99 relance client                 ✓
Courrier retourné « n'habite pas à l'adresse indiquée » ;  → mise_a_jour     marge 0.98 mise à jour du dossier         ✓
Personne politiquement exposée : homonyme d'un ministre ét → homonymie       marge 0.29 analyste (marge faible)        ✓
Le chiffre d'affaires encaissé par cette petite boulangeri → analyse_lcbft   marge 0.75 ANALYSTE LCB-FT (prioritaire)  ✓
Avis d'imposition manquant pour l'étude du crédit immobili → piece_manquante marge 0.79 relance client                 ✓

9/10 alertes bien pré-triées ; journal (probabilité par option) : cas_usage/21_alertes_kyc/journal_kyc.jsonl

[mlx, 4 s chargement compris]
```

## Adapter chez vous
Vos motifs d'alerte réels ; la décision de déclaration de soupçon reste humaine ; le journal conservé selon votre politique d'archivage.

## Ce qui se passe et pourquoi (résultats et pièges)
Première version, non retouchée : **9/10**. L'erreur est la plus coûteuse possible : dix dépôts en espèces de 9 500 € (fractionnement) lus comme « pièce manquante » ; la marge faible (0,43) l'envoie quand même à un analyste. Sans le seuil, elle aurait été traitée comme une relance.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
