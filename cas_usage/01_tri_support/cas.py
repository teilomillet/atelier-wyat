# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 1 — Trier les messages du support de la boutique en ligne, avec repli humain (lot sur un CSV)."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {
    "livraison": "Livraison : colis en retard, perdu, suivi bloqué, livré mais pas reçu",
    "retour": "Retour, échange ou remboursement d'un article déjà reçu",
    "paiement": "Paiement : carte refusée, double débit, prélèvement sans commande",
    "compte": "Compte client : connexion, mot de passe, adresse e-mail, données du compte",
    "autre": "Autre demande précise sans rapport avec une commande",
}
SEUIL = 0.5   # marge minimale pour router sans humain

justes, sortie = 0, []
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.choice("Quel service doit traiter ce message ?", OPTIONS, context=ligne["message"]))
    file = d.selected if d.probability_margin >= SEUIL else "humain"
    justes += d.selected == ligne["attendu"]
    sortie.append({"id": ligne["id"], "file": file, "choix": d.selected, "marge": round(d.probability_margin, 2)})
    print(f"{ligne['message'][:60]:<60} → {file:<9} (choix {d.selected}, marge {d.probability_margin:.2f}, attendu {ligne['attendu']})")

with open(ICI / "routage.csv", "w", newline="", encoding="utf-8") as f:   # à reprendre par votre outil de tickets
    w = csv.DictWriter(f, fieldnames=sortie[0])
    w.writeheader()
    w.writerows(sortie)
print(f"\n{justes}/{len(sortie)} choix justes ; {sum(s['file'] == 'humain' for s in sortie)} message(s) pour un humain → routage.csv")
