<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 08 — Donner une priorité aux alertes d'exploitation

*IT / exploitation · secteur : Tech · type de tâche : **Score (P4 → P1)** · ⚠️ moyen (bon à un niveau près)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (10 lignes).*

**Problème.** Toutes les alertes arrivent en « urgent » ; l'astreinte est réveillée pour une imprimante.

**Décision.** Échelle ordonnée P4 … P1 ; wyat donne une probabilité par niveau et une valeur moyenne. Action : P1 → astreinte, P2 → aujourd'hui, P3/P4 → file normale.

## Lancer
```sh
.venv/bin/python cas_usage/08_priorite_incident/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 8 — Donner une priorité P1 à P4 aux alertes d'exploitation (Score : une échelle ordonnée)."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ECHELLE = [   # du moins grave au plus grave : wyat rend une probabilité par niveau et une valeur moyenne
    "P4 : aucune gêne pour les clients, demande de confort ou cosmétique, peut attendre des semaines",
    "P3 : gêne légère ou risque lointain, le service fonctionne, à traiter cette semaine",
    "P2 : dégradation importante ou panne prévisible très bientôt, à traiter aujourd'hui",
    "P1 : service essentiel en panne pour beaucoup de clients, intervention immédiate, astreinte réveillée",
]

justes = proches = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.score("Quelle est la priorité de cette alerte ?", ECHELLE, context=ligne["alerte"]))
    niveau = f"P{4 - int(d.selected)}"
    attendu = int(ligne["attendu"][1])
    n += 1
    justes += niveau == ligne["attendu"]
    proches += abs(int(niveau[1]) - attendu) <= 1
    signe = "✓" if niveau == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['alerte'][:66]:<66} → {niveau} (valeur {d.expected_ordinal_value:.2f} sur 0–3) {signe}")
print(f"\n{justes}/{n} priorités exactes, {proches}/{n} à un niveau près")
```

## Sortie réelle (mlx)
```
Le site de paiement est inaccessible pour tous les clients depuis  → P1 (valeur 2.95 sur 0–3) ✓
Panne fibre sur tout le quartier de Bellevue (environ 2 000 abonné → P1 (valeur 2.67 sur 0–3) ✓
Le disque du serveur de sauvegarde est plein à 91 %, les sauvegard → P3 (valeur 1.18 sur 0–3) ✓
L'imprimante du 2e étage n'imprime plus en couleur                 → P2 (valeur 1.53 sur 0–3) ✗ (attendu P4)
L'application mobile est lente pour certains utilisateurs, mais fo → P3 (valeur 1.13 sur 0–3) ✓
Le certificat HTTPS du site principal expire dans 2 jours          → P3 (valeur 1.68 sur 0–3) ✗ (attendu P2)
Un salarié signale une faute de frappe sur la page « Contact »     → P3 (valeur 0.72 sur 0–3) ✗ (attendu P4)
Les clients ne peuvent plus se connecter à leur espace client, err → P1 (valeur 2.91 sur 0–3) ✓
La base de données répond deux fois plus lentement que d'habitude  → P2 (valeur 1.93 sur 0–3) ✓
Demande d'ajout d'un nouvel écran pour le poste d'accueil          → P4 (valeur 0.30 sur 0–3) ✓

7/10 priorités exactes, 9/10 à un niveau près

[mlx, 4 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `7/10 priorités exactes, 9/10 à un niveau près` (identique)

## Adapter chez vous
Vos définitions de priorité (celles de votre ITIL ou de votre contrat de service) ; réglez la règle « P1 » sur la valeur moyenne (par exemple ≥ 2,5) plutôt que sur le niveau le plus probable.

## Ce qui se passe et pourquoi (résultats et pièges)
Les petites demandes sont surévaluées (imprimante couleur → P2) ; une expiration de certificat « dans 2 jours » est sous-évaluée : le temps restant, c'est du code (date d'expiration).

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
