<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 20 — Fil d'échanges fournisseur : quelle est la demande actuelle ? (fraude au changement de RIB)

*Comptabilité fournisseurs / trésorerie · secteur : Banque, tous secteurs · type de tâche : **Choice** · ✅ à montrer*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (10 lignes).*

**Problème.** Les fraudes au virement passent par un changement de coordonnées bancaires glissé dans un échange, parfois contredit ensuite.

**Décision.** « D'après le dernier état de l'échange, que demande le fournisseur ? » → paiement habituel / changement de RIB / report ou annulation / autre. Tout changement de RIB, ou marge < 0,4 → **contre-appel** au numéro connu, jamais automatisé.

## Lancer
```sh
.venv/bin/python cas_usage/20_demande_modifiee_virement/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 20 — Fil d'échanges avec un fournisseur : quelle est la demande ACTUELLE ? (Choice ; tout changement de RIB → contre-appel)"""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {
    "paiement_habituel": "Payer la facture sur les coordonnées bancaires habituelles, déjà connues",
    "changement_rib": "Payer sur de nouvelles coordonnées bancaires (nouvel IBAN, nouvelle banque)",
    "report_annulation": "Reporter, suspendre ou annuler le paiement",
    "autre": "Autre demande sans rapport avec le paiement (livraison, devis, contact)",
}

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    fil = [m.strip() for m in l["fil"].split("||")]          # messages du plus ancien au plus récent
    contexte = "\n".join(f"Message {i + 1} : {m}" for i, m in enumerate(fil))
    d = modele.decide(wyat.Request.choice("D'après le dernier état de l'échange, que demande le fournisseur ?", OPTIONS, context=contexte))
    if d.selected == "changement_rib" or d.probability_margin < 0.4:
        action = "CONTRE-APPEL au numéro connu avant tout paiement"   # procédure anti-fraude, jamais automatisée
    else:
        action = "traitement normal"
    n += 1
    justes += d.selected == l["attendu"]
    print(f"{fil[-1][:56]:<56} → {d.selected:<18} marge {d.probability_margin:.2f} {action} {'✓' if d.selected == l['attendu'] else '✗ attendu ' + l['attendu']}")
print(f"\n{justes}/{n} demandes actuelles identifiées")
```

## Sortie réelle (mlx)
```
Merci de régler comme d'habitude sous 30 jours.          → paiement_habituel  marge 0.99 traitement normal ✓
Petite précision : nous avons changé de banque, merci d' → changement_rib     marge 0.98 CONTRE-APPEL au numéro connu avant tout paiement ✓
Pardon, message envoyé par erreur : nos coordonnées banc → paiement_habituel  marge 0.93 traitement normal ✓
Finalement, merci de ne pas régler cette facture : un av → report_annulation  marge 0.99 traitement normal ✓
Pouvez-vous confirmer l'adresse de livraison du site de  → autre              marge 0.81 traitement normal ✓
Suite à un audit, les paiements doivent désormais être f → changement_rib     marge 0.74 CONTRE-APPEL au numéro connu avant tout paiement ✓
Pour cette facture-ci, l'ancien compte est encore valabl → paiement_habituel  marge 0.94 traitement normal ✓
En raison d'un litige sur la livraison, nous suspendons  → report_annulation  marge 0.99 traitement normal ✓
Finalement nous en aurons besoin de 250.                 → autre              marge 0.77 traitement normal ✓
Je confirme ce nouvel IBAN, merci de mettre à jour votre → changement_rib     marge 0.98 CONTRE-APPEL au numéro connu avant tout paiement ✓

10/10 demandes actuelles identifiées

[mlx, 4 s chargement compris]
```

## Adapter chez vous
Branché sur la boîte de la comptabilité fournisseurs ; le contre-appel reste la procédure de référence ; journal des alertes pour l'audit.

## Ce qui se passe et pourquoi (résultats et pièges)
Première version, non retouchée : **10/10**, y compris les messages qui annulent le précédent (« envoyé par erreur, payez sur le compte habituel »). 10 fils synthétiques ne prouvent rien : chez vous, mesurez sur de vrais fils anonymisés. Le modèle ne vérifie pas l'IBAN : c'est le contre-appel qui protège.

Repère de benchmark associé : DMBench Mise à jour (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
