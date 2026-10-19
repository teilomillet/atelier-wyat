<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 07 — Modérer les avis clients avant publication

*E-commerce / marketing · secteur : Commerce · type de tâche : **Choice** · ✅ à montrer*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (13 lignes).*

**Problème.** Les avis doivent être publiés vite, sans insultes, publicité ni coordonnées, et les accusations graves relues.

**Décision.** publier / insulte / pub / coordonnées / à vérifier (insulte, pub, coordonnées → masquer). Action : publier, masquer, ou file de modération ; **marge < 0,3 → modération humaine**.

## Lancer
```sh
.venv/bin/python cas_usage/07_moderation_avis/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 7 — Modérer les avis clients avant publication : publier, masquer, ou faire vérifier par une personne."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {   # plusieurs options précises valent mieux qu'une option « masquer » fourre-tout
    "publier": "Avis sur le produit ou le service, positif ou négatif, même sévère, sans insulte ni menace",
    "insulte": "Insulte ou menace contre une personne",
    "pub": "Publicité, lien vers un autre site ou spam",
    "coordonnees": "L'avis contient une adresse postale, un numéro de téléphone ou un e-mail",
    "verifier": "Accusation grave (escroquerie, insulte reçue, fraude) contre l'entreprise ou un salarié, à vérifier avant publication",
}
ACTION = {"publier": "publier", "insulte": "masquer", "pub": "masquer", "coordonnees": "masquer", "verifier": "verifier"}

scores = {"ecriture": [0, 0], "verification": [0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.choice("Que faire de cet avis client avant publication ?", OPTIONS, context=ligne["avis"]))
    action = ACTION[d.selected] if d.probability_margin >= 0.3 else "verifier"   # en cas de doute : une personne
    scores[ligne["jeu"]][0] += action == ligne["attendu"]
    scores[ligne["jeu"]][1] += 1
    signe = "✓" if action == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['avis'][:62]:<62} → {action:<9} (choix {d.selected}, marge {d.probability_margin:.2f}) {signe}")
print("\n" + " ; ".join(f"{jeu} : {j}/{n} avis bien traités" for jeu, (j, n) in scores.items()))
```

## Sortie réelle (mlx)
```
Livraison rapide, la box marche très bien, je recommande.      → publier   (choix publier, marge 0.98) ✓
Service client nul. Trois appels pour rien. Je change d'opérat → publier   (choix publier, marge 0.79) ✓
Le technicien était une vraie ordure, je connais son adresse,  → verifier  (choix insulte, marge 0.29) ✗ (attendu masquer)
Achetez des abonnements IPTV pas chers sur www.tv-gratuite-ill → masquer   (choix pub, marge 0.90) ✓
Très bon accueil en boutique, merci à Julie pour sa patience.  → publier   (choix publier, marge 0.93) ✓
Je suis M. Bernard, 12 rue des Lilas à Nantes, appelez-moi au  → masquer   (choix coordonnees, marge 0.48) ✓
Ils m'ont facturé 300 € de frais cachés, c'est de l'escroqueri → verifier  (choix verifier, marge 0.84) ✓
Bof. Ça marche mais sans plus.                                 → publier   (choix publier, marge 0.96) ✓
Votre employé m'a insulté au téléphone et a raccroché.         → verifier  (choix verifier, marge 0.90) ✓
Les débits sont corrects la nuit, mais le soir c'est inutilisa → publier   (choix publier, marge 0.91) ✓
Installation faite en 1 h, technicien ponctuel et propre.      → publier   (choix publier, marge 0.94) ✓
Bande d'incapables, vous êtes des voleurs et des abrutis.      → masquer   (choix insulte, marge 0.96) ✓
Pour le même prix allez voir chez FibreMax, code promo FIBRE20 → masquer   (choix pub, marge 0.82) ✓

ecriture : 9/10 avis bien traités ; verification : 3/3 avis bien traités

[mlx, 4 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `ecriture : 9/10 avis bien traités ; verification : 3/3 avis bien traités` (identique)

## Adapter chez vous
Votre charte de modération, une option par motif de refus ; les avis négatifs mais légitimes doivent rester publiés (obligation de loyauté).

## Ce qui se passe et pourquoi (résultats et pièges)
**Première version avec une seule option « masquer » fourre-tout : 7/10** (la pub et les coordonnées passaient). Une option par motif : 9/10, puis 3/3 sur les lignes écrites après coup ; l'insulte la moins nette (marge 0,29) part en modération humaine, le bon sens d'erreur. Ne masquez jamais un avis seulement parce qu'il est négatif.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
