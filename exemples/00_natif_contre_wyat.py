# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Étape 1 — La version native (mots-clés) face à wyat, sur les mêmes messages de dev.

Les mots-clés sont tirés des définitions des options (atelier/options.py), pas ajustés sur dev :
c'est la règle qu'on écrirait en 10 minutes (minuscules, accents retirés). Usage : python exemples/00_natif_contre_wyat.py
"""
import unicodedata

import atelier as at

MOTS_CLES = {   # premier service dont un mot apparaît ; sinon « autre »
    "facturation": ["factur", "prelev", "debit", "rembours", "paiement", "paye", "montant", "€"],
    "technique": ["internet", "wifi", "box", "tv", "reseau", "sim", "appli", "marche pas", "fonctionne"],
    "resiliation": ["resili", "mettre fin", "arreter"],
    "livraison": ["colis", "livr", "commande", "suivi", "renvoy", "retour"],
}


def sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte.lower()) if unicodedata.category(c) != "Mn")


def natif(message: str) -> str:
    texte = sans_accents(message)
    for service, mots in MOTS_CLES.items():
        if any(m in texte for m in mots):
            return service
    return "autre"


dev = at.lire("dev.csv")
modele = at.charger_modele()
rapport, res = at.evaluer(modele, dev, at.OPTIONS)
res["natif"] = dev.message.map(natif).values
n = len(res)
justes_natif, justes_wyat = int((res.natif == res.label).sum()), int(res.correct.sum())
print(f"\nNatif (mots-clés) : {justes_natif}/{n} justes   |   wyat : {justes_wyat}/{n} justes")
print("Le natif ne dit jamais « je ne sais pas » ; wyat donne une marge (étape 5 : sous le seuil → humain).\n")
desaccords = res[res.natif != res.prediction]
print(f"{len(desaccords)} messages où les deux ne sont pas d'accord (10 premiers) :")
for r in desaccords.head(10).itertuples():
    print(f"  « {r.message[:58]:<58} » natif={r.natif:<11} wyat={r.prediction:<11} (marge {r.marge:.2f}) attendu={r.label}")
