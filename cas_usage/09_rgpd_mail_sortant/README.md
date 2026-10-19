<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 09 — Avant d'envoyer un mail à l'extérieur : données personnelles ?

*DPO / conformité · secteur : Tous · type de tâche : **Noul + règles** · ⚠️ limite : utile seulement avec les règles*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (13 lignes).*

**Problème.** Des listes de clients, IBAN ou informations de santé partent par mail chez des prestataires.

**Décision.** Deux questions oui / non (données personnelles identifiantes ? données sensibles : santé, sanction ?) **+ règles écrites** (IBAN, carte, téléphone, e-mail, n° de sécurité sociale). Action : bloquer et demander une relecture.

## Lancer
```sh
.venv/bin/python cas_usage/09_rgpd_mail_sortant/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 9 — Avant d'envoyer un mail à l'extérieur : contient-il des données personnelles ? (wyat + règles écrites)"""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

QUESTION = ("Ce mail contient-il des données personnelles sur une personne identifiable "
            "(coordonnées, numéro bancaire, santé, numéro de sécurité sociale, sanction) ?")
SENSIBLE = "Ce mail parle-t-il de la santé, d'une absence pour maladie, d'une sanction ou d'un licenciement d'une personne identifiable ?"
MOTIFS = {   # ce que le code sait trouver mieux qu'un modèle : des formats
    "IBAN": r"\bFR\d{2}(?: ?\d{4}){5}", "carte": r"\b(?:\d{4} ?){4}\b", "téléphone": r"\b0[1-9](?: ?\d{2}){4}\b", "e-mail": r"[\w.-]+@[\w-]+\.\w+",
    "sécu": r"\b[12] ?\d{2} ?\d{2} ?\d{2} ?\d{3} ?\d{3} ?\d{2}\b",
}

scores = {"ecriture": [0, 0, 0], "verification": [0, 0, 0]}   # wyat seul, wyat + règles, total
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    p = max(modele.decide(wyat.Request.noul(q, context=ligne["mail"])).probability_true for q in (QUESTION, SENSIBLE))
    formats = [nom for nom, motif in MOTIFS.items() if re.search(motif, ligne["mail"])]
    wyat_seul = "oui" if p >= 0.5 else "non"
    les_deux = "oui" if formats or p >= 0.5 else "non"
    s = scores[ligne["jeu"]]
    s[0] += wyat_seul == ligne["attendu"]
    s[1] += les_deux == ligne["attendu"]
    s[2] += 1
    print(f"{ligne['mail'][:58]:<58} P(oui) {p:.2f}  règles {formats or '-'}  → {'BLOQUER, à relire' if les_deux == 'oui' else 'envoyer'} (attendu {ligne['attendu']})")
print("\n" + " ; ".join(f"{jeu} : wyat seul {a}/{n}, wyat + règles {b}/{n}" for jeu, (a, b, n) in scores.items()))
```

## Sortie réelle (mlx)
```
Bonjour, voici le planning de l'intervention de jeudi, l'é P(oui) 0.04  règles -  → envoyer (attendu non)
Ci-joint la liste des clients en impayé : Martine Roux, 14 P(oui) 0.77  règles ['téléphone']  → BLOQUER, à relire (attendu oui)
Pour le remboursement, l'IBAN du client est FR76 3000 6000 P(oui) 0.95  règles ['IBAN', 'carte']  → BLOQUER, à relire (attendu oui)
Le rapport trimestriel est en ligne sur l'intranet.        P(oui) 0.12  règles -  → envoyer (attendu non)
Mme Lopez est en arrêt maladie pour une dépression, elle n P(oui) 0.96  règles -  → BLOQUER, à relire (attendu oui)
Le client a payé avec la carte 4970 1012 3456 7890, expira P(oui) 0.17  règles ['carte']  → BLOQUER, à relire (attendu oui)
Rappel : la réunion budget est décalée à 15 h, salle Garon P(oui) 0.07  règles -  → envoyer (attendu non)
Peux-tu vérifier le dossier de M. Diallo, né le 03/04/1981 P(oui) 0.97  règles ['sécu']  → BLOQUER, à relire (attendu oui)
Merci pour votre devis, nous revenons vers vous la semaine P(oui) 0.04  règles -  → envoyer (attendu non)
Le salarié en période d'essai a été licencié pour insuffis P(oui) 0.97  règles -  → BLOQUER, à relire (attendu oui)
Le collaborateur Karim B. sera absent 3 semaines pour une  P(oui) 0.14  règles -  → envoyer (attendu oui)
Voici les chiffres de ventes agrégés par région pour le tr P(oui) 0.04  règles -  → envoyer (attendu non)
Contact du client pour la livraison : Jeanne Morel, jeanne P(oui) 0.10  règles ['e-mail']  → BLOQUER, à relire (attendu oui)

ecriture : wyat seul 9/10, wyat + règles 10/10 ; verification : wyat seul 1/3, wyat + règles 2/3

[mlx, 5 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `ecriture : wyat seul 9/10, wyat + règles 10/10 ; verification : wyat seul 1/3, wyat + règles 2/3` (identique)

## Adapter chez vous
Les formats propres à votre activité (numéro client, n° de contrat) en règles ; branché dans la passerelle de messagerie ou un complément du client mail.

## Ce qui se passe et pourquoi (résultats et pièges)
Seul, wyat rate des numéros de carte (P = 0,17) et des informations de santé : **les règles font l'essentiel**. Une 2ᵉ question « données sensibles » a fait passer les lignes d'écriture de 7/10 à 9/10 (10/10 avec les règles)… et sur 3 lignes écrites ensuite, wyat seul n'en a eu qu'**1/3** (« absent 3 semaines pour une opération du genou » : 0,14). C'est exactement le sur-ajustement du bloc 5. À utiliser comme filet supplémentaire, jamais comme garantie RGPD.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
