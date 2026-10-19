<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 02 — Router les courriers et documents entrants

*Accueil / services généraux · secteur : Tous · type de tâche : **Choice** · ✅ à montrer*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (12 lignes).*

**Problème.** Factures, arrêts de travail, mises en demeure et devis arrivent à la même adresse ; chacun doit partir au bon service.

**Décision.** « À quel service transmettre ce document ? » → comptabilité / RH / juridique / achats / informatique. Action : transférer le mail ou le PDF (texte extrait) dans la bonne boîte.

## Lancer
```sh
.venv/bin/python cas_usage/02_routage_courrier/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 2 — Router les courriers et documents entrants vers le bon service de l'entreprise."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

SERVICES = {
    "comptabilite": "Comptabilité : factures fournisseurs, relances de paiement, attestations fiscales et sociales",
    "rh": "Ressources humaines : salariés, candidatures, congés, arrêts de travail, paie",
    "juridique": "Juridique : contrats, avenants, mises en demeure, litiges, propriété intellectuelle",
    "achats": "Achats : devis, propositions commerciales de fournisseurs, commandes de matériel",
    "informatique": "Informatique interne : panne d'ordinateur, accès, VPN, logiciels des salariés",
}

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.choice("À quel service faut-il transmettre ce document ?", SERVICES, context=ligne["document"]))
    n += 1
    justes += d.selected == ligne["attendu"]
    signe = "✓" if d.selected == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['document'][:62]:<62} → {d.selected:<13} marge {d.probability_margin:.2f} {signe}")
print(f"\n{justes}/{n} documents bien routés")
```

## Sortie réelle (mlx)
```
Facture n° F-2026-0912 — Bureau Plus — 1 240,00 € TTC — échéan → comptabilite  marge 0.99 ✓
Arrêt de travail de M. Leroy du 12 au 19 octobre, à transmettr → rh            marge 0.98 ✓
Mise en demeure : nous vous mettons en demeure de cesser l'uti → juridique     marge 0.96 ✓
Devis n° 3381 : 40 écrans 27 pouces, valable 30 jours, livrais → achats        marge 0.99 ✓
Mon ordinateur portable ne démarre plus depuis la mise à jour  → informatique  marge 0.96 ✓
Relance : notre facture du 3 septembre reste impayée à ce jour → comptabilite  marge 0.95 ✓
Demande de congés payés du 22 au 31 décembre — signée par le r → rh            marge 0.95 ✓
Avenant n° 2 au contrat de prestation : modification de la dur → juridique     marge 0.97 ✓
Proposition commerciale pour le renouvellement de la flotte de → achats        marge 0.76 ✓
Le VPN refuse ma connexion depuis l'hôtel                      → informatique  marge 0.99 ✓
Attestation URSSAF de vigilance demandée par notre client pour → comptabilite  marge 0.20 ✓
Candidature spontanée pour un poste de technicien fibre, CV en → rh            marge 0.93 ✓

12/12 documents bien routés

[mlx, 4 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `12/12 documents bien routés` (identique)

## Adapter chez vous
Vos services, avec 3 ou 4 exemples de documents typiques dans chaque option ; texte des PDF extrait avec `pdftotext` ; lancé par le script qui relève la boîte (IMAP) ou en lot (`integrations/lot_cron.sh`).

## Ce qui se passe et pourquoi (résultats et pièges)
Documents à cheval (une relance de facture contestée : compta ou juridique ?) : décidez la règle à l'avance et écrivez-la dans les options ; ne mettez que la première page.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
