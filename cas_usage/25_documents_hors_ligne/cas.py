# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 25 — Environnement isolé (sans réseau) : niveau de manipulation d'un document, proposé à un humain habilité.

Le script COUPE le réseau dans le processus avant de charger le modèle : si quelque chose tentait de sortir, il échouerait.
Il faut donc un modèle déjà copié sur la machine : WYAT_MODEL=/chemin/vers/wyat-1-800m/model (voir docs/deploiement_hors_ligne.md).
"""
import csv
import os
import platform
import socket
from pathlib import Path

def _reseau_coupe(*_args, **_kwargs):
    raise ConnectionError("réseau coupé par le cas 25 : rien ne sort de cette machine")
socket.socket.connect = _reseau_coupe          # toute connexion sortante échoue désormais
socket.create_connection = _reseau_coupe

import wyat

ICI = Path(__file__).parent
chemin = os.environ.get("WYAT_MODEL", "")
if not Path(chemin).is_dir():
    raise SystemExit("Indiquez un modèle local : WYAT_MODEL=/chemin/vers/wyat-1-800m/model (le cas refuse de télécharger).")
modele = wyat.load(chemin, backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

NIVEAUX = {
    "libre": "Diffusion libre : information publique ou destinée à être publiée",
    "interne": "Usage interne : organisation, procédures courantes, comptes rendus sans donnée sensible",
    "a_proteger": "À protéger : données personnelles, informations de sécurité, contrats, plans, vulnérabilités, besoin d'en connaître",
}

justes = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    d = modele.decide(wyat.Request.choice("Quel niveau de manipulation proposer pour ce document ?", NIVEAUX, context=l["extrait"]))
    humain = d.selected == "a_proteger" or d.probability_margin < 0.6
    n += 1
    justes += d.selected == l["attendu"]
    print(f"{l['extrait'][:58]:<58} → {d.selected:<10} marge {d.probability_margin:.2f}{'  → avis d’une personne habilitée' if humain else ''}"
          f" {'✓' if d.selected == l['attendu'] else '✗ attendu ' + l['attendu']}")
print(f"\n{justes}/{n} niveaux proposés justes ; aucune connexion réseau n'a été possible pendant l'exécution")
