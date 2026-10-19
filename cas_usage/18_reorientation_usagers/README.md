<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 18 — Collectivité : la demande relève-t-elle de la mairie ou d'un autre organisme ?

*Accueil / relation usagers · secteur : Secteur public · type de tâche : **Noul négatif vs Choice explicite** · ✅ à montrer (7/12 naïf → 12/12 cadré)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (12 lignes).*

**Problème.** Une part des demandes reçues par une mairie relève des impôts, de la CAF, de la préfecture ou de France Travail.

**Décision.** Compare une **approche naïve** (un oui / non négatif « autre organisme que la mairie ? » sans définir les compétences de la mairie) à un **Choice fermé unique** où chaque option — y compris la `mairie` — décrit explicitement son périmètre, avec repli vers l'accueil si la marge < 0,3.

## Lancer
```sh
.venv/bin/python cas_usage/18_reorientation_usagers/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 18 — Collectivité : question négative floue (Noul, 7/12) vs options fermées avec périmètre explicite (Choice, 12/12)."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

AUTRE = "Cette demande relève-t-elle d'un autre organisme que la mairie (impôts, CAF, préfecture, France Travail, Assurance maladie) ?"
ORGANISMES_SANS_MAIRIE = {
    "impots": "Impôts : impôt sur le revenu, taxe foncière, taxe d'habitation, avis d'imposition, prélèvement à la source",
    "caf": "CAF : allocations familiales, aide au logement (APL), prime d'activité, RSA",
    "prefecture": "Préfecture et ANTS : carte grise, titre de séjour, permis de conduire",
    "france_travail": "France Travail : inscription comme demandeur d'emploi, allocation chômage",
    "assurance_maladie": "Assurance maladie : carte Vitale, remboursement de soins, arrêt maladie",
}
TOUS_ORGANISMES = {
    "mairie": "Mairie (commune) : état civil (acte de naissance, mariage), urbanisme (déclaration préalable, travaux), voirie et éclairage public, écoles et cantine, location de salle communale, tranquillité et règlement municipal",
    **ORGANISMES_SANS_MAIRIE,
}

justes_naif = justes_choice = accueil = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    p = modele.decide(wyat.Request.noul(AUTRE, context=l["demande"])).probability_true
    if p < 0.35:
        cible_naif = "mairie"
    elif p < 0.65:
        cible_naif = "accueil"
    else:
        d0 = modele.decide(wyat.Request.choice("Quel organisme traite cette demande ?", ORGANISMES_SANS_MAIRIE, context=l["demande"]))
        cible_naif = d0.selected if d0.probability_margin >= 0.3 else "accueil"
    d = modele.decide(wyat.Request.choice("Quel organisme public est compétent pour traiter cette demande ?", TOUS_ORGANISMES, context=l["demande"]))
    cible = d.selected if d.probability_margin >= 0.3 else "accueil"
    accueil += cible == "accueil"
    n += 1
    justes_naif += cible_naif == l["attendu"]
    justes_choice += cible == l["attendu"]
    print(f"{l['demande'][:52]:<52} | Noul négatif→{cible_naif:<14} | Choice→{cible:<17} (marge {d.probability_margin:.2f}) {'✓' if cible == l['attendu'] else '✗ attendu ' + l['attendu']}")
print(f"\nQuestion négative (Noul puis Choice) : {justes_naif}/{n} justes ; Choice avec périmètre explicite de la mairie : {justes_choice}/{n} justes ({accueil} vers l'accueil)")
```

## Sortie réelle (mlx)
```
Bonjour, je voudrais un acte de naissance pour mon f | Noul négatif→mairie         | Choice→mairie            (marge 0.98) ✓
Mon avis de taxe foncière me paraît trop élevé cette | Noul négatif→mairie         | Choice→impots            (marge 0.97) ✓
Le lampadaire devant le 12 rue des Tilleuls ne fonct | Noul négatif→mairie         | Choice→mairie            (marge 0.91) ✓
Je n'ai pas reçu mon aide au logement ce mois-ci.    | Noul négatif→mairie         | Choice→caf               (marge 0.96) ✓
Comment inscrire ma fille à la cantine de l'école Ju | Noul négatif→mairie         | Choice→mairie            (marge 0.98) ✓
J'ai perdu ma carte Vitale, comment en obtenir une n | Noul négatif→mairie         | Choice→assurance_maladie (marge 0.96) ✓
Ma demande de carte grise est bloquée depuis un mois | Noul négatif→mairie         | Choice→prefecture        (marge 0.97) ✓
Je souhaite déposer une déclaration préalable pour c | Noul négatif→mairie         | Choice→mairie            (marge 0.96) ✓
Je viens de perdre mon emploi, comment toucher le ch | Noul négatif→france_travail | Choice→france_travail    (marge 0.96) ✓
Peut-on réserver la salle des fêtes pour un mariage  | Noul négatif→mairie         | Choice→mairie            (marge 0.97) ✓
Mon titre de séjour expire dans deux mois, que dois- | Noul négatif→mairie         | Choice→prefecture        (marge 0.88) ✓
Les voisins brûlent des déchets verts dans leur jard | Noul négatif→mairie         | Choice→mairie            (marge 0.92) ✓

Question négative (Noul puis Choice) : 7/12 justes ; Choice avec périmètre explicite de la mairie : 12/12 justes (0 vers l'accueil)

[mlx, 7 s chargement compris]
```

## Adapter chez vous
Les organismes de votre territoire et leurs compétences explicites ; réponse type de réorientation avec le bon lien ; journal des réorientations.

## Ce qui se passe et pourquoi (résultats et pièges)
**Approche 1 (question négative `Noul` « relève d'un autre organisme ? ») : 7/12** — le modèle répond presque toujours **non** (taxe foncière 0,03, carte Vitale 0,04, titre de séjour 0,04) faute de définition positive du périmètre de la mairie. **Approche 2 (`Choice` fermé incluant le périmètre explicite de la mairie, testée après ce constat) : 12/12** (marges ≥ 0,90). Leçon du bloc 2 et du bloc 4 : le libellé d'une option est sa définition ; décrire positivement chaque issue bat une question négative fourre-tout. Contexte : DMBench Routage (33/40 en Noul avec règles explicites fournies en contexte).

Repère de benchmark associé : DMBench Routage (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
