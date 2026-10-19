<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 13 — Hameçonnage : premier tri des e-mails signalés

*Sécurité (tous secteurs) · secteur : Tous · type de tâche : **Noul + règles** · ✅ à montrer (premier filtre)*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (12 lignes).*

**Problème.** Les collaborateurs signalent des e-mails douteux ; l'équipe sécurité les relit un par un.

**Décision.** P(hameçonnage) avec deux seuils : < 0,25 classer, ≥ 0,75 quarantaine, entre les deux **analyste** ; règles écrites (domaine qui imite un domaine officiel, lien raccourci) qui mettent en quarantaine quoi que dise le modèle.

## Lancer
```sh
.venv/bin/python cas_usage/13_hameconnage_mails/cas.py
```

## Le code (`cas.py`)
```python
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
```

## Sortie réelle (mlx)
```
Votre mot de passe expire aujourd'hui        P 0.93 règles - → quarantaine ✓
Maintenance VPN samedi                       P 0.04 règles - → classer     ✓
Nouvelles coordonnées bancaires              P 0.97 règles - → quarantaine ✓
Document à signer : avenant contrat          P 0.08 règles - → classer     ✓
Erreur sur votre bulletin de paie            P 0.85 règles ['domaine imité'] → quarantaine ✓
Votre avis d'impôt est disponible            P 0.08 règles - → classer     ✓
Demande confidentielle                       P 0.93 règles - → quarantaine ✓
Votre ticket 48213 est résolu                P 0.02 règles - → classer     ✓
Colis en attente                             P 0.13 règles ['lien raccourci'] → quarantaine ✓
Fichier partagé avec vous                    P 0.08 règles - → classer     ✗ attendu hameconnage
Relance facture F-2291                       P 0.03 règles - → classer     ✓
Remboursement effectué                       P 0.05 règles - → classer     ✓

ecriture 8/8 ; verification 3/4 ; 0 e-mail(s) en zone grise pour l'analyste

[mlx, 4 s chargement compris]
```

## Adapter chez vous
Votre liste de domaines officiels (`OFFICIELS`) et vos fournisseurs ; les deux seuils réglés sur 100 signalements réels ; branché sur la boîte « signalement » (IMAP) ou le bouton de signalement du client mail.

## Ce qui se passe et pourquoi (résultats et pièges)
Première version, non retouchée. Manqué : le faux partage SharePoint (P = 0,08), dont le domaine imite un service absent de la liste `OFFICIELS` : la règle ne sait que ce qu'on lui donne. Aucun e-mail n'est tombé en zone grise : sur ces données, le modèle est soit très sûr, soit très peu sûr, ce qui ne garantit rien sur les vôtres. Contexte : sur PhishNChips, wyat-1-800m fait 57,45 % pour une chance de 50 % (voir `docs/benchmarks.md`) : c'est un **premier filtre**, pas un détecteur.

Repère de benchmark associé : PhishNChips (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
