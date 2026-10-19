# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 24 — Protection de la marque : contexte naïf avec prix mélangé (3/8) vs wyat sur le texte seul (6/8) + règles prix/mots."""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

PRODUIT_NAIF = "Sac « Méridienne » en cuir de veau grainé, fabriqué en France, prix boutique 2 400 €"
RELATION_NAIVE = {
    "exact": "L'annonce propose ce produit précis",
    "substitut": "L'annonce propose un produit différent qui pourrait le remplacer (autre modèle, autre marque)",
    "complement": "L'annonce propose un accessoire ou un produit qui va avec (housse, bandoulière, produit d'entretien)",
    "hors_sujet": "L'annonce n'a rien à voir avec ce produit",
}
PRODUIT_TEXTE = "Sac Méridienne en cuir de veau grainé"
RELATION_TEXTE = {
    "exact": "Le produit proposé est exactement le sac Méridienne lui-même.",
    "substitut": "Un autre sac pouvant remplacer le produit cherché (autre modèle, autre marque ou cabas inspiré).",
    "complement": "Un accessoire ou produit d'entretien utilisé avec le sac Méridienne ; ne remplace pas le sac.",
    "hors_sujet": "Un article sans aucun rapport avec un sac à main.",
}
MOTS = re.compile(r"réplique|replica|qualité miroir|mirror quality|inspiré|style|1:1|sans boîte ni facture|AAA", re.I)
PRIX_MINI = 0.4 * 2400   # en dessous, « exact » est suspect : c'est le code qui compare les prix, pas le modèle

justes_naif = justes_wyat = n = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    d_naif = modele.decide(wyat.Request.choice("Quel est le lien entre l'annonce et le produit de référence ?", RELATION_NAIVE,
                                               context={"produit_de_reference": PRODUIT_NAIF, "annonce": l["annonce"], "prix": l["prix"]}))
    d = modele.decide(wyat.Request.choice("Comment cet article se rapporte-t-il au produit recherché ?", RELATION_TEXTE,
                                          context={"search": PRODUIT_TEXTE, "product": l["annonce"]}))
    signaux = (["mots"] if MOTS.search(l["annonce"]) else []) + (["prix"] if d.selected == "exact" and float(l["prix"]) < PRIX_MINI else [])
    action = "à vérifier (marque)" if signaux or (d.selected == "exact" and d.probability_margin < 0.5) else "-"
    n += 1
    justes_naif += d_naif.selected == l["attendu"]
    justes_wyat += d.selected == l["attendu"]
    print(f"{l['annonce'][:46]:<46} {l['prix']:>5} € | naïf→{d_naif.selected:<10} | texte→{d.selected:<10} {str(signaux or '-'):<16} {action} {'✓' if d.selected == l['attendu'] else '✗ att ' + l['attendu']}")
print(f"\nContexte naïf (prix dans le prompt) : {justes_naif}/{n} relations justes ; texte seul (wyat) + prix/mots en code : {justes_wyat}/{n} relations justes")
