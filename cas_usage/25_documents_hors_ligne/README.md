<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 25 — Environnement isolé : niveau de manipulation d'un document

*Défense / OIV / secteur public · secteur : Défense / souverain · type de tâche : **Choice, réseau coupé** · ⚠️ aide au tri seulement*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (10 lignes).*

**Problème.** Sur un réseau isolé, des documents doivent recevoir un niveau de manipulation avant d'être partagés.

**Décision.** Le script **coupe le réseau dans le processus** avant de charger le modèle, et refuse de démarrer sans modèle local. Choice libre / interne / à protéger ; « à protéger » ou marge < 0,6 → avis d'une personne habilitée. Le modèle **propose**, il ne classifie pas : la classification relève d'une autorité habilitée (IGI 1300 en France).

## Lancer
```sh
.venv/bin/python cas_usage/25_documents_hors_ligne/cas.py
```

## Le code (`cas.py`)
```python
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
```

## Sortie réelle (mlx)
```
Communiqué de presse : inauguration du nouveau centre de f → libre      marge 0.96 ✓
Liste nominative des personnels d'astreinte avec numéros d → a_proteger marge 0.79  → avis d’une personne habilitée ✓
Compte rendu de la réunion de service : planning des congé → interne    marge 0.99 ✓
Rapport d'audit : trois vulnérabilités critiques non corri → a_proteger marge 0.62  → avis d’une personne habilitée ✓
Offre d'emploi : technicien de maintenance, poste basé à T → interne    marge 0.91 ✗ attendu libre
Procédure interne de réservation des véhicules de service. → interne    marge 0.98 ✓
Plan des accès et des zones de surveillance vidéo du bâtim → interne    marge 0.46  → avis d’une personne habilitée ✗ attendu a_proteger
Note : le restaurant d'entreprise sera fermé vendredi pour → interne    marge 0.72 ✓
Contrat de maintenance avec le prestataire, montants et cl → interne    marge 0.16  → avis d’une personne habilitée ✗ attendu a_proteger
Rapport annuel publié sur le site institutionnel.          → interne    marge 0.90 ✗ attendu libre

6/10 niveaux proposés justes ; aucune connexion réseau n'a été possible pendant l'exécution

[mlx, 3 s chargement compris]
```

## Adapter chez vous
Copie du modèle par support validé (voir `docs/deploiement_hors_ligne.md`) ; vos niveaux internes ; journal local.

## Ce qui se passe et pourquoi (résultats et pièges)
Première version, non retouchée : **6/10**. Le modèle **sous-protège** : plan des zones de surveillance vidéo et contrat avec pénalités proposés en « interne » (marges 0,46 et 0,16, donc renvoyés à un humain) ; offre d'emploi et rapport annuel publiés jugés « internes » (sur-protection, sans gravité). À ne jamais utiliser pour abaisser un niveau.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
