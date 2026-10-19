<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 06 — Qualifier les demandes de contact commerciales

*Ventes · secteur : Commerce · type de tâche : **Choice** · ⚠️ faible : 7/11 au total*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (11 lignes).*

**Problème.** Le formulaire « professionnels » mélange vrais projets, curieux, étudiants et démarcheurs.

**Décision.** « Quelle suite donner ? » → appeler (rappel sous 24 h) / informer (documentation, relance à 1 mois) / écarter. Action : créer la tâche dans le CRM.

## Lancer
```sh
.venv/bin/python cas_usage/06_qualification_leads/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 6 — Qualifier les demandes entrantes du formulaire « professionnels » : qui rappeler vite ?"""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {
    "appeler": "Une entreprise qui veut acheter nos offres : besoin précis, taille ou délai donnés, ou demande de rappel",
    "informer": "Une personne ou une entreprise intéressée par nos offres, sans projet daté : lui envoyer de la documentation",
    "ecarter": "Pas un futur client : étudiant, curieux sans projet, ou quelqu'un qui veut NOUS vendre un service (démarchage, SEO, publicité)",
}
ACTIONS = {"appeler": "→ commercial, rappel sous 24 h", "informer": "→ e-mail de présentation + relance à 1 mois", "ecarter": "→ archivé"}

scores = {"ecriture": [0, 0], "verification": [0, 0]}
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.choice("Quelle suite donner à cette demande de contact ?", OPTIONS, context=ligne["demande"]))
    scores[ligne["jeu"]][0] += d.selected == ligne["attendu"]
    scores[ligne["jeu"]][1] += 1
    signe = "✓" if d.selected == ligne["attendu"] else f"✗ (attendu {ligne['attendu']})"
    print(f"{ligne['demande'][:58]:<58} {d.selected:<8} {ACTIONS[d.selected]:<38} marge {d.probability_margin:.2f} {signe}")
print("\n" + " ; ".join(f"{jeu} : {j}/{n} demandes bien qualifiées" for jeu, (j, n) in scores.items()))
```

## Sortie réelle (mlx)
```
Bonjour, nous sommes 45 salariés sur 3 sites et cherchons  appeler  → commercial, rappel sous 24 h         marge 0.76 ✓
Je voudrais juste connaître vos tarifs, par curiosité.     ecarter  → archivé                              marge 0.82 ✗ (attendu informer)
Directrice des achats d'un réseau de 12 agences : nous lan appeler  → commercial, rappel sous 24 h         marge 0.97 ✓
Je suis étudiant et je fais un exposé sur les opérateurs t ecarter  → archivé                              marge 0.48 ✓
Notre cabinet (8 personnes) a des coupures fréquentes avec informer → e-mail de présentation + relance à 1 mois marge 0.63 ✓
Proposition de partenariat SEO : nous pouvons faire passer informer → e-mail de présentation + relance à 1 mois marge 0.25 ✗ (attendu ecarter)
Gérant d'un restaurant, je veux une offre internet + télép appeler  → commercial, rappel sous 24 h         marge 0.66 ✓
Je m'abonnerai peut-être un jour. Envoyez-moi votre newsle informer → e-mail de présentation + relance à 1 mois marge 0.95 ✓
Nous ouvrons une deuxième boutique en mars et il nous faut informer → e-mail de présentation + relance à 1 mois marge 0.16 ✗ (attendu appeler)
Bonjour, je suis commercial chez un éditeur de logiciels d informer → e-mail de présentation + relance à 1 mois marge 0.95 ✗ (attendu ecarter)
Notre association compare les opérateurs pour l'an prochai informer → e-mail de présentation + relance à 1 mois marge 0.97 ✓

ecriture : 6/8 demandes bien qualifiées ; verification : 1/3 demandes bien qualifiées

[mlx, 4 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `ecriture : 6/8 demandes bien qualifiées ; verification : 1/3 demandes bien qualifiées` (identique)

## Adapter chez vous
Vos critères de projet (taille, délai, budget) dans l'option « appeler » ; `integrations/pandas_tri.py` sur l'export du CRM.

## Ce qui se passe et pourquoi (résultats et pièges)
Les démarcheurs qui parlent de « partenariat » ressemblent à des prospects. « Par curiosité » : informer ou écarter ? Même les humains hésitent : décidez la règle. Les options ont été réécrites une fois (6/8 dans les deux versions) et les 3 lignes « vérification » écrites ensuite : 1/3. Pas prêt : il faudrait 100 vrais exemples et sans doute un critère chiffré (taille, délai) extrait par le code.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
