# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 13 — Hameçonnage : premier tri des e-mails signalés par les collaborateurs (wyat + règles ; zone grise → analyste)."""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

QUESTION = ("Cet e-mail est-il une tentative d'hameçonnage ou de fraude : faux lien de connexion, urgence artificielle, "
            "demande d'identifiants, de paiement, de coordonnées bancaires ou de pièce jointe à ouvrir ?")
OFFICIELS = {"groupe-exemple.fr", "microsoft.com", "dgfip.finances.gouv.fr", "docusign.net", "ameli.fr"}   # votre liste
RACCOURCISSEURS = re.compile(r"bit\.ly|tinyurl|is\.gd|t\.ly", re.I)
BAS, HAUT = 0.25, 0.75   # < BAS : classer ; ≥ HAUT : quarantaine ; entre les deux : analyste

def regles(expediteur: str, corps: str) -> list[str]:
    domaine = expediteur.rsplit("@", 1)[-1].lower()
    officiel = any(domaine == o or domaine.endswith("." + o) for o in OFFICIELS)
    imite = not officiel and any(o.split(".")[0] in domaine for o in OFFICIELS)
    return [nom for nom, ok in (("domaine imité", imite), ("lien raccourci", bool(RACCOURCISSEURS.search(corps)))) if ok]

bilan = {"ecriture": [0, 0], "verification": [0, 0]}
analyste = 0
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    p = modele.decide(wyat.Request.noul(QUESTION, context=f"Expéditeur : {l['expediteur']}\nObjet : {l['objet']}\n\n{l['corps']}")).probability_true
    r = regles(l["expediteur"], l["corps"])
    action = "quarantaine" if r or p >= HAUT else ("analyste" if p >= BAS else "classer")
    analyste += action == "analyste"
    bon = (action != "classer") == (l["attendu"] == "hameconnage")   # l'analyste compte comme « arrêté »
    bilan[l["jeu"]][0] += bon
    bilan[l["jeu"]][1] += 1
    print(f"{l['objet'][:44]:<44} P {p:.2f} règles {r or '-'} → {action:<11} {'✓' if bon else '✗ attendu ' + l['attendu']}")
print("\n" + " ; ".join(f"{j} {a}/{n}" for j, (a, n) in bilan.items()) + f" ; {analyste} e-mail(s) en zone grise pour l'analyste")
