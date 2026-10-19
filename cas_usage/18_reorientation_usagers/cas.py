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
