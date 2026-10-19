<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 23 — Avis clients (FR / EN) : aspects cités et tonalité

*Service client / qualité · secteur : Luxe / commerce · type de tâche : **Choice (un par aspect)** · ⚠️ moyen (sur-étiquette)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (8 lignes).*

**Problème.** Le service client veut savoir, avis par avis, ce qui est loué ou reproché : produit, boutique, livraison, après-vente.

**Décision.** Pour chaque aspect, un Choice positif / négatif / absent ; sortie : des étiquettes `aspect:tonalité`. Mesure : F1 par avis.

## Lancer
```sh
.venv/bin/python cas_usage/23_avis_clients_aspects/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 23 — Avis clients (FR / EN) : étiqueter chaque aspect cité et sa tonalité (un Choice par aspect), pour le service client."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

ASPECTS = {
    "produit": "la qualité du produit (matière, finition, solidité)",
    "boutique": "l'accueil et le conseil en boutique",
    "livraison": "la livraison ou l'emballage",
    "apres_vente": "le service après-vente, la réparation ou l'entretien",
}
TONALITE = {"positif": "L'avis en parle positivement", "negatif": "L'avis en parle négativement", "absent": "L'avis n'en parle pas"}

def etiquettes(avis: str) -> set[str]:
    sortie = set()
    for aspect, libelle in ASPECTS.items():
        d = modele.decide(wyat.Request.choice(f"Que dit cet avis sur {libelle} ?", TONALITE, context=avis))
        if d.selected != "absent":
            sortie.add(f"{aspect}:{d.selected}")
    return sortie

total_f1 = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    predit, attendu = etiquettes(l["avis"]), set(filter(None, l["attendu"].split(";")))
    vp = len(predit & attendu)
    f1 = 1.0 if not predit and not attendu else (2 * vp / (len(predit) + len(attendu)))
    total_f1 += f1
    n += 1
    print(f"{l['avis'][:54]:<54} → {', '.join(sorted(predit)) or '-'}  (F1 {f1:.2f} ; attendu {', '.join(sorted(attendu))})")
print(f"\nF1 moyen par avis : {100 * total_f1 / n:.1f} sur 100")
```

## Sortie réelle (mlx)
```
Le sac est magnifique, le cuir est d'une grande qualit → apres_vente:positif, boutique:positif, produit:positif  (F1 0.80 ; attendu boutique:positif, produit:positif)
Colis arrivé avec trois jours de retard et la boîte ét → apres_vente:negatif, livraison:negatif, produit:negatif  (F1 0.50 ; attendu livraison:negatif)
Superb watch, but the boutique staff ignored us for tw → apres_vente:negatif, boutique:negatif  (F1 0.50 ; attendu boutique:negatif, produit:positif)
J'ai confié mon carré pour un nettoyage : rendu impecc → apres_vente:positif, boutique:positif, livraison:positif, produit:positif  (F1 0.40 ; attendu apres_vente:positif)
La couture s'est défaite au bout d'un mois et le servi → apres_vente:negatif, boutique:negatif  (F1 0.50 ; attendu apres_vente:negatif, produit:negatif)
Emballage soigné, livraison rapide.                    → livraison:positif  (F1 1.00 ; attendu livraison:positif)
The repair took four months and nobody kept me informe → apres_vente:negatif, boutique:negatif, livraison:negatif  (F1 0.50 ; attendu apres_vente:negatif)
Accueil chaleureux à la boutique de la rue du Faubourg → boutique:positif  (F1 1.00 ; attendu boutique:positif)

F1 moyen par avis : 65.0 sur 100

[mlx, 6 s chargement compris]
```

## Adapter chez vous
Vos aspects ; une revue humaine des avis négatifs ; les tableaux de bord sur des volumes, jamais sur un avis isolé.

## Ce qui se passe et pourquoi (résultats et pièges)
Première version, non retouchée : **F1 moyen 65 sur 100**. Le modèle **ajoute des aspects absents** (« après-vente » et « boutique » inventés sur des avis qui n'en parlent pas) : l'option « absent » n'est pas assez choisie. Fonctionne en anglais comme en français. Contexte : sur ACOS (étiquetage d'aspects), wyat-1-800m fait 8,05 sur 100 contre 6,45 pour D3-Lite : les deux sont très bas sur ce format.

Repère de benchmark associé : ACOS (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
