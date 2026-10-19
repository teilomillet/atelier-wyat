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
