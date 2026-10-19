<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Cas 01 — Trier les messages du support (boutique en ligne)

*Service client · secteur : Commerce · type de tâche : **Choice** · ✅ à montrer*
*Entreprise, personnes et données fictives ; `donnees.csv` est synthétique (12 lignes).*

**Problème.** Les messages arrivent dans une seule boîte ; quelqu'un les lit pour les ranger dans la bonne file.

**Décision.** « Quel service doit traiter ce message ? » → livraison / retour / paiement / compte / autre. Action : poser l'étiquette de file ; **marge < 0,5 → file « humain »**.

## Lancer
```sh
.venv/bin/python cas_usage/01_tri_support/cas.py
```

## Le code (`cas.py`)
```python
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 1 — Trier les messages du support de la boutique en ligne, avec repli humain (lot sur un CSV)."""
import csv
import os
import platform
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

OPTIONS = {
    "livraison": "Livraison : colis en retard, perdu, suivi bloqué, livré mais pas reçu",
    "retour": "Retour, échange ou remboursement d'un article déjà reçu",
    "paiement": "Paiement : carte refusée, double débit, prélèvement sans commande",
    "compte": "Compte client : connexion, mot de passe, adresse e-mail, données du compte",
    "autre": "Autre demande précise sans rapport avec une commande",
}
SEUIL = 0.5   # marge minimale pour router sans humain

justes, sortie = 0, []
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for ligne in _lignes:
    d = modele.decide(wyat.Request.choice("Quel service doit traiter ce message ?", OPTIONS, context=ligne["message"]))
    file = d.selected if d.probability_margin >= SEUIL else "humain"
    justes += d.selected == ligne["attendu"]
    sortie.append({"id": ligne["id"], "file": file, "choix": d.selected, "marge": round(d.probability_margin, 2)})
    print(f"{ligne['message'][:60]:<60} → {file:<9} (choix {d.selected}, marge {d.probability_margin:.2f}, attendu {ligne['attendu']})")

with open(ICI / "routage.csv", "w", newline="", encoding="utf-8") as f:   # à reprendre par votre outil de tickets
    w = csv.DictWriter(f, fieldnames=sortie[0])
    w.writeheader()
    w.writerows(sortie)
print(f"\n{justes}/{len(sortie)} choix justes ; {sum(s['file'] == 'humain' for s in sortie)} message(s) pour un humain → routage.csv")
```

## Sortie réelle (mlx)
```
Bonjour, ma commande n°48213 est arrivée cassée, je veux un  → humain    (choix retour, marge 0.13, attendu retour)
Je n'arrive plus à me connecter à mon compte, le mot de pass → compte    (choix compte, marge 0.99, attendu compte)
Vous m'avez débité deux fois 54,90 € pour la même commande   → paiement  (choix paiement, marge 0.89, attendu paiement)
Où en est mon colis ? Le suivi n'a pas bougé depuis 5 jours  → livraison (choix livraison, marge 0.99, attendu livraison)
Je voudrais renvoyer le pull, il est trop petit              → retour    (choix retour, marge 0.74, attendu retour)
Comment changer l'adresse e-mail de mon compte ?             → compte    (choix compte, marge 0.93, attendu compte)
Le livreur a laissé le colis devant la porte et il a disparu → livraison (choix livraison, marge 0.96, attendu livraison)
Ma carte est refusée au moment de payer alors qu'elle marche → paiement  (choix paiement, marge 0.95, attendu paiement)
Bonjour, est-ce que vous recrutez des vendeurs pour Noël ?   → autre     (choix autre, marge 1.00, attendu autre)
Remboursement toujours pas reçu, retour déposé il y a 3 sema → humain    (choix retour, marge 0.33, attendu retour)
j'ai été prélevé mais la commande n'apparaît pas dans mon co → humain    (choix paiement, marge 0.08, attendu paiement)
Le colis indique livré mais je n'ai rien                     → livraison (choix livraison, marge 0.84, attendu livraison)

12/12 choix justes ; 3 message(s) pour un humain → routage.csv

[mlx, 4 s chargement compris]
```

Contrôle sur l'autre moteur (torch) : `12/12 choix justes ; 3 message(s) pour un humain → routage.csv` (identique)

## Adapter chez vous
Vos files et leurs vrais mots (relisez 50 messages avant d'écrire les options) ; le seuil selon le coût d'un mauvais routage ; branchez `routage.csv` sur l'import de votre outil, ou utilisez `integrations/webhook_tickets.py` à la création du ticket.

## Ce qui se passe et pourquoi (résultats et pièges)
Une option « autre » trop large aspire tout (bloc 4) ; les messages à deux sujets ont une marge faible : c'est voulu, ils vont à un humain.

Repère de benchmark associé : — (voir [`docs/benchmarks.md`](../../docs/benchmarks.md) ; ces données ne reproduisent pas le benchmark).
